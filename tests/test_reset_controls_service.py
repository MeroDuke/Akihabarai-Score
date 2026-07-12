from PyQt6.QtWidgets import QComboBox

from app.services.reset_controls_service import (
    reset_combo_to_first_item,
    reset_profile_combos_to_first_item,
)


def _combo_with_items(current_index: int) -> QComboBox:
    combo = QComboBox()
    combo.addItems(["Első", "Második", "Harmadik"])
    combo.setCurrentIndex(current_index)
    return combo


def test_reset_combo_to_first_item_blocks_signals(qtbot):
    combo = _combo_with_items(2)
    qtbot.addWidget(combo)
    emitted_indexes = []
    combo.currentIndexChanged.connect(emitted_indexes.append)

    reset_combo_to_first_item(combo)

    assert combo.currentIndex() == 0
    assert emitted_indexes == []


def test_reset_profile_combos_to_first_item_resets_all_combos(qtbot):
    combos = [_combo_with_items(1), _combo_with_items(2)]
    for combo in combos:
        qtbot.addWidget(combo)

    reset_profile_combos_to_first_item(combos)

    assert [combo.currentIndex() for combo in combos] == [0, 0]
