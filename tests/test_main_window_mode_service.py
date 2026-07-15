from types import SimpleNamespace

from app.services.main_window_mode_service import (
    APP_MODE_FREEHAND,
    APP_MODE_SCORED,
    apply_app_mode_for_window,
    toggle_app_mode_for_window,
)


class FakeButton:
    def __init__(self):
        self.text = None
        self.tooltip = None

    def setText(self, text):
        self.text = text

    def setToolTip(self, tooltip):
        self.tooltip = tooltip


def test_apply_scored_mode_shows_current_mode_and_freehand_target():
    window = SimpleNamespace(current_mode=APP_MODE_SCORED, mode_btn=FakeButton())

    apply_app_mode_for_window(window)

    assert window.mode_btn.text == "Adatvezérelt"
    assert window.mode_btn.tooltip == "Váltás Szabadkezes módra"


def test_toggle_app_mode_switches_mode_text_and_tooltip_both_ways():
    window = SimpleNamespace(current_mode=APP_MODE_SCORED, mode_btn=FakeButton())
    log_messages = []

    toggle_app_mode_for_window(
        window,
        log_info_func=lambda component, message: log_messages.append(
            (component, message)
        ),
    )

    assert window.current_mode == APP_MODE_FREEHAND
    assert window.mode_btn.text == "Szabadkezes"
    assert window.mode_btn.tooltip == "Váltás Adatvezérelt módra"

    toggle_app_mode_for_window(
        window,
        log_info_func=lambda component, message: log_messages.append(
            (component, message)
        ),
    )

    assert window.current_mode == APP_MODE_SCORED
    assert window.mode_btn.text == "Adatvezérelt"
    assert window.mode_btn.tooltip == "Váltás Szabadkezes módra"
    assert log_messages == [
        ("ui", "button_click: toggle_app_mode"),
        ("ui", "app_mode_changed: mode='freehand'"),
        ("ui", "button_click: toggle_app_mode"),
        ("ui", "app_mode_changed: mode='scored'"),
    ]
