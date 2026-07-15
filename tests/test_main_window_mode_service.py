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
        self.hidden = False

    def setText(self, text):
        self.text = text

    def setToolTip(self, tooltip):
        self.tooltip = tooltip

    def setEnabled(self, enabled):
        self.enabled = enabled

    def isEnabled(self):
        return self.enabled

    def setVisible(self, visible):
        self.hidden = not visible

    def isHidden(self):
        return self.hidden


class FakeLayout:
    def __init__(self):
        self.stretches = {}

    def setStretch(self, index, stretch):
        self.stretches[index] = stretch


class FakeTierBoard:
    def __init__(self, fronted_count=0):
        self.fronted_count = fronted_count
        self.show_front_calls = 0

    def show_all_front_sides(self):
        self.show_front_calls += 1
        return self.fronted_count


def _make_window(current_mode):
    add_button_updates = []
    window = SimpleNamespace(
        current_mode=current_mode,
        mode_btn=FakeButton(),
        mix_combo=FakeButton(),
        profile_mix_panel=FakeButton(),
        dimensions_panel=FakeButton(),
        add_tier_btn=FakeButton(),
        result_panel=FakeButton(),
        tier_panel=SimpleNamespace(set_flip_enabled=lambda enabled: None),
        tier_board=FakeTierBoard(fronted_count=2),
        flip_all_tier_cards_btn=FakeButton(),
        main_layout=FakeLayout(),
        title_edit=SimpleNamespace(text=lambda: "Cowboy Bebop"),
        update_add_tier_button_state=lambda title: (
            add_button_updates.append(title),
            window.add_tier_btn.setEnabled(
                window.current_mode == APP_MODE_SCORED and bool(title.strip())
            ),
        ),
    )
    return window, add_button_updates


def test_apply_scored_mode_shows_current_mode_and_freehand_target():
    window, add_button_updates = _make_window(APP_MODE_SCORED)
    debug_messages = []

    apply_app_mode_for_window(
        window,
        log_debug_func=lambda component, message: debug_messages.append(
            (component, message)
        ),
    )

    assert window.mode_btn.text == "Adatvezérelt"
    assert window.mode_btn.tooltip == "Váltás Szabadkezes módra"
    assert window.mix_combo.enabled is True
    assert window.profile_mix_panel.enabled is True
    assert window.dimensions_panel.enabled is True
    assert add_button_updates == ["Cowboy Bebop"]
    assert window.result_panel.isHidden() is False
    assert window.main_layout.stretches == {0: 4, 1: 2, 2: 3}
    assert debug_messages == [
        (
            "ui",
            "app_mode_ui_applied: mode='scored' mix_combo=True "
            "profile_mix=True dimensions=True add_tier=True "
            "result_panel_visible=True layout_stretches=(4, 2, 3) "
            "tier_flip=None tier_cards_fronted=0",
        )
    ]
    assert window.tier_board.show_front_calls == 0


def test_apply_freehand_mode_disables_scoring_inputs():
    window, add_button_updates = _make_window(APP_MODE_FREEHAND)
    debug_messages = []

    apply_app_mode_for_window(
        window,
        log_debug_func=lambda component, message: debug_messages.append(
            (component, message)
        ),
    )

    assert window.mix_combo.enabled is False
    assert window.profile_mix_panel.enabled is False
    assert window.dimensions_panel.enabled is False
    assert add_button_updates == ["Cowboy Bebop"]
    assert window.result_panel.isHidden() is True
    assert window.main_layout.stretches == {0: 4, 1: 0, 2: 5}
    assert debug_messages == [
        (
            "ui",
            "app_mode_ui_applied: mode='freehand' mix_combo=False "
            "profile_mix=False dimensions=False add_tier=False "
            "result_panel_visible=False layout_stretches=(4, 0, 5) "
            "tier_flip=None tier_cards_fronted=2",
        )
    ]
    assert window.tier_board.show_front_calls == 1


def test_toggle_app_mode_switches_mode_text_and_tooltip_both_ways():
    window, _ = _make_window(APP_MODE_SCORED)
    log_messages = []
    debug_messages = []

    toggle_app_mode_for_window(
        window,
        log_info_func=lambda component, message: log_messages.append(
            (component, message)
        ),
        log_debug_func=lambda component, message: debug_messages.append(
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
        log_debug_func=lambda component, message: debug_messages.append(
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
    assert len(debug_messages) == 2
    assert "mode='freehand'" in debug_messages[0][1]
    assert "mode='scored'" in debug_messages[1][1]
