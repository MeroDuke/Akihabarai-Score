from PyQt6.QtWidgets import QComboBox, QSpinBox

from app.services.profile_weight_reset_service import (
    apply_initial_profile_weights,
    reset_profile_inputs_to_initial_state,
)


def _combo(current_index: int) -> QComboBox:
    combo = QComboBox()
    combo.addItems(["Balanced", "Visual", "Story"])
    combo.setCurrentIndex(current_index)
    return combo


def _spin(value: int) -> QSpinBox:
    spin = QSpinBox()
    spin.setMinimum(0)
    spin.setMaximum(100)
    spin.setValue(value)
    return spin


def test_apply_initial_profile_weights_sets_first_spin_to_total(qtbot):
    spins = [_spin(10), _spin(20), _spin(70)]
    for spin in spins:
        qtbot.addWidget(spin)

    apply_initial_profile_weights(spins, total_weight=100)

    assert [spin.value() for spin in spins] == [100, 0, 0]


def test_apply_initial_profile_weights_allows_empty_spin_list():
    apply_initial_profile_weights([], total_weight=100)


def test_reset_profile_inputs_to_initial_state_resets_controls_and_returns_state(qtbot):
    combos = [_combo(1), _combo(2), _combo(1)]
    spins = [_spin(25), _spin(25), _spin(50)]
    for widget in [*combos, *spins]:
        qtbot.addWidget(widget)

    reset_state = reset_profile_inputs_to_initial_state(
        profile_combos=combos,
        weight_spins=spins,
        profile_names=["Balanced", "Visual"],
        total_weight=100,
    )

    assert [combo.currentIndex() for combo in combos] == [0, 0, 0]
    assert [spin.value() for spin in spins] == [100, 0, 0]
    assert reset_state.selection_memory == ["Balanced", "Visual", "Balanced"]
    assert reset_state.current_mix_needed == 1
