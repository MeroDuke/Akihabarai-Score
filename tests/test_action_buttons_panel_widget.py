from app.widgets.action_buttons_panel_widget import ActionButtonsPanelWidget


def test_action_buttons_panel_uses_hungarian_labels(qtbot):
    panel = ActionButtonsPanelWidget("Verzió: v0.18.0")
    qtbot.addWidget(panel)

    assert panel.version_btn.text() == "Verzió: v0.18.0"
    assert panel.reset_btn.text() == "Alaphelyzet (5,0)"
    assert panel.add_tier_btn.text() == "Hozzáadás Tier listához"


def test_action_buttons_panel_uses_fixed_button_height(qtbot):
    panel = ActionButtonsPanelWidget("Verzió: v0.18.0")
    qtbot.addWidget(panel)

    assert panel.version_btn.minimumHeight() == 30
    assert panel.version_btn.maximumHeight() == 30
    assert panel.reset_btn.minimumHeight() == 30
    assert panel.reset_btn.maximumHeight() == 30
    assert panel.add_tier_btn.minimumHeight() == 30
    assert panel.add_tier_btn.maximumHeight() == 30
