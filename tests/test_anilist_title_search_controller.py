from types import SimpleNamespace

import pytest
from PyQt6.QtCore import QObject, QStringListModel

import app.controllers.anilist_title_search_controller as controller_module
from app.controllers.anilist_title_search_controller import AniListTitleSearchController
from app.core.models import AnimeSearchResult


class DummyCompleter:
    def __init__(self):
        self.complete_count = 0
        self.popup_widget = DummyPopup()

    def complete(self):
        self.complete_count += 1
        self.popup_widget.visible = True

    def popup(self):
        return self.popup_widget


class DummyPopup:
    def __init__(self):
        self.visible = False
        self.hide_count = 0

    def hide(self):
        self.visible = False
        self.hide_count += 1


@pytest.fixture
def log_messages(monkeypatch):
    messages = []
    monkeypatch.setattr(
        controller_module,
        "log_debug",
        lambda component, message: messages.append((component, message)),
    )
    monkeypatch.setattr(
        controller_module,
        "log_warning",
        lambda component, message: messages.append((component, message)),
    )
    return messages


@pytest.fixture
def parent(qtbot):
    obj = QObject()
    return obj


def _make_response(results=None, error=None, error_detail=None):
    results = [] if results is None else results
    return SimpleNamespace(
        results=results,
        error=error,
        error_detail=error_detail,
        ok=error is None,
    )


def _make_controller(
    parent,
    *,
    online=True,
    enabled=True,
    debounce_ms=1000,
    on_connection_error=None,
):
    model = QStringListModel([])
    completer = DummyCompleter()

    controller = AniListTitleSearchController(
        parent=parent,
        completer_model=model,
        completer=completer,
        debounce_ms=debounce_ms,
        is_online_mode=lambda: online,
        is_integration_enabled=lambda: enabled,
        on_connection_error=on_connection_error,
    )

    return controller, model, completer


def test_schedule_online_title_search_starts_timer_for_non_empty_query(parent, log_messages):
    controller, model, _ = _make_controller(parent)

    controller.schedule_online_title_search(" 86 ")

    assert controller.pending_title_search_query == "86"
    assert controller.title_search_timer.isActive() is True
    assert any("online_title_search_scheduled" in message for _, message in log_messages)


def test_schedule_online_title_search_clears_results_for_empty_query(parent, log_messages):
    controller, model, _ = _make_controller(parent)
    model.setStringList(["Existing"])

    controller.schedule_online_title_search("   ")

    assert controller.pending_title_search_query == ""
    assert controller.title_search_timer.isActive() is False
    assert model.rowCount() == 0
    assert any("online_title_search_cleared" in message for _, message in log_messages)


def test_handle_title_text_edited_ignores_offline_mode(parent, log_messages):
    controller, _, _ = _make_controller(parent, online=False)

    controller.handle_title_text_edited("Re:")

    assert controller.pending_title_search_query == ""
    assert controller.title_search_timer.isActive() is False
    assert any("offline_mode" in message for _, message in log_messages)


def test_run_debounced_title_search_starts_async_worker(parent, log_messages):
    controller, model, completer = _make_controller(parent)
    controller.pending_title_search_query = "Result"
    started_queries = []
    controller._start_online_title_search = lambda query: started_queries.append(query)

    controller.run_debounced_title_search()

    assert started_queries == ["Result"]
    assert model.stringList() == []
    assert completer.complete_count == 0
    assert any("debounced_title_search_started" in message for _, message in log_messages)


def test_apply_online_search_response_refreshes_model_and_opens_popup_for_multiple_results(
    parent, log_messages
):
    results = [
        AnimeSearchResult(1, "Result A", None, None, None, None),
        AnimeSearchResult(2, "Result B", None, None, None, None),
    ]
    controller, model, completer = _make_controller(parent)

    controller._apply_online_search_response(
        "Result",
        _make_response(results=results),
    )

    assert model.stringList() == ["Result A", "Result B"]
    assert completer.complete_count == 1
    assert any("autocomplete_popup_opened" in message for _, message in log_messages)


def test_apply_online_search_response_suppresses_popup_for_single_exact_match(
    parent, log_messages
):
    results = [AnimeSearchResult(116589, "86 Eighty-Six", None, None, None, 2021)]
    controller, model, completer = _make_controller(parent)

    controller._apply_online_search_response(
        "86 Eighty-Six",
        _make_response(results=results),
    )

    assert model.stringList() == ["86 Eighty-Six"]
    assert completer.complete_count == 0
    assert any("single_exact_match" in message for _, message in log_messages)


def test_empty_online_results_close_popup_left_open_by_previous_search(
    parent, log_messages
):
    controller, model, completer = _make_controller(parent)
    completer.complete()
    assert completer.popup_widget.visible is True

    controller._apply_online_search_response(
        "a",
        _make_response(results=[]),
    )

    assert model.stringList() == []
    assert completer.complete_count == 1
    assert completer.popup_widget.visible is False
    assert completer.popup_widget.hide_count == 1
    assert any("reason='no_results'" in message for _, message in log_messages)


