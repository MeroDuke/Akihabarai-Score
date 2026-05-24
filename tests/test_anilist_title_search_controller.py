import pytest
from PyQt6.QtCore import QObject, QStringListModel

import app.controllers.anilist_title_search_controller as controller_module
from app.controllers.anilist_title_search_controller import AniListTitleSearchController
from app.core.models import AnimeSearchResult


class DummyCompleter:
    def __init__(self):
        self.complete_count = 0

    def complete(self):
        self.complete_count += 1


@pytest.fixture
def log_messages(monkeypatch):
    messages = []
    monkeypatch.setattr(
        controller_module,
        "log_debug",
        lambda component, message: messages.append((component, message)),
    )
    return messages


@pytest.fixture
def parent(qtbot):
    obj = QObject()
    return obj


def _make_controller(
    parent,
    *,
    online=True,
    enabled=True,
    debounce_ms=1000,
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


def test_run_debounced_title_search_refreshes_model_and_opens_popup_for_multiple_results(
    parent, monkeypatch, log_messages
):
    monkeypatch.setattr(
        controller_module,
        "search_anime_titles_online",
        lambda query="": ["Result A", "Result B"],
    )
    controller, model, completer = _make_controller(parent)
    controller.pending_title_search_query = "Result"

    controller.run_debounced_title_search()

    assert model.stringList() == ["Result A", "Result B"]
    assert completer.complete_count == 1
    assert any("autocomplete_popup_opened" in message for _, message in log_messages)


def test_run_debounced_title_search_suppresses_popup_for_single_exact_match(
    parent, monkeypatch, log_messages
):
    monkeypatch.setattr(
        controller_module,
        "search_anime_titles_online",
        lambda query="": ["86 Eighty-Six"],
    )
    controller, model, completer = _make_controller(parent)
    controller.pending_title_search_query = "86 Eighty-Six"

    controller.run_debounced_title_search()

    assert model.stringList() == ["86 Eighty-Six"]
    assert completer.complete_count == 0
    assert any("single_exact_match" in message for _, message in log_messages)


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
        "search_anime_online",
        lambda title="": [expected],
    )

    controller, _, _ = _make_controller(parent)

    result = controller.find_anime_result_by_title("86 Eighty-Six")

    assert result is expected
    assert any("find_anime_result_matched" in message for _, message in log_messages)


def test_reset_online_state_clears_state_and_stops_timer(parent, log_messages):
    controller, _, _ = _make_controller(parent)
    controller.pending_title_search_query = "Re:"
    controller.last_manual_online_query = "Re:"
    controller.last_online_requery_title = "Re:Zero"
    controller.title_search_timer.start()

    controller.reset_online_state()

    assert controller.pending_title_search_query == ""
    assert controller.last_manual_online_query == ""
    assert controller.last_online_requery_title == ""
    assert controller.title_search_timer.isActive() is False
    assert any("title_search_state_reset" in message for _, message in log_messages)
