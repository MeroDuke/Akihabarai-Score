"""AniList title-search UI controller.

This module owns the runtime-only AniList title search state used by the
main window: debounce, online/offline search routing, selection re-query
handling, and autocomplete popup decisions.
"""

from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import QTimer
from PyQt6.QtCore import QStringListModel
from PyQt6.QtWidgets import QCompleter

from app.core.models import AnimeSearchResult
from app.logger import log_debug
from app.services.anilist_service import (
    search_anime,
    search_anime_online,
    search_anime_titles,
    search_anime_titles_online,
)


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
    ):
        self.completer_model = completer_model
        self.completer = completer
        self.is_online_mode = is_online_mode
        self.is_integration_enabled = is_integration_enabled

        self.pending_title_search_query = ""
        self.last_manual_online_query = ""
        self.last_online_requery_title = ""

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
        self.title_search_timer.stop()
        log_debug("anilist", "title_search_state_reset")

    def refresh_title_autocomplete_results(self, query: str = ""):
        mode = "online" if self.is_online_mode() else "offline"
        titles = (
            search_anime_titles_online(query)
            if self.is_online_mode()
            else search_anime_titles(query)
        )
        self.completer_model.setStringList(titles)
        log_debug(
            "anilist",
            f"title_autocomplete_results_refreshed: mode='{mode}' "
            f"query='{query.strip()}' count={len(titles)} titles={titles}",
        )

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
        self.refresh_title_autocomplete_results(self.pending_title_search_query)

        result_count = self.completer_model.rowCount()
        if self._is_single_exact_match(result_count):
            log_debug(
                "anilist",
                f"autocomplete_popup_suppressed: reason='single_exact_match' "
                f"query='{self.pending_title_search_query}'",
            )
            return

        if result_count > 0:
            self.completer.complete()
            log_debug(
                "anilist",
                f"autocomplete_popup_opened: query='{self.pending_title_search_query}' "
                f"count={result_count}",
            )
        else:
            log_debug(
                "anilist",
                f"autocomplete_popup_not_opened: reason='no_results' "
                f"query='{self.pending_title_search_query}'",
            )

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
        results = search_anime_online(title) if self.is_online_mode() else search_anime(title)

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

    def _is_single_exact_match(self, result_count: int) -> bool:
        if result_count != 1:
            return False

        only_title = self.completer_model.data(self.completer_model.index(0, 0))
        if not isinstance(only_title, str):
            return False

        return (
            only_title.strip().casefold()
            == self.pending_title_search_query.strip().casefold()
        )
