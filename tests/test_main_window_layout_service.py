from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow

from app.core.models import DimState
from app.services.main_window_layout_service import build_main_window_layout


def _callback(calls, name, *args):
    calls.append((name, args))


def _build_layout(qtbot, *, show_tier_flip_button=True):
    window = QMainWindow()
    qtbot.addWidget(window)
    calls = []

    layout = build_main_window_layout(
        window=window,
        title_placeholder="pl. Re:Zero S3",
        title_max_length=80,
        mix_mode_names=["1 profil", "2 profil"],
        show_title_mode_button=True,
        show_tier_flip_button=show_tier_flip_button,
        profile_names=["Balanced", "Visual"],
        total_weight=100,
        states=[DimState("Történet / plot"), DimState("Karakterek")],
        version_button_text="Verzió: v0.18.0",
        on_recompute=partial(_callback, calls, "recompute"),
        on_title_search_text_changed=partial(_callback, calls, "title_text"),
        on_toggle_title_input_mode=partial(_callback, calls, "toggle_title_mode"),
        on_mix_changed=partial(_callback, calls, "mix_changed"),
        on_profile_changed=partial(_callback, calls, "profile_changed"),
        on_weight_changed=partial(_callback, calls, "weight_changed"),
        on_slider_changed=partial(_callback, calls, "slider_changed"),
        on_spin_changed=partial(_callback, calls, "spin_changed"),
        on_open_releases_page=partial(_callback, calls, "open_releases"),
        on_toggle_app_mode=partial(_callback, calls, "toggle_app_mode"),
        on_reset_values=partial(_callback, calls, "reset"),
        on_add_current_to_tier_board=partial(_callback, calls, "add_tier"),
        on_update_add_tier_button_state=partial(_callback, calls, "add_button_state"),
        on_copy_result_image_to_clipboard=partial(_callback, calls, "copy_result"),
        on_copy_to_clipboard=partial(_callback, calls, "copy_details"),
        on_update_tier_buttons_state=partial(_callback, calls, "tier_buttons"),
        on_flip_all_tier_cards=partial(_callback, calls, "flip_tier"),
        on_clear_all_tier_cards=partial(_callback, calls, "clear_tier"),
        on_copy_tier_image_to_clipboard=partial(_callback, calls, "copy_tier"),
    )

    window.show()
    qtbot.waitExposed(window)
    return window, layout, calls


def test_build_main_window_layout_creates_expected_panels(qtbot):
    window, layout, _ = _build_layout(qtbot)

    assert window.centralWidget() is not None
    assert layout.left_box.title() == "Bevitel"
    assert layout.top_inputs_panel.title_label.text() == "Anime / szezon cím:"
    assert layout.profile_mix_panel.title() == "Profil konfiguráció"
    assert layout.dimensions_panel.title() == "Dimenziók"
    assert layout.action_buttons_panel.version_btn.text() == "Verzió: v0.18.0"
    assert layout.result_panel.title() == "Eredmény"
    assert layout.tier_panel.title() == "Tier lista"
    assert layout.main_layout.indexOf(layout.left_box) >= 0
    assert layout.main_layout.indexOf(layout.result_panel) >= 0
    assert layout.main_layout.indexOf(layout.tier_panel) >= 0


def test_build_main_window_layout_can_hide_only_tier_flip_button(qtbot):
    window, layout, _ = _build_layout(qtbot, show_tier_flip_button=False)

    assert window.isVisible() is True
    assert layout.tier_panel.flip_all_tier_cards_btn.isVisible() is False
    assert layout.tier_panel.clear_all_tier_cards_btn.isVisible() is True
    assert layout.tier_panel.copy_tier_btn.isVisible() is True


def test_build_main_window_layout_wires_primary_button_callbacks(qtbot):
    _, layout, calls = _build_layout(qtbot)

    qtbot.mouseClick(layout.top_inputs_panel.title_mode_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(layout.action_buttons_panel.version_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(layout.action_buttons_panel.mode_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(layout.action_buttons_panel.reset_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(layout.action_buttons_panel.add_tier_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(layout.result_panel.copy_img_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(layout.result_panel.copy_btn, Qt.MouseButton.LeftButton)

    callback_names = [name for name, _ in calls]

    assert "toggle_title_mode" in callback_names
    assert "open_releases" in callback_names
    assert "toggle_app_mode" in callback_names
    assert "reset" in callback_names
    assert "add_tier" in callback_names
    assert "copy_result" in callback_names
    assert "copy_details" in callback_names


def test_build_main_window_layout_wires_input_change_callbacks(qtbot):
    _, layout, calls = _build_layout(qtbot)

    layout.top_inputs_panel.title_edit.setText("Cowboy Bebop")
    layout.profile_mix_panel.weight_spins[0].setValue(25)
    layout.dimensions_panel.slider_widgets[0].setValue(60)
    layout.dimensions_panel.spin_widgets[1].setValue(7.5)

    callback_names = [name for name, _ in calls]

    assert "recompute" in callback_names
    assert "add_button_state" in callback_names
    assert "weight_changed" in callback_names
    assert "slider_changed" in callback_names
    assert "spin_changed" in callback_names
