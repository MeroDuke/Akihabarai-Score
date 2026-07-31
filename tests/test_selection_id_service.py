from PyQt6.QtWidgets import QComboBox
from types import SimpleNamespace

from app.services.selection_id_service import (
    add_identifier_items,
    current_identifier,
    find_identifier,
    set_identifier_labels,
)
from app.services.tier_card_edit_service import capture_tier_card_input_snapshot


def test_combo_displays_label_but_exposes_stable_identifier(qtbot):
    combo = QComboBox()
    qtbot.addWidget(combo)
    set_identifier_labels(
        combo,
        {
            "fantasy": "Fantasy",
            "mystery": "Rejtély",
        },
    )
    add_identifier_items(combo, ["fantasy", "mystery"])

    combo.setCurrentIndex(1)

    assert combo.currentText() == "Rejtély"
    assert current_identifier(combo) == "mystery"
    assert find_identifier(combo, "mystery") == 1


def test_combo_helpers_support_legacy_text_only_items(qtbot):
    combo = QComboBox()
    qtbot.addWidget(combo)
    combo.addItems(["1 profil", "2 profil"])

    combo.setCurrentIndex(1)

    assert current_identifier(combo) == "2 profil"
    assert find_identifier(combo, "2 profil") == 1


def test_tier_card_snapshot_captures_ids_instead_of_visible_labels(qtbot):
    mix_combo = QComboBox()
    profile_combo = QComboBox()
    qtbot.addWidget(mix_combo)
    qtbot.addWidget(profile_combo)
    mix_combo.addItem("2 profil", "double")
    profile_combo.addItem("Rejtély", "mystery")

    window = SimpleNamespace(
        mix_combo=mix_combo,
        profile_combos=[profile_combo],
        weight_spins=[SimpleNamespace(value=lambda: 100)],
        states=[SimpleNamespace(value=7.5)],
    )

    snapshot = capture_tier_card_input_snapshot(window)

    assert snapshot.mix_mode == "double"
    assert snapshot.profile_names == ["mystery"]
