from PyQt6.QtWidgets import QComboBox


def reset_combo_to_first_item(combo: QComboBox) -> None:
    combo.blockSignals(True)
    combo.setCurrentIndex(0)
    combo.blockSignals(False)


def reset_profile_combos_to_first_item(profile_combos: list[QComboBox]) -> None:
    for combo in profile_combos:
        reset_combo_to_first_item(combo)
