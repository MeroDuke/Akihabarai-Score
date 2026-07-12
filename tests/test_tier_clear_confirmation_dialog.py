from PyQt6.QtWidgets import QMessageBox

from app.widgets.tier_clear_confirmation_dialog import (
    build_tier_clear_all_confirmation_dialog,
)


def test_tier_clear_all_confirmation_dialog_uses_hungarian_labels(qtbot):
    dialog = build_tier_clear_all_confirmation_dialog(None)
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Tier lista törlése"
    assert dialog.text() == "Biztosan törlöd az összes mentett kártyát a Tier listáról?"
    assert dialog.icon() == QMessageBox.Icon.Question
    assert dialog.defaultButton() is dialog.button(QMessageBox.StandardButton.No)
    assert dialog.button(QMessageBox.StandardButton.Yes).text() == "Igen"
    assert dialog.button(QMessageBox.StandardButton.No).text() == "Nem"
