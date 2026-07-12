from PyQt6.QtWidgets import QMessageBox, QWidget


def build_tier_clear_all_confirmation_dialog(parent: QWidget | None) -> QMessageBox:
    dialog = QMessageBox(parent)
    dialog.setIcon(QMessageBox.Icon.Question)
    dialog.setWindowTitle("Tier lista törlése")
    dialog.setText("Biztosan törlöd az összes mentett kártyát a Tier listáról?")
    dialog.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    dialog.setDefaultButton(QMessageBox.StandardButton.No)

    yes_button = dialog.button(QMessageBox.StandardButton.Yes)
    if yes_button is not None:
        yes_button.setText("Igen")

    no_button = dialog.button(QMessageBox.StandardButton.No)
    if no_button is not None:
        no_button.setText("Nem")

    return dialog


def ask_tier_clear_all_confirmation(parent: QWidget | None) -> bool:
    dialog = build_tier_clear_all_confirmation_dialog(parent)
    answer = dialog.exec()
    return answer == QMessageBox.StandardButton.Yes