def test_apply_online_search_response_reports_connection_error(
    parent, log_messages
):
    connection_errors = []
    controller, model, completer = _make_controller(
        parent,
        on_connection_error=lambda reason, detail: connection_errors.append((reason, detail)),
    )
    model.setStringList(["Existing"])
    controller.title_search_timer.start()

    controller._apply_online_search_response(
        "Re:Zero",
        _make_response(
            error="api_request_timeout",
            error_detail="simulated timeout",
        ),
    )

    assert model.stringList() == []
    assert controller.title_search_timer.isActive() is False
    assert completer.complete_count == 0
    assert connection_errors == [("api_request_timeout", "simulated timeout")]
    assert any("online_title_search_failed" in message for _, message in log_messages)
    assert any("api_request_timeout" in message for _, message in log_messages)


def test_handle_online_search_finished_ignores_stale_query(parent, log_messages):
    results = [AnimeSearchResult(1, "Old Result", None, None, None, None)]
    controller, model, completer = _make_controller(parent)
    controller._active_search_query = "new"

    controller._handle_online_search_finished(
        "old",
        _make_response(results=results),
    )

    assert model.stringList() == []
    assert completer.complete_count == 0
    assert any("stale_query" in message for _, message in log_messages)


def test_handle_title_selected_schedules_requery_only_once(parent, log_messages):
    controller, _, _ = _make_controller(parent)
    calls = []
    controller.last_manual_online_query = "Re:"
    controller.schedule_online_title_search = lambda query: calls.append(query)

    controller.handle_title_selected("Re:Zero kara Hajimeru Isekai Seikatsu")
    controller.handle_title_selected("Re:Zero kara Hajimeru Isekai Seikatsu")

    assert calls == ["Re:Zero kara Hajimeru Isekai Seikatsu"]
    assert controller.last_online_requery_title == "Re:Zero kara Hajimeru Isekai Seikatsu"
    assert any("online_selection_requery_scheduled" in message for _, message in log_messages)
    assert any("already_requeried" in message for _, message in log_messages)


def test_find_anime_result_by_title_uses_online_provider(parent, monkeypatch, log_messages):
    expected = AnimeSearchResult(
        anilist_id=116589,
        title_romaji="86 Eighty-Six",
        title_english="86 EIGHTY-SIX",
        title_native="86―エイティシックス―",
        cover_url="https://example.test/86.jpg",
        season_year=2021,
    )

    monkeypatch.setattr(
        controller_module,
        "search_anime_online_response",
        lambda title="": _make_response(results=[expected]),
    )

    controller, _, _ = _make_controller(parent)

    result = controller.find_anime_result_by_title("86 Eighty-Six")

    assert result is expected
    assert any("find_anime_result_matched" in message for _, message in log_messages)


def test_find_anime_result_by_title_ignores_trailing_result_whitespace(
    parent, monkeypatch, log_messages
):
    expected = AnimeSearchResult(
        anilist_id=196029,
        title_romaji="Kami no Niwatsuki Kusunoki-tei ",
        title_english="Kusunoki's Garden of Gods",
        title_native=None,
        cover_url="https://example.test/kusunoki.jpg",
        season_year=2026,
    )

    monkeypatch.setattr(
        controller_module,
        "search_anime_online_response",
        lambda title="": _make_response(results=[expected]),
    )

    controller, _, _ = _make_controller(parent)

    result = controller.find_anime_result_by_title("Kami no Niwatsuki Kusunoki-tei")

    assert result is expected
    assert any("find_anime_result_matched" in message for _, message in log_messages)


def test_find_anime_result_by_title_reports_connection_error(parent, monkeypatch, log_messages):
    connection_errors = []
    monkeypatch.setattr(
        controller_module,
        "search_anime_online_response",
        lambda title="": _make_response(
            error="api_request_failed",
            error_detail="simulated network error",
        ),
    )
    controller, model, _ = _make_controller(
        parent,
        on_connection_error=lambda reason, detail: connection_errors.append((reason, detail)),
    )
    model.setStringList(["Existing"])

    result = controller.find_anime_result_by_title("86 Eighty-Six")

    assert result is None
    assert model.stringList() == []
    assert connection_errors == [("api_request_failed", "simulated network error")]
    assert any("online_title_search_failed" in message for _, message in log_messages)


def test_reset_online_state_clears_state_and_stops_timer(parent, log_messages):
    controller, _, _ = _make_controller(parent)
    controller.pending_title_search_query = "Re:"
    controller.last_manual_online_query = "Re:"
    controller.last_online_requery_title = "Re:Zero"
    controller._active_search_query = "Re:"
    controller._queued_search_query = "Re:Zero"
    controller.title_search_timer.start()

    controller.reset_online_state()

    assert controller.pending_title_search_query == ""
    assert controller.last_manual_online_query == ""
    assert controller.last_online_requery_title == ""
    assert controller._active_search_query == ""
    assert controller._queued_search_query is None
    assert controller.title_search_timer.isActive() is False
    assert any("title_search_state_reset" in message for _, message in log_messages)
