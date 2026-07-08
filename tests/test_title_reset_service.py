from PyQt6.QtWidgets import QLineEdit

from app.services.title_reset_service import reset_title_input_state


class DummyTitleSearchController:
    def __init__(self):
        self.reset_calls = 0

    def reset_online_state(self) -> None:
        self.reset_calls += 1


def test_reset_title_input_state_clears_title_and_controller_state(qtbot):
    title_edit = QLineEdit()
    title_edit.setText("Cowboy Bebop")
    qtbot.addWidget(title_edit)
    controller = DummyTitleSearchController()

    reset_state = reset_title_input_state(title_edit, controller)

    assert title_edit.text() == ""
    assert controller.reset_calls == 1
    assert reset_state.selected_anime_result is None
    assert reset_state.selected_cover_pixmap is None


def test_reset_title_input_state_allows_missing_controller(qtbot):
    title_edit = QLineEdit()
    title_edit.setText("Trigun")
    qtbot.addWidget(title_edit)

    reset_state = reset_title_input_state(title_edit, None)

    assert title_edit.text() == ""
    assert reset_state.selected_anime_result is None
    assert reset_state.selected_cover_pixmap is None
