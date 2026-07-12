from PyQt6.QtWidgets import QComboBox, QSpinBox

from app.services.profile_mix_service import (
    INACTIVE_PROFILE_LABEL,
    apply_profile_mix_row_states,
    refresh_active_profile_combo_options,
)


def _combo() -> QComboBox:
    combo = QComboBox()
    combo.addItems(["Old", "Values"])
    combo.setCurrentIndex(1)
    return combo


def _spin(value: int) -> QSpinBox:
    spin = QSpinBox()
    spin.setMinimum(0)
    spin.setMaximum(100)
    spin.setValue(value)
    return spin


def test_apply_profile_mix_row_states_updates_active_and_inactive_rows(qtbot):
    combos = [_combo(), _combo(), _combo()]
    spins = [_spin(40), _spin(60), _spin(30)]
    for widget in [*combos, *spins]:
        qtbot.addWidget(widget)

    apply_profile_mix_row_states(
        profile_combos=combos,
        weight_spins=spins,
        profile_names=["Balanced", "Visual", "Story"],
        needed=2,
    )

    assert [combo.isEnabled() for combo in combos] == [True, True, False]
    assert [spin.isEnabled() for spin in spins] == [True, True, False]
    assert [spins[index].value() for index in range(3)] == [40, 60, 0]
    assert [combos[0].itemText(index) for index in range(combos[0].count())] == [
        "Balanced",
        "Visual",
        "Story",
    ]
    assert [combos[1].itemText(index) for index in range(combos[1].count())] == [
        "Balanced",
        "Visual",
        "Story",
    ]
    assert combos[2].itemText(0) == INACTIVE_PROFILE_LABEL
    assert combos[2].currentText() == "—"


def test_apply_profile_mix_row_states_restores_active_profile_selection(qtbot):
    combos = [_combo(), _combo(), _combo()]
    spins = [_spin(40), _spin(60), _spin(0)]
    for widget in [*combos, *spins]:
        qtbot.addWidget(widget)

    def restore_selection(combo: QComboBox, index: int) -> None:
        if index == 1:
            combo.setCurrentText("Story")

    apply_profile_mix_row_states(
        profile_combos=combos,
        weight_spins=spins,
        profile_names=["Balanced", "Visual", "Story"],
        needed=2,
        restore_profile_selection=restore_selection,
    )

    assert combos[0].currentText() == "Balanced"
    assert combos[1].currentText() == "Story"
    assert combos[2].currentText() == "—"


def test_apply_profile_mix_row_states_blocks_combo_signals(qtbot):
    combos = [_combo(), _combo(), _combo()]
    spins = [_spin(40), _spin(60), _spin(0)]
    for widget in [*combos, *spins]:
        qtbot.addWidget(widget)
    emitted_indexes = []
    for combo in combos:
        combo.currentIndexChanged.connect(emitted_indexes.append)

    apply_profile_mix_row_states(
        profile_combos=combos,
        weight_spins=spins,
        profile_names=["Balanced", "Visual", "Story"],
        needed=1,
    )

    assert emitted_indexes == []


def test_refresh_active_profile_combo_options_keeps_active_profiles_unique(qtbot):
    combos = [_combo(), _combo(), _combo()]
    for combo in combos:
        qtbot.addWidget(combo)
        combo.clear()
        combo.addItems(["Balanced", "Visual", "Story"])

    combos[0].setCurrentText("Balanced")
    combos[1].setCurrentText("Balanced")
    combos[2].setCurrentText("Story")

    refresh_active_profile_combo_options(
        profile_combos=combos,
        all_profiles=["Balanced", "Visual", "Story"],
        needed=3,
    )

    assert combos[0].currentText() == "Balanced"
    assert combos[1].currentText() == "Visual"
    assert combos[2].currentText() == "Story"
    assert [combos[0].itemText(index) for index in range(combos[0].count())] == [
        "Balanced",
    ]
    assert [combos[1].itemText(index) for index in range(combos[1].count())] == [
        "Visual",
    ]


def test_refresh_active_profile_combo_options_leaves_inactive_combo_untouched(qtbot):
    combos = [_combo(), _combo(), _combo()]
    for combo in combos:
        qtbot.addWidget(combo)
        combo.clear()
        combo.addItems(["Balanced", "Visual", "Story"])
    combos[2].clear()
    combos[2].addItem(INACTIVE_PROFILE_LABEL)

    refresh_active_profile_combo_options(
        profile_combos=combos,
        all_profiles=["Balanced", "Visual", "Story"],
        needed=2,
    )

    assert combos[2].count() == 1
    assert combos[2].currentText() == "—"


def test_refresh_active_profile_combo_options_blocks_combo_signals(qtbot):
    combos = [_combo(), _combo(), _combo()]
    for combo in combos:
        qtbot.addWidget(combo)
        combo.clear()
        combo.addItems(["Balanced", "Visual", "Story"])
    emitted_indexes = []
    for combo in combos:
        combo.currentIndexChanged.connect(emitted_indexes.append)

    refresh_active_profile_combo_options(
        profile_combos=combos,
        all_profiles=["Balanced", "Visual", "Story"],
        needed=2,
    )

    assert emitted_indexes == []
