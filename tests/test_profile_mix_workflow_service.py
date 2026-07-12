from PyQt6.QtWidgets import QComboBox, QSpinBox

import app.services.profile_mix_workflow_service as workflow_service


def _combo(items, current):
    combo = QComboBox()
    combo.addItems(items)
    combo.setCurrentText(current)
    return combo


def _spin(value):
    spin = QSpinBox()
    spin.setRange(0, 100)
    spin.setValue(value)
    return spin


def test_apply_mix_mode_change_workflow_updates_rows_weights_and_memory(
    monkeypatch,
    qtbot,
):
    profiles = {"Balanced": [], "Visual": [], "Drama": []}
    combos = [
        _combo(list(profiles), "Balanced"),
        _combo(list(profiles), "Visual"),
        _combo(list(profiles), "Drama"),
    ]
    spins = [_spin(34), _spin(33), _spin(33)]
    for widget in [*combos, *spins]:
        qtbot.addWidget(widget)
    building_values = []
    log_messages = []
    monkeypatch.setattr(
        workflow_service,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )

    state = workflow_service.apply_mix_mode_change_workflow(
        profile_combos=combos,
        weight_spins=spins,
        profiles=profiles,
        selection_memory=["Balanced", "Visual", "Drama"],
        current_mix_needed=3,
        mix_mode="2 profil",
        mix_modes={"1 profil": 1, "2 profil": 2, "3 profil": 3},
        total_weight=100,
        set_building=lambda value: building_values.append(value),
    )

    assert building_values == [True, False]
    assert state.current_mix_needed == 2
    assert state.selection_memory == ["Balanced", "Visual", "Drama"]
    assert [combo.isEnabled() for combo in combos] == [True, True, False]
    assert [spin.isEnabled() for spin in spins] == [True, True, False]
    assert [spin.value() for spin in spins] == [34, 66, 0]
    assert combos[0].currentText() == "Balanced"
    assert combos[1].currentText() == "Visual"
    assert combos[2].currentText() == "—"
    assert log_messages == [("ui", "mix_mode_changed: mode='2 profil'")]


def test_apply_profile_selection_change_workflow_refreshes_options_and_memory(
    monkeypatch,
    qtbot,
):
    profiles = {"Balanced": [], "Visual": [], "Drama": []}
    combos = [
        _combo(list(profiles), "Balanced"),
        _combo(list(profiles), "Balanced"),
        _combo(list(profiles), "Drama"),
    ]
    spins = [_spin(50), _spin(50), _spin(0)]
    for widget in [*combos, *spins]:
        qtbot.addWidget(widget)
    building_values = []
    log_messages = []
    monkeypatch.setattr(
        workflow_service,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )

    state = workflow_service.apply_profile_selection_change_workflow(
        profile_combos=combos,
        weight_spins=spins,
        profiles=profiles,
        selection_memory=["Balanced", "Visual", "Drama"],
        mix_mode="2 profil",
        mix_modes={"1 profil": 1, "2 profil": 2, "3 profil": 3},
        set_building=lambda value: building_values.append(value),
    )

    assert building_values == [True, False]
    assert state.selected == ["Balanced", "Balanced"]
    assert state.ratios == [0.5, 0.5]
    assert state.selection_memory == ["Balanced", "Visual", "Drama"]
    assert combos[0].currentText() == "Balanced"
    assert combos[1].currentText() == "Visual"
    assert log_messages == [
        ("ui", "profile_changed: selected=['Balanced', 'Balanced'] ratios=[0.5, 0.5]"),
    ]


def test_apply_profile_weight_change_workflow_adjusts_active_weights(
    monkeypatch,
    qtbot,
):
    spins = [_spin(70), _spin(20), _spin(50)]
    for spin in spins:
        qtbot.addWidget(spin)
    building_values = []
    log_messages = []
    monkeypatch.setattr(
        workflow_service,
        "log_info",
        lambda component, message: log_messages.append((component, message)),
    )

    handled = workflow_service.apply_profile_weight_change_workflow(
        weight_spins=spins,
        changed_idx=0,
        new_value=70,
        mix_mode="2 profil",
        mix_modes={"1 profil": 1, "2 profil": 2, "3 profil": 3},
        set_building=lambda value: building_values.append(value),
    )

    assert handled is True
    assert building_values == [True, False]
    assert [spin.value() for spin in spins] == [70, 30, 50]
    assert log_messages == [("ui", "weight_changed: idx=0 value=70")]
