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
        self.enabled = None

    def setText(self, text):
        self.text = text

    def setToolTip(self, tooltip):
        self.tooltip = tooltip

    def setEnabled(self, enabled):
        self.enabled = enabled


def _make_window(current_mode):
    add_button_updates = []
    window = SimpleNamespace(
        current_mode=current_mode,
        mode_btn=FakeButton(),
        mix_combo=FakeButton(),
        profile_mix_panel=FakeButton(),
        dimensions_panel=FakeButton(),
        title_edit=SimpleNamespace(text=lambda: "Cowboy Bebop"),
        update_add_tier_button_state=lambda title: add_button_updates.append(title),
    )
    return window, add_button_updates


def test_apply_scored_mode_shows_current_mode_and_freehand_target():
    window, add_button_updates = _make_window(APP_MODE_SCORED)

    apply_app_mode_for_window(window)

    assert window.mode_btn.text == "Adatvezérelt"
    assert window.mode_btn.tooltip == "Váltás Szabadkezes módra"
    assert window.mix_combo.enabled is True
    assert window.profile_mix_panel.enabled is True
    assert window.dimensions_panel.enabled is True
    assert add_button_updates == ["Cowboy Bebop"]


def test_apply_freehand_mode_disables_scoring_inputs():
    window, add_button_updates = _make_window(APP_MODE_FREEHAND)

    apply_app_mode_for_window(window)

    assert window.mix_combo.enabled is False
    assert window.profile_mix_panel.enabled is False
    assert window.dimensions_panel.enabled is False
    assert add_button_updates == ["Cowboy Bebop"]


def test_toggle_app_mode_switches_mode_text_and_tooltip_both_ways():
    window, _ = _make_window(APP_MODE_SCORED)
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
