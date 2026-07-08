from PyQt6.QtWidgets import QSpinBox

from app.services.profile_weight_reset_service import apply_initial_profile_weights


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
