import importlib
from types import SimpleNamespace

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMessageBox

import app.main as main_module
import app.services.tier_clear_service as tier_clear_service


@pytest.fixture
def valid_profiles_config():
    dimensions = [
        "Story",
        "Characters",
        "World",
        "Visuals",
        "Music",
        "Pacing",
        "Emotion",
        "Originality",
    ]
    profiles = {
        "Balanced": [1.0] * 8,
        "Story-heavy": [1.2, 1.0, 1.0, 0.8, 0.8, 1.0, 1.0, 1.0],
        "Visual-heavy": [0.8, 0.9, 0.9, 1.3, 1.1, 0.9, 0.9, 1.0],
    }
    tier_thresholds = {
        "S": 9.0,
        "A": 8.0,
        "B": 7.0,
        "C": 6.0,
        "D": 5.0,
    }
    return dimensions, profiles, tier_thresholds, None


@pytest.fixture
def valid_ui_config():
    return {"dummy": True}, None


@pytest.fixture(autouse=True)
def disable_real_update_check(monkeypatch):
    monkeypatch.setattr(
        main_module,
        "check_for_update",
        lambda version: SimpleNamespace(
            ok=True,
            update_available=False,
            local_version="v0.14.1",
            latest_version="v0.14.1",
            error="",
        ),
    )


def _make_window(monkeypatch, qtbot, profiles_cfg, ui_cfg):
    monkeypatch.setattr(main_module, "load_profiles_config", lambda: profiles_cfg)
    monkeypatch.setattr(main_module, "load_ui_config", lambda: ui_cfg)
    monkeypatch.setattr(main_module, "log_info", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module, "log_warning", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module, "log_debug", lambda *args, **kwargs: None)
    monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: None)

    window = main_module.MainWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    return window


