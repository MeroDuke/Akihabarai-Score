from PyQt6.QtWidgets import QSpinBox


def apply_initial_profile_weights(
    weight_spins: list[QSpinBox],
    total_weight: int,
) -> None:
    if not weight_spins:
        return

    weight_spins[0].setValue(total_weight)
    for spin in weight_spins[1:]:
        spin.setValue(0)
