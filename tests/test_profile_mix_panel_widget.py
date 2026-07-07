from app.widgets.profile_mix_panel_widget import ProfileMixPanelWidget


def test_profile_mix_panel_uses_hungarian_labels(qtbot):
    panel = ProfileMixPanelWidget(["Balanced", "Visual"], total_weight=100)
    qtbot.addWidget(panel)

    layout = panel.layout()

    assert panel.title() == "Profil konfiguráció"
    assert layout.itemAtPosition(0, 1).widget().text() == "Profil"
    assert layout.itemAtPosition(0, 3).widget().text() == "Súly (0-100)"
    assert [label.text() for label in panel.profile_labels] == [
        "Profil 1:",
        "Profil 2:",
        "Profil 3:",
    ]


def test_profile_mix_panel_builds_three_profile_rows(qtbot):
    panel = ProfileMixPanelWidget(["Balanced", "Visual"], total_weight=100)
    qtbot.addWidget(panel)

    assert len(panel.profile_combos) == 3
    assert len(panel.weight_spins) == 3

    for combo in panel.profile_combos:
        assert [combo.itemText(index) for index in range(combo.count())] == [
            "Balanced",
            "Visual",
        ]

    for weight_spin in panel.weight_spins:
        assert weight_spin.minimum() == 0
        assert weight_spin.maximum() == 100
        assert weight_spin.singleStep() == 1
        assert weight_spin.value() == 0
