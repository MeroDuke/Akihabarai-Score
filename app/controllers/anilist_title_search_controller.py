"""AniList title-search UI controller.

This module owns the runtime-only AniList title search state used by the
main window: debounce, online/offline search routing, selection re-query
handling, autocomplete popup decisions, and async online request isolation.
"""

from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import QObject, QThread, QTimer, QStringListModel, pyqtSignal
from PyQt6.QtWidgets import QCompleter

from app.core.models import AnimeSearchResult
from app.logger import log_debug, log_warning
from app.services.anilist_service import (
    search_anime,
    search_anime_online_response,
    search_anime_titles,
)


class _AniListTitleSearchWorker(QObject):
    """Run one AniList online title search outside the UI thread."""

    finished = pyqtSignal(str, object)

    def __init__(self, query: str):
        super().__init__()
        self.query = query

    def run(self):
        response = search_anime_online_response(self.query)
        self.finished.emit(self.query, response)


class AniListTitleSearchController:
    """Coordinate title autocomplete searches for offline and online modes."""

    def __init__(
        self,
        *,
        parent,
        completer_model: QStringListModel,
        completer: QCompleter,
        debounce_ms: int,
        is_online_mode: Callable[[], bool],
        is_integration_enabled: Callable[[], bool],
        on_connection_error: Callable[[str, str], None] | None = None,
    ):
        self.completer_model = completer_model
        self.completer = completer
        self.is_online_mode = is_online_mode
        self.is_integration_enabled = is_integration_enabled
        self.on_connection_error = on_connection_error

        self.pending_title_search_query = ""
        self.last_manual_online_query = ""
        self.last_online_requery_title = ""

        self._active_search_thread: QThread | None = None
        self._active_search_worker: _AniListTitleSearchWorker | None = None
        self._active_search_query = ""
        self._queued_search_query: str | None = None

        self.title_search_timer = QTimer(parent)
        self.title_search_timer.setSingleShot(True)
        self.title_search_timer.setInterval(debounce_ms)
        self.title_search_timer.timeout.connect(self.run_debounced_title_search)

        log_debug(
            "anilist",
            f"title_search_controller_initialized: debounce_ms={debounce_ms}",
        )

    def reset_online_state(self):
        self.pending_title_search_query = ""
        self.last_manual_online_query = ""
        self.last_online_requery_title = ""
        self._active_search_query = ""
        self._queued_search_query = None
        self.title_search_timer.stop()
        log_debug("anilist", "title_search_state_reset")

    def refresh_title_autocomplete_results(self, query: str = "") -> bool:
        mode = "online" if self.is_online_mode() else "offline"

        if self.is_online_mode():
            normalized_query = query.strip()
            if not normalized_query:
                self.completer_model.setStringList([])
                log_debug(
                    "anilist",
                    "title_autocomplete_results_refreshed: "
                    "mode='online' query='' count=0 titles=[]",
                )
                return True

            self._start_online_title_search(normalized_query)
            return True

        titles = search_anime_titles(query)
        self.completer_model.setStringList(titles)
        log_debug(
            "anilist",
            f"title_autocomplete_results_refreshed: mode='{mode}' "
            f"query='{query.strip()}' count={len(titles)} titles={titles}",
        )
        return True

    def handle_title_text_edited(self, text: str):
        if not self.is_integration_enabled():
            log_debug(
                "anilist",
                "title_text_edit_ignored: reason='integration_disabled'",
            )
            return

        if not self.is_online_mode():
            log_debug(
                "anilist",
                "title_text_edit_ignored: reason='offline_mode'",
            )
            return

        self.last_manual_online_query = text.strip()
        self.last_online_requery_title = ""
        log_debug(
            "anilist",
            f"online_title_text_edited: query='{self.last_manual_online_query}'",
        )
        self.schedule_online_title_search(text)

    def schedule_online_title_search(self, query: str):
        normalized_query = query.strip()
        self.pending_title_search_query = normalized_query

        if not normalized_query:
            self.title_search_timer.stop()
            self.completer_model.setStringList([])
            self._queued_search_query = None
            log_debug(
                "anilist",
                "online_title_search_cleared: reason='empty_query'",
            )
            return

        self.title_search_timer.start()
        log_debug(
            "anilist",
            f"online_title_search_scheduled: query='{normalized_query}' "
            f"debounce_ms={self.title_search_timer.interval()}",
        )

    def run_debounced_title_search(self):
        if not self.is_integration_enabled():
            log_debug(
                "anilist",
                "debounced_title_search_skipped: reason='integration_disabled'",
            )
            return

        if not self.is_online_mode():
            log_debug(
                "anilist",
                "debounced_title_search_skipped: reason='offline_mode'",
            )
            return

        log_debug(
            "anilist",
            f"debounced_title_search_started: query='{self.pending_title_search_query}'",
        )

        if not self.pending_title_search_query:
            self.completer_model.setStringList([])
            log_debug(
                "anilist",
                "debounced_title_search_skipped: reason='empty_query'",
            )
            return

        self._start_online_title_search(self.pending_title_search_query)

    def handle_title_selected(self, title: str):
        if self.is_online_mode():
            self._schedule_requery_after_online_selection(title)
        else:
            log_debug(
                "anilist",
                f"title_selected_no_requery: reason='offline_mode' title='{title}'",
            )

    def find_anime_result_by_title(self, title: str) -> AnimeSearchResult | None:
        normalized_title = title.strip().casefold()
        if not normalized_title:
            log_debug("anilist", "find_anime_result_skipped: reason='empty_title'")
            return None

        mode = "online" if self.is_online_mode() else "offline"
        if self.is_online_mode():
            response = search_anime_online_response(title)
            if not response.ok:
                self._handle_connection_error(
                    response.error or "unknown_error",
                    response.error_detail or "",
                )
                return None
            results = response.results
        else:
            results = search_anime(title)

        for result in results:
            if result.title_romaji.casefold() == normalized_title:
                log_debug(
                    "anilist",
                    f"find_anime_result_matched: mode='{mode}' "
                    f"title='{title}' anilist_id={result.anilist_id}",
                )
                return result

        log_debug(
            "anilist",
            f"find_anime_result_not_found: mode='{mode}' title='{title}'",
        )
        return None

    def _start_online_title_search(self, query: str):
        normalized_query = query.strip()
        if not normalized_query:
            self.completer_model.setStringList([])
            return

        if self._is_online_search_running():
            self._queued_search_query = normalized_query
            log_debug(
                "anilist",
                f"online_title_search_queued: query='{normalized_query}' "
                f"active_query='{self._active_search_query}'",
            )
            return

        self._active_search_query = normalized_query
        self._active_search_thread = QThread()
        self._active_search_worker = _AniListTitleSearchWorker(normalized_query)
        self._active_search_worker.moveToThread(self._active_search_thread)

        self._active_search_thread.started.connect(self._active_search_worker.run)
        self._active_search_worker.finished.connect(self._handle_online_search_finished)
        self._active_search_worker.finished.connect(self._active_search_thread.quit)
        self._active_search_worker.finished.connect(self._active_search_worker.deleteLater)
        self._active_search_thread.finished.connect(self._active_search_thread.deleteLater)
        self._active_search_thread.finished.connect(self._handle_online_search_thread_finished)

        log_debug(
            "anilist",
            f"online_title_search_worker_started: query='{normalized_query}'",
        )
        self._active_search_thread.start()

    def _handle_online_search_finished(self, query: str, response):
        if not self.is_integration_enabled() or not self.is_online_mode():
            log_debug(
                "anilist",
                f"online_title_search_result_ignored: reason='inactive_mode' query='{query}'",
            )
            return

        if query.strip().casefold() != self._active_search_query.strip().casefold():
            log_debug(
                "anilist",
                f"online_title_search_result_ignored: reason='stale_query' "
                f"query='{query}' active_query='{self._active_search_query}'",
            )
            return

        self._apply_online_search_response(query, response)

    def _handle_online_search_thread_finished(self):
        finished_query = self._active_search_query
        self._active_search_thread = None
        self._active_search_worker = None
        self._active_search_query = ""

        queued_query = self._queued_search_query
        self._queued_search_query = None

        log_debug(
            "anilist",
            f"online_title_search_worker_finished: query='{finished_query}'",
        )

        if (
            queued_query
            and self.is_integration_enabled()
            and self.is_online_mode()
            and queued_query == self.pending_title_search_query
        ):
            log_debug(
                "anilist",
                f"online_title_search_worker_starting_queued: query='{queued_query}'",
            )
            self._start_online_title_search(queued_query)

    def _apply_online_search_response(self, query: str, response):
        if not response.ok:
            self._handle_connection_error(
                response.error or "unknown_error",
                response.error_detail or "",
            )
            return

        titles = [result.title_romaji for result in response.results]
        self.completer_model.setStringList(titles)
        log_debug(
            "anilist",
            f"title_autocomplete_results_refreshed: mode='online' "
            f"query='{query.strip()}' count={len(titles)} titles={titles}",
        )

        result_count = self.completer_model.rowCount()
        if self._is_single_exact_match(result_count, query):
            log_debug(
                "anilist",
                f"autocomplete_popup_suppressed: reason='single_exact_match' "
                f"query='{query}'",
            )
            return

        if result_count > 0:
            self.completer.complete()
            log_debug(
                "anilist",
                f"autocomplete_popup_opened: query='{query}' count={result_count}",
            )
        else:
            log_debug(
                "anilist",
                f"autocomplete_popup_not_opened: reason='no_results' query='{query}'",
            )

    def _handle_connection_error(self, reason: str, detail: str):
        self.title_search_timer.stop()
        self.completer_model.setStringList([])
        self._queued_search_query = None
        log_warning(
            "anilist",
            f"online_title_search_failed: reason='{reason}' detail='{detail}'",
        )

        if self.on_connection_error is not None:
            self.on_connection_error(reason, detail)

    def _is_online_search_running(self) -> bool:
        return (
            self._active_search_thread is not None
            and self._active_search_thread.isRunning()
        )

    def _schedule_requery_after_online_selection(self, title: str):
        normalized_title = title.strip()
        normalized_manual_query = self.last_manual_online_query.strip()

        if not normalized_title:
            log_debug(
                "anilist",
                "online_selection_requery_skipped: reason='empty_title'",
            )
            return

        if not normalized_manual_query:
            log_debug(
                "anilist",
                f"online_selection_requery_skipped: reason='missing_manual_query' "
                f"title='{normalized_title}'",
            )
            return

        if normalized_title.casefold() == normalized_manual_query.casefold():
            log_debug(
                "anilist",
                f"online_selection_requery_skipped: reason='same_as_manual_query' "
                f"title='{normalized_title}'",
            )
            return

        if normalized_title.casefold() == self.last_online_requery_title.casefold():
            log_debug(
                "anilist",
                f"online_selection_requery_skipped: reason='already_requeried' "
                f"title='{normalized_title}'",
            )
            return

        self.last_online_requery_title = normalized_title
        log_debug(
            "anilist",
            f"online_selection_requery_scheduled: from_query='{normalized_manual_query}' "
            f"title='{normalized_title}'",
        )
        self.schedule_online_title_search(normalized_title)

    def _is_single_exact_match(self, result_count: int, query: str | None = None) -> bool:
        if result_count != 1:
            return False

        only_title = self.completer_model.data(self.completer_model.index(0, 0))
        if not isinstance(only_title, str):
            return False

        expected_query = self.pending_title_search_query if query is None else query
        return only_title.strip().casefold() == expected_query.strip().casefold()
