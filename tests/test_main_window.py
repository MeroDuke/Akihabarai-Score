import importlib

import pytest
from PyQt6.QtWidgets import QMessageBox

import app.main as main_module


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
    assert window.mix_combo.count() > 0
    assert window.table.columnCount() == 4


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
    assert window.table.item(0, 1).text() == "5.0"
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
