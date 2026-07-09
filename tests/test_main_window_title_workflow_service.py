from types import SimpleNamespace

from PyQt6.QtWidgets import QLineEdit, QPushButton

from app.services import main_window_title_workflow_service as title_workflow


class FakeController:
    def __init__(self):
        self.pending_title_search_query = "Re:"
        self.title_search_timer = SimpleNamespace(stop=lambda: None)
        self.scheduled = []
        self.ran = False
        self.find_calls = []

    def schedule_online_title_search(self, query):
        self.scheduled.append(query)

    def run_debounced_title_search(self):
        self.ran = True

    def find_anime_result_by_title(self, title):
        self.find_calls.append(title)
        return SimpleNamespace(anilist_id=1, title_romaji=title)


def _make_window(qtbot):
    window = SimpleNamespace()
    window.TITLE_INPUT_MODE_OFFLINE = "offline"
    window.TITLE_INPUT_MODE_ONLINE = "online"
    window.title_input_mode = "offline"
    window.anilist_integration_enabled = True
    window.title_placeholder_offline = "Offline"
    window.title_placeholder_online = "Online"
    window.title_search_debounce_ms = 1000
    window.title_edit = QLineEdit()
    window.title_mode_btn = QPushButton()
    window.title_search_controller = FakeController()
    window.title_completer = None
    window.selected_anime_result = None
    window.selected_cover_pixmap = None
    window.recompute_calls = 0
    window.recompute = lambda: setattr(
        window,
        "recompute_calls",
        window.recompute_calls + 1,
    )
    window._set_selected_title_state = lambda result, cover: (
        setattr(window, "selected_anime_result", result),
        setattr(window, "selected_cover_pixmap", cover),
    )
    window.on_title_autocomplete_selected = lambda title: None
    qtbot.addWidget(window.title_edit)
    qtbot.addWidget(window.title_mode_btn)
    return window


def test_toggle_title_input_mode_for_window_logs_and_updates_ui(qtbot):
    window = _make_window(qtbot)
    log_messages = []

    title_workflow.toggle_title_input_mode_for_window(
        window,
        log_change=True,
        log_info_func=lambda component, message: log_messages.append(
            (component, message)
        ),
    )

    assert window.title_input_mode == "online"
    assert window.title_edit.placeholderText() == "Online"
    assert ("ui", "title_input_mode_changed: mode='online'") in log_messages


def test_title_search_controller_accessors_allow_missing_controller(qtbot):
    window = _make_window(qtbot)
    window.title_search_controller = None

    assert title_workflow.get_pending_title_search_query(window) == ""
    assert title_workflow.get_title_search_timer(window) is None


def test_schedule_run_and_find_delegate_to_controller(qtbot):
    window = _make_window(qtbot)

    title_workflow.schedule_online_title_search_for_window(window, "Frieren")
    title_workflow.run_debounced_title_search_for_window(window)
    result = title_workflow.find_anime_result_by_title_for_window(window, "Frieren")

    assert window.title_search_controller.scheduled == ["Frieren"]
    assert window.title_search_controller.ran is True
    assert result.title_romaji == "Frieren"


def test_handle_title_search_text_changed_updates_selection(qtbot, monkeypatch):
    window = _make_window(qtbot)
    selected = SimpleNamespace(title_romaji="Sousou no Frieren")
    cover = object()
    window.selected_anime_result = selected
    window.selected_cover_pixmap = cover
    returned_state = SimpleNamespace(
        selected_anime_result=None,
        selected_cover_pixmap=None,
    )
    calls = []
    monkeypatch.setattr(
        title_workflow,
        "handle_title_search_text_changed",
        lambda **kwargs: calls.append(kwargs) or returned_state,
    )

    title_workflow.handle_title_search_text_changed_for_window(window, "Manual")

    assert calls[0]["text"] == "Manual"
    assert calls[0]["selected_anime_result"] is selected
    assert calls[0]["selected_cover_pixmap"] is cover
    assert window.selected_anime_result is None
    assert window.selected_cover_pixmap is None


def test_handle_title_autocomplete_selected_updates_selection(qtbot, monkeypatch):
    window = _make_window(qtbot)
    result = SimpleNamespace(anilist_id=116589)
    cover = object()
    returned_state = SimpleNamespace(
        selected_anime_result=result,
        selected_cover_pixmap=cover,
    )
    calls = []
    monkeypatch.setattr(
        title_workflow,
        "handle_title_autocomplete_selected",
        lambda **kwargs: calls.append(kwargs) or returned_state,
    )

    title_workflow.handle_title_autocomplete_selected_for_window(window, "86")

    assert calls[0]["title"] == "86"
    assert calls[0]["title_edit"] is window.title_edit
    assert calls[0]["controller"] is window.title_search_controller
    assert window.selected_anime_result is result
    assert window.selected_cover_pixmap is cover
