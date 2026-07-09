from types import SimpleNamespace

from PyQt6.QtWidgets import QLineEdit, QPushButton

from app.services.title_search_workflow_service import (
    disable_title_autocomplete,
    get_next_title_input_mode,
    handle_title_autocomplete_selected,
    handle_title_search_text_changed,
    sync_title_input_mode_ui,
)


class FakeController:
    def __init__(self, result=None):
        self.result = result
        self.edited_texts = []
        self.refresh_queries = []
        self.selected_titles = []
        self.title_search_timer = SimpleNamespace(stop=lambda: None)

    def handle_title_text_edited(self, text):
        self.edited_texts.append(text)

    def refresh_title_autocomplete_results(self, query=""):
        self.refresh_queries.append(query)

    def find_anime_result_by_title(self, title):
        return self.result

    def handle_title_selected(self, title):
        self.selected_titles.append(title)


def test_get_next_title_input_mode_respects_disabled_integration():
    assert (
        get_next_title_input_mode(
            integration_enabled=False,
            current_mode="online",
            offline_mode="offline",
            online_mode="online",
        )
        == "offline"
    )


def test_sync_title_input_mode_ui_enables_online_autocomplete(qtbot):
    title_edit = QLineEdit()
    title_mode_btn = QPushButton()
    qtbot.addWidget(title_edit)
    qtbot.addWidget(title_mode_btn)
    title_edit.setText("Re:")
    controller = FakeController()

    mode = sync_title_input_mode_ui(
        title_input_mode="online",
        title_placeholder_offline="offline placeholder",
        title_placeholder_online="online placeholder",
        title_edit=title_edit,
        title_mode_btn=title_mode_btn,
        integration_enabled=True,
        controller=controller,
        completer=None,
    )

    assert mode == "online"
    assert title_edit.placeholderText() == "online placeholder"
    assert title_mode_btn.text()
    assert title_edit.completer() is None


def test_handle_title_search_text_changed_clears_changed_selection():
    selected = SimpleNamespace(title_romaji="Sousou no Frieren")
    cover = object()
    controller = FakeController()

    state = handle_title_search_text_changed(
        text="Manual title",
        selected_anime_result=selected,
        selected_cover_pixmap=cover,
        controller=controller,
    )

    assert state.selected_anime_result is None
    assert state.selected_cover_pixmap is None
    assert controller.edited_texts == ["Manual title"]


def test_handle_title_autocomplete_selected_applies_selection_before_recompute(qtbot):
    title_edit = QLineEdit()
    qtbot.addWidget(title_edit)
    result = SimpleNamespace(anilist_id=116589, title_romaji="86 Eighty-Six")
    cover = object()
    controller = FakeController(result=result)
    events = []

    def apply_selection(selected_anime_result, selected_cover_pixmap):
        events.append(("apply", selected_anime_result, selected_cover_pixmap))

    def recompute():
        events.append(("recompute",))

    state = handle_title_autocomplete_selected(
        title="86 Eighty-Six",
        title_edit=title_edit,
        controller=controller,
        recompute=recompute,
        apply_selection=apply_selection,
        load_cover_pixmap=lambda selected: cover,
    )

    assert state.selected_anime_result is result
    assert state.selected_cover_pixmap is cover
    assert title_edit.text() == "86 Eighty-Six"
    assert events == [("apply", result, cover), ("recompute",)]
    assert controller.selected_titles == ["86 Eighty-Six"]


def test_disable_title_autocomplete_clears_completer(qtbot):
    title_edit = QLineEdit()
    qtbot.addWidget(title_edit)

    disable_title_autocomplete(title_edit=title_edit, controller=None)

    assert title_edit.completer() is None