def test_main_window_builds_with_valid_config(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    assert window.windowTitle()
    assert len(window.states) == 8
    assert len(window.slider_widgets) == 8
    assert len(window.spin_widgets) == 8
    assert len(window.profile_combos) == 3
    assert len(window.weight_spins) == 3
    assert window.top_inputs_panel.title_label.text() == "Anime / szezon cím:"
    assert window.title_edit.placeholderText() == "pl. Re:Zero S3"
    assert window.top_inputs_panel.mix_label.text() == "Profil-mix mód:"
    assert window.mix_combo.count() > 0
    assert window.profile_mix_panel.title() == "Profil konfiguráció"
    profile_mix_layout = window.profile_mix_panel.layout()
    assert profile_mix_layout.itemAtPosition(0, 1).widget().text() == "Profil"
    assert profile_mix_layout.itemAtPosition(0, 3).widget().text() == "Súly (0-100)"
    assert [
        label.text()
        for label in window.profile_mix_panel.profile_labels
    ] == ["Profil 1:", "Profil 2:", "Profil 3:"]
    assert window.dimensions_panel.title() == "Dimenziók"
    assert window.dimensions_panel.header_name.text() == "Dimenzió"
    assert window.dimensions_panel.header_value.text() == "Pont (1-10)"
    assert window.version_btn.text().startswith("Verzió: v")
    assert window.mode_btn.text() == "Adatvezérelt"
    assert window.mode_btn.toolTip() == "Váltás Szabadkezes módra"
    assert window.reset_btn.text() == "Alaphelyzet (5,0)"
    assert window.add_tier_btn.text() == "Hozzáadás Tier listához"
    assert window.table.columnCount() == 4
    assert window.right_box.title() == "Eredmény"
    assert window.copy_img_btn.text() == "Eredmény képként másolása"
    assert [
        window.table.horizontalHeaderItem(column).text()
        for column in range(window.table.columnCount())
    ] == ["Dimenzió", "Pont", "Relevancia", "Hozzájárulás"]
    assert window.copy_btn.text() == "Részletes adatok másolása vágólapra"
    assert window.tier_box.title() == "Tier lista"
    assert window.flip_all_tier_cards_btn.text() == "Összes kártya megfordítása"
    assert window.clear_all_tier_cards_btn.text() == "Minden kártya törlése"
    assert window.copy_tier_btn.text() == "Tier lista képként másolása"


def test_mode_button_toggles_label_and_reset_preserves_current_mode(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    qtbot.mouseClick(window.mode_btn, Qt.MouseButton.LeftButton)

    assert window.current_mode == "freehand"
    assert window.mode_btn.text() == "Szabadkezes"
    assert window.mode_btn.toolTip() == "Váltás Adatvezérelt módra"
    assert window.title_edit.isEnabled() is True
    assert window.title_mode_btn.isEnabled() is True
    assert window.mix_combo.isEnabled() is False
    assert window.profile_mix_panel.isEnabled() is False
    assert window.dimensions_panel.isEnabled() is False
    assert window.add_tier_btn.isEnabled() is False
    assert window.copy_img_btn.isEnabled() is False
    assert window.copy_btn.isEnabled() is False
    assert window.result_panel.isHidden() is True
    assert [window.main_layout.stretch(index) for index in range(3)] == [4, 0, 5]

    window.title_edit.setText("Frieren")

    assert window.add_tier_btn.isEnabled() is False

    qtbot.mouseClick(window.reset_btn, Qt.MouseButton.LeftButton)

    assert window.current_mode == "freehand"
    assert window.mode_btn.text() == "Szabadkezes"

    qtbot.mouseClick(window.mode_btn, Qt.MouseButton.LeftButton)

    assert window.current_mode == "scored"
    assert window.mode_btn.text() == "Adatvezérelt"
    assert window.mix_combo.isEnabled() is True
    assert window.profile_mix_panel.isEnabled() is True
    assert window.dimensions_panel.isEnabled() is True
    assert window.copy_img_btn.isEnabled() is True
    assert window.copy_btn.isEnabled() is True
    assert window.result_panel.isHidden() is False
    assert [window.main_layout.stretch(index) for index in range(3)] == [4, 2, 3]


def test_mode_cycle_preserves_saved_tier_cards_and_restores_flip_state(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )
    cover = QPixmap(10, 10)
    cover.fill()
    assert window.tier_board.add_saved_entry(
        "Cover anime", 8.0, "A", cover_pixmap=cover
    ) is True
    assert window.tier_board.add_saved_entry(
        "Text anime", 7.0, "B"
    ) is True
    cover_entry = window.tier_board.saved_entries_by_tier["A"][0]
    text_entry = window.tier_board.saved_entries_by_tier["B"][0]
    cover_entry.set_flipped(True)
    saved_titles_before = set(window.tier_board.saved_titles)

    qtbot.mouseClick(window.mode_btn, Qt.MouseButton.LeftButton)

    assert window.tier_board.saved_entry_count() == 2
    assert window.tier_board.saved_entries_by_tier["A"][0] is cover_entry
    assert window.tier_board.saved_entries_by_tier["B"][0] is text_entry
    assert window.tier_board.saved_titles == saved_titles_before
    assert cover_entry.card_side == cover_entry.SIDE_COVER
    assert text_entry.card_side == text_entry.SIDE_DETAILS
    assert cover_entry.flip_button.isHidden() is True
    assert window.flip_all_tier_cards_btn.isEnabled() is False
    assert window.clear_all_tier_cards_btn.isEnabled() is True
    assert window.copy_tier_btn.isEnabled() is True

    qtbot.mouseClick(window.mode_btn, Qt.MouseButton.LeftButton)

    assert window.tier_board.saved_entry_count() == 2
    assert window.tier_board.saved_entries_by_tier["A"][0] is cover_entry
    assert window.tier_board.saved_entries_by_tier["B"][0] is text_entry
    assert cover_entry.card_side == cover_entry.SIDE_COVER
    assert cover_entry.flip_button.isHidden() is False
    assert window.flip_all_tier_cards_btn.isEnabled() is True
    assert window.clear_all_tier_cards_btn.isEnabled() is True
    assert window.copy_tier_btn.isEnabled() is True


def test_mode_cycle_is_safe_with_empty_tier_board(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    qtbot.mouseClick(window.mode_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(window.mode_btn, Qt.MouseButton.LeftButton)

    assert window.current_mode == "scored"
    assert window.tier_board.saved_entry_count() == 0
    assert window.flip_all_tier_cards_btn.isEnabled() is False
    assert window.clear_all_tier_cards_btn.isEnabled() is False
    assert window.copy_tier_btn.isEnabled() is False


def test_mode_change_debug_log_reports_integrated_ui_state(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )
    debug_messages = []
    monkeypatch.setattr(
        main_module,
        "log_debug",
        lambda component, message: debug_messages.append((component, message)),
    )

    qtbot.mouseClick(window.mode_btn, Qt.MouseButton.LeftButton)

    mode_messages = [
        message
        for component, message in debug_messages
        if component == "ui" and message.startswith("app_mode_ui_applied:")
    ]
    assert len(mode_messages) == 1
    assert "mode='freehand'" in mode_messages[0]
    assert "result_panel_visible=False" in mode_messages[0]
    assert "tier_flip=False" in mode_messages[0]
    assert "tier_preview_visible=False" in mode_messages[0]


def test_window_size_uses_ui_config(
    monkeypatch, qtbot, valid_profiles_config
):
    ui_cfg = {
        "window": {
            "default_width": 1600,
            "default_height": 720,
            "minimum_width": 1280,
            "minimum_height": 720,
        }
    }, None

    window = _make_window(monkeypatch, qtbot, valid_profiles_config, ui_cfg)

    assert window.get_default_window_size() == (1600, 720)
    assert window.get_minimum_window_size() == (1280, 720)


def test_window_size_falls_back_when_window_config_is_missing(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    assert window.get_default_window_size() == (
        window.DEFAULT_WINDOW_WIDTH,
        window.DEFAULT_WINDOW_HEIGHT,
    )
    assert window.get_minimum_window_size() == (
        window.DEFAULT_MINIMUM_WINDOW_WIDTH,
        window.DEFAULT_MINIMUM_WINDOW_HEIGHT,
    )


def test_window_size_falls_back_when_window_config_values_are_invalid(
    monkeypatch, qtbot, valid_profiles_config
):
    ui_cfg = {
        "window": {
            "default_width": False,
            "default_height": "invalid",
            "minimum_width": 0,
            "minimum_height": -1,
        }
    }, None

    window = _make_window(monkeypatch, qtbot, valid_profiles_config, ui_cfg)

    assert window.get_default_window_size() == (
        window.DEFAULT_WINDOW_WIDTH,
        window.DEFAULT_WINDOW_HEIGHT,
    )
    assert window.get_minimum_window_size() == (
        window.DEFAULT_MINIMUM_WINDOW_WIDTH,
        window.DEFAULT_MINIMUM_WINDOW_HEIGHT,
    )


def test_main_window_raises_runtime_error_on_invalid_profiles_config(
    monkeypatch, qtbot, valid_ui_config
):
    bad_profiles_cfg = (None, None, None, "Broken profiles config")

    monkeypatch.setattr(main_module, "load_profiles_config", lambda: bad_profiles_cfg)
    monkeypatch.setattr(main_module, "load_ui_config", lambda: valid_ui_config)
    monkeypatch.setattr(main_module, "log_info", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module, "log_warning", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module, "log_debug", lambda *args, **kwargs: None)
    monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: None)

    with pytest.raises(RuntimeError, match="Broken profiles config"):
        main_module.MainWindow()


def test_on_mix_changed_two_profiles_mode_enables_first_two_only(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    target_index = window.mix_combo.findText("2 profil")
    if target_index == -1:
        pytest.skip("A '2 profil' mix mód nem található a MIX_MODES alapján.")

    window.mix_combo.setCurrentIndex(target_index)
    qtbot.wait(50)

    assert window.profile_combos[0].isEnabled() is True
    assert window.profile_combos[1].isEnabled() is True
    assert window.profile_combos[2].isEnabled() is False

    assert window.weight_spins[0].isEnabled() is True
    assert window.weight_spins[1].isEnabled() is True
    assert window.weight_spins[2].isEnabled() is False

    active_weight_sum = window.weight_spins[0].value() + window.weight_spins[1].value()
    assert active_weight_sum == main_module.TOTAL_WEIGHT
    assert window.weight_spins[2].value() == 0

def test_mix_mode_change_preserves_profile_selections(
    monkeypatch, qtbot, valid_ui_config
):
    dimensions = [
        "Story",
        "Characters",
        "World",
        "Visuals",
        "Music",
        "Pacing",
        "Emotion",
        "Originality",
    ]
    profiles = {
        "Balanced": [1.0] * 8,
        "Story-heavy": [1.2, 1.0, 1.0, 0.8, 0.8, 1.0, 1.0, 1.0],
        "Visual-heavy": [0.8, 0.9, 0.9, 1.3, 1.1, 0.9, 0.9, 1.0],
        "Drama-heavy": [1.1, 1.2, 1.0, 0.8, 0.8, 1.0, 1.3, 0.9],
        "Action-heavy": [0.9, 1.0, 0.9, 1.2, 1.1, 1.2, 0.9, 0.8],
    }
    tier_thresholds = {
        "S": 9.0,
        "A": 8.0,
        "B": 7.0,
        "C": 6.0,
        "D": 5.0,
    }
    profiles_cfg = (dimensions, profiles, tier_thresholds, None)

    window = _make_window(monkeypatch, qtbot, profiles_cfg, valid_ui_config)

    three_profile_index = window.mix_combo.findText("3 profil")
    one_profile_index = window.mix_combo.findText("1 profil")

    if three_profile_index == -1 or one_profile_index == -1:
        pytest.skip("A szükséges mix módok nem találhatók a MIX_MODES alapján.")

    window.mix_combo.setCurrentIndex(three_profile_index)
    qtbot.wait(20)

    window.profile_combos[0].setCurrentText("Drama-heavy")
    window.profile_combos[1].setCurrentText("Action-heavy")
    window.profile_combos[2].setCurrentText("Visual-heavy")
    qtbot.wait(20)

    assert window.profile_combos[0].currentText() == "Drama-heavy"
    assert window.profile_combos[1].currentText() == "Action-heavy"
    assert window.profile_combos[2].currentText() == "Visual-heavy"

    window.mix_combo.setCurrentIndex(one_profile_index)
    qtbot.wait(20)

    assert window.profile_combos[0].currentText() == "Drama-heavy"
    assert window.profile_combos[1].currentText() == "—"
    assert window.profile_combos[2].currentText() == "—"

    window.mix_combo.setCurrentIndex(three_profile_index)
    qtbot.wait(20)

    assert window.profile_combos[0].currentText() == "Drama-heavy"
    assert window.profile_combos[1].currentText() == "Action-heavy"
    assert window.profile_combos[2].currentText() == "Visual-heavy"
def test_slider_change_updates_spin_and_state(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    window.slider_widgets[0].setValue(87)
    qtbot.wait(20)

    assert window.states[0].value == 8.7
    assert window.spin_widgets[0].value() == pytest.approx(8.7)


def test_spin_change_updates_slider_and_state(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    window.spin_widgets[1].setValue(6.4)
    qtbot.wait(20)

    assert window.states[1].value == pytest.approx(6.4)
    assert window.slider_widgets[1].value() == 64


def test_recompute_updates_labels_and_table(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    stub_result = {
        "selected": ["Balanced"],
        "ratios": [1.0],
        "values": [5.0] * 8,
        "score": 8.34,
        "display_score": 8.3,
        "tier": "A",
        "summary_html": "<b>Stub summary</b>",
        "relevances": [1.0] * 8,
        "contributions": [0.5] * 8,
    }

    monkeypatch.setattr(main_module, "load_profiles_config", lambda: valid_profiles_config)
    monkeypatch.setattr(main_module, "load_ui_config", lambda: valid_ui_config)
    monkeypatch.setattr(main_module, "build_result_payload", lambda **kwargs: stub_result)
    monkeypatch.setattr(main_module, "log_info", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module, "log_warning", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module, "log_debug", lambda *args, **kwargs: None)
    monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: None)

    window = main_module.MainWindow()
    qtbot.addWidget(window)

    window.recompute()

    assert window.score_label.text() == "8.3 / 10"
    assert window.tier_label.text() == "Tier: A"
    assert window.summary_label.text() == "<b>Stub summary</b>"
    assert window.table.rowCount() == 8
    assert window.table.item(0, 0).text() == "Story"
    assert window.table.item(0, 1).text() == "5"
    assert window.table.item(0, 2).text() == "1.00"
    assert window.table.item(0, 3).text() == "0.50"


def test_reset_values_restores_dimensions_title_and_profile_defaults(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    target_index = window.mix_combo.findText("3 profil")
    if target_index == -1:
        pytest.skip("A '3 profil' mix mód nem található a MIX_MODES alapján.")

    window.title_edit.setText("Teszt cím")
    window.mix_combo.setCurrentIndex(target_index)
    qtbot.wait(20)

    window.profile_combos[0].setCurrentText("Story-heavy")
    window.profile_combos[1].setCurrentText("Visual-heavy")
    window.weight_spins[0].setValue(20)
    window.weight_spins[1].setValue(30)
    window.weight_spins[2].setValue(50)
    window.slider_widgets[0].setValue(91)
    window.spin_widgets[1].setValue(3.2)
    qtbot.wait(20)

    window.reset_values()
    qtbot.wait(20)

    for state in window.states:
        assert state.value == pytest.approx(5.0)

    for slider in window.slider_widgets:
        assert slider.value() == 50

    for spin in window.spin_widgets:
        assert spin.value() == pytest.approx(5.0)

    assert window.title_edit.text() == ""
    assert window.mix_combo.currentIndex() == 0

    assert window.profile_combos[0].isEnabled() is True
    assert window.profile_combos[1].isEnabled() is False
    assert window.profile_combos[2].isEnabled() is False

    assert window.weight_spins[0].isEnabled() is True
    assert window.weight_spins[1].isEnabled() is False
    assert window.weight_spins[2].isEnabled() is False

    assert window.profile_combos[0].currentText() == "Balanced"
    assert window.profile_combos[1].currentText() == "—"
    assert window.profile_combos[2].currentText() == "—"

    assert window.weight_spins[0].value() == main_module.TOTAL_WEIGHT
    assert window.weight_spins[1].value() == 0
    assert window.weight_spins[2].value() == 0


def test_add_tier_button_requires_title(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    assert not window.add_tier_btn.isEnabled()

    window.title_edit.setText("Cowboy Bebop")
    qtbot.wait(20)

    assert window.add_tier_btn.isEnabled()

    window.title_edit.setText("   ")
    qtbot.wait(20)

    assert not window.add_tier_btn.isEnabled()

    window.title_edit.setText("Cowboy Bebop")
    qtbot.wait(20)

    window.reset_values()

    assert not window.add_tier_btn.isEnabled()


def test_title_input_mode_toggle_switches_button_placeholder_and_logs(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    log_messages = []

    monkeypatch.setattr(main_module, "load_profiles_config", lambda: valid_profiles_config)
    monkeypatch.setattr(main_module, "load_ui_config", lambda: valid_ui_config)
    monkeypatch.setattr(main_module, "log_info", lambda component, message: log_messages.append((component, message)))
    monkeypatch.setattr(main_module, "log_warning", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module, "log_debug", lambda *args, **kwargs: None)
    monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: None)

    window = main_module.MainWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)

    assert window.anilist_integration_enabled is True
    assert window.title_input_mode == window.TITLE_INPUT_MODE_OFFLINE
    assert window.title_mode_btn.isVisible() is True
    assert window.title_mode_btn.text() == "✏ Offline"
    assert window.title_edit.placeholderText() == window.title_placeholder_offline

    qtbot.mouseClick(window.title_mode_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(20)

    assert window.title_input_mode == window.TITLE_INPUT_MODE_ONLINE
    assert window.title_mode_btn.text() == "🌐 Online"
    assert window.title_edit.placeholderText() == window.title_placeholder_online
    assert ("ui", "title_input_mode_changed: mode='online'") in log_messages

    qtbot.mouseClick(window.title_mode_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(20)

    assert window.title_input_mode == window.TITLE_INPUT_MODE_OFFLINE
    assert window.title_mode_btn.text() == "✏ Offline"
    assert window.title_edit.placeholderText() == window.title_placeholder_offline
    assert ("ui", "title_input_mode_changed: mode='offline'") in log_messages


def test_title_input_mode_button_can_be_hidden_by_feature_flag(
    monkeypatch, qtbot, valid_profiles_config
):
    ui_cfg = {"features": {"anilist_enabled": False}}, None

    window = _make_window(monkeypatch, qtbot, valid_profiles_config, ui_cfg)

    assert window.anilist_integration_enabled is False
    assert window.title_input_mode == window.TITLE_INPUT_MODE_OFFLINE
    assert window.title_mode_btn.isVisible() is False
    assert window.title_edit.placeholderText() == window.title_placeholder_offline
    assert window.title_search_controller is None
    assert window.title_completer is None
    assert window.title_completer_model is None
    assert window.pending_title_search_query == ""
    assert window.title_search_timer is None

    window.toggle_title_input_mode()

    assert window.title_input_mode == window.TITLE_INPUT_MODE_OFFLINE
    assert window.title_edit.placeholderText() == window.title_placeholder_offline
    assert window.title_search_controller is None

    window._schedule_online_title_search("Frieren")
    window._run_debounced_title_search()

    assert window._find_anime_result_by_title("Frieren") is None


def test_title_autocomplete_selection_stores_runtime_anime_result(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    assert window.selected_anime_result is None

    window.on_title_autocomplete_selected("86 Eighty-Six")

    assert window.selected_anime_result is not None
    assert window.selected_anime_result.anilist_id == 116589
    assert window.selected_anime_result.title_romaji == "86 Eighty-Six"
    assert window.selected_anime_result.cover_url is not None


def test_manual_title_edit_clears_selected_anime_result(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    window.on_title_autocomplete_selected("Sousou no Frieren")
    assert window.selected_anime_result is not None

    window.on_title_search_text_changed("Manual title")

    assert window.selected_anime_result is None


def test_reset_values_clears_selected_anime_result(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    window.on_title_autocomplete_selected("Sousou no Frieren")
    assert window.selected_anime_result is not None

    window.reset_values()

    assert window.selected_anime_result is None


def test_version_button_shows_current_version(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    monkeypatch.setattr(main_module, "APP_VERSION", "0.14.1")

    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    assert window.version_btn.text() == "Verzió: v0.14.1"
    assert window.version_btn.styleSheet() == ""


def test_version_button_adds_v_prefix_only_when_missing(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    monkeypatch.setattr(main_module, "APP_VERSION", "v0.14.1")

    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    assert window.version_btn.text() == "Verzió: v0.14.1"


def test_version_button_click_opens_github_releases_page(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    opened_urls = []
    monkeypatch.setattr(
        main_module.QDesktopServices,
        "openUrl",
        lambda url: opened_urls.append(url.toString()),
    )

    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    qtbot.mouseClick(window.version_btn, Qt.MouseButton.LeftButton)

    assert opened_urls == [window.GITHUB_RELEASES_URL]


def test_check_for_updates_marks_version_button_when_update_available(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    monkeypatch.setattr(
        main_module,
        "check_for_update",
        lambda version: SimpleNamespace(
            ok=True,
            update_available=True,
            local_version="v0.14.1",
            latest_version="v0.15.0",
            error="",
        ),
    )

    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )
    window.check_for_updates()

    assert window.version_btn.text() == "Frissítés elérhető: v0.15.0"
    assert "background-color" in window.version_btn.styleSheet()
    assert "font-weight" in window.version_btn.styleSheet()


def test_check_for_updates_keeps_default_version_button_when_no_update(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    monkeypatch.setattr(
        main_module,
        "check_for_update",
        lambda version: SimpleNamespace(
            ok=True,
            update_available=False,
            local_version="v0.14.1",
            latest_version="v0.14.1",
            error="",
        ),
    )

    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )
    window.version_btn.setText("Frissítés elérhető: v0.15.0")
    window.version_btn.setStyleSheet("background-color: red; font-weight: bold;")

    window.check_for_updates()

    assert window.version_btn.text() == window._build_version_button_text()
    assert window.version_btn.styleSheet() == ""


def test_check_for_updates_keeps_default_version_button_on_error(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    monkeypatch.setattr(
        main_module,
        "check_for_update",
        lambda version: SimpleNamespace(
            ok=False,
            update_available=False,
            local_version="",
            latest_version="",
            error="network timeout",
        ),
    )

    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    window.check_for_updates()

    assert window.version_btn.text() == window._build_version_button_text()
    assert window.version_btn.styleSheet() == ""



def test_tier_flip_all_button_only_enables_when_flippable_card_exists(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    assert window.flip_all_tier_cards_btn.text() == "Összes kártya megfordítása"
    assert window.clear_all_tier_cards_btn.text() == "Minden kártya törlése"
    assert window.flip_all_tier_cards_btn.isEnabled() is False
    assert window.clear_all_tier_cards_btn.isEnabled() is False
    assert window.copy_tier_btn.isEnabled() is False

    assert window.tier_board.add_saved_entry("Szöveges anime", 8.0, "A") is True
    qtbot.wait(20)

    assert window.flip_all_tier_cards_btn.isEnabled() is False
    assert window.clear_all_tier_cards_btn.isEnabled() is True
    assert window.copy_tier_btn.isEnabled() is True

    cover = QPixmap(10, 10)
    cover.fill()
    assert window.tier_board.add_saved_entry(
        "Borítós anime",
        8.5,
        "S",
        cover_pixmap=cover,
    ) is True
    qtbot.wait(20)

    assert window.flip_all_tier_cards_btn.isEnabled() is True
    assert window.clear_all_tier_cards_btn.isEnabled() is True
    assert window.copy_tier_btn.isEnabled() is True

    cover_entry = window.tier_board.saved_entries_by_tier["S"][0]
    cover_entry.remove_requested.emit(cover_entry)
    qtbot.wait(20)

    assert window.flip_all_tier_cards_btn.isEnabled() is False
    assert window.clear_all_tier_cards_btn.isEnabled() is True
    assert window.copy_tier_btn.isEnabled() is True

    text_entry = window.tier_board.saved_entries_by_tier["A"][0]
    text_entry.remove_requested.emit(text_entry)
    qtbot.wait(20)

    assert window.flip_all_tier_cards_btn.isEnabled() is False
    assert window.clear_all_tier_cards_btn.isEnabled() is False
    assert window.copy_tier_btn.isEnabled() is False


def test_tier_flip_all_button_click_calls_tier_board_toggle_when_flippable_exists(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    calls = []
    monkeypatch.setattr(
        window.tier_board,
        "has_flippable_entries",
        lambda: True,
    )
    monkeypatch.setattr(
        window.tier_board,
        "toggle_all_saved_cards",
        lambda: calls.append(True),
    )

    window.flip_all_tier_cards_btn.setEnabled(True)
    qtbot.mouseClick(window.flip_all_tier_cards_btn, Qt.MouseButton.LeftButton)

    assert calls == [True]


def test_tier_flip_all_button_click_is_skipped_when_no_flippable_card_exists(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    calls = []
    monkeypatch.setattr(
        window.tier_board,
        "has_flippable_entries",
        lambda: False,
    )
    monkeypatch.setattr(
        window.tier_board,
        "toggle_all_saved_cards",
        lambda: calls.append(True),
    )

    window.flip_all_tier_cards_btn.setEnabled(True)
    qtbot.mouseClick(window.flip_all_tier_cards_btn, Qt.MouseButton.LeftButton)

    assert calls == []
    assert window.flip_all_tier_cards_btn.isEnabled() is False




def test_tier_clear_all_button_click_calls_tier_board_clear_after_confirmation(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    calls = []
    log_messages = []
    monkeypatch.setattr(
        main_module,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )
    monkeypatch.setattr(
        tier_clear_service,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )
    monkeypatch.setattr(
        window,
        "_ask_clear_all_tier_cards_confirmation",
        lambda: True,
    )
    monkeypatch.setattr(
        window.tier_board,
        "saved_entry_count",
        lambda: 1,
    )
    monkeypatch.setattr(
        window.tier_board,
        "clear_all_saved_entries",
        lambda: calls.append(True) or 1,
    )

    window.clear_all_tier_cards_btn.setEnabled(True)
    qtbot.mouseClick(window.clear_all_tier_cards_btn, Qt.MouseButton.LeftButton)

    assert calls == [True]
    assert (
        "tier_board",
        "clear_all_entries_confirmation: decision='yes'",
    ) in log_messages


def test_tier_clear_all_button_cancel_does_not_clear(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    calls = []
    log_messages = []
    monkeypatch.setattr(
        main_module,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )
    monkeypatch.setattr(
        tier_clear_service,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )
    monkeypatch.setattr(
        window,
        "_ask_clear_all_tier_cards_confirmation",
        lambda: False,
    )
    monkeypatch.setattr(
        window.tier_board,
        "saved_entry_count",
        lambda: 1,
    )
    monkeypatch.setattr(
        window.tier_board,
        "clear_all_saved_entries",
        lambda: calls.append(True) or 1,
    )

    window.clear_all_tier_cards_btn.setEnabled(True)
    qtbot.mouseClick(window.clear_all_tier_cards_btn, Qt.MouseButton.LeftButton)

    assert calls == []
    assert (
        "tier_board",
        "clear_all_entries_confirmation: decision='no'",
    ) in log_messages
    assert ("tier_board", "clear_all_entries_cancelled") in log_messages


def test_tier_copy_button_click_is_skipped_when_tier_board_is_empty(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    calls = []
    monkeypatch.setattr(
        window.tier_board,
        "prepare_export_mode",
        lambda enabled: calls.append(enabled),
    )

    window.copy_tier_btn.setEnabled(True)
    qtbot.mouseClick(window.copy_tier_btn, Qt.MouseButton.LeftButton)

    assert calls == []
    assert window.copy_tier_btn.isEnabled() is False


def test_tier_copy_button_enables_when_card_is_added_and_disables_when_removed(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    assert window.copy_tier_btn.isEnabled() is False

    assert window.tier_board.add_saved_entry("Teszt anime", 8.0, "A") is True
    qtbot.wait(20)

    assert window.copy_tier_btn.isEnabled() is True

    entry = window.tier_board.saved_entries_by_tier["A"][0]
    entry.remove_requested.emit(entry)
    qtbot.wait(20)

    assert window.copy_tier_btn.isEnabled() is False


def test_tier_action_buttons_are_in_same_bottom_row(
    monkeypatch, qtbot, valid_profiles_config, valid_ui_config
):
    window = _make_window(
        monkeypatch, qtbot, valid_profiles_config, valid_ui_config
    )

    tier_layout = window.tier_box.layout()
    bottom_item = tier_layout.itemAt(tier_layout.count() - 1)
    button_row = bottom_item.layout()

    assert button_row is not None
    assert button_row.itemAt(0).widget() is window.flip_all_tier_cards_btn
    assert button_row.itemAt(1).widget() is window.clear_all_tier_cards_btn
    assert button_row.itemAt(2).widget() is window.copy_tier_btn
