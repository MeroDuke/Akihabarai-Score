from PyQt6.QtWidgets import QMessageBox, QWidget
from app.adapters.qt_desktop_adapter import execute_modal_dialog
from app.services.localization_service import translate


def build_tier_clear_all_confirmation_dialog(parent: QWidget | None) -> QMessageBox:
    dialog = QMessageBox(parent)
    dialog.setIcon(QMessageBox.Icon.Question)
    dialog.setWindowTitle(translate("dialog.tier_clear.title"))
    dialog.setText(translate("dialog.tier_clear.message"))
    dialog.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    dialog.setDefaultButton(QMessageBox.StandardButton.No)

    yes_button = dialog.button(QMessageBox.StandardButton.Yes)
    if yes_button is not None:
        yes_button.setText(translate("dialog.yes"))

    no_button = dialog.button(QMessageBox.StandardButton.No)
    if no_button is not None:
        no_button.setText(translate("dialog.no"))

    return dialog


def ask_tier_clear_all_confirmation(parent: QWidget | None) -> bool:
    dialog = build_tier_clear_all_confirmation_dialog(parent)
    answer = execute_modal_dialog(dialog)
    return answer == QMessageBox.StandardButton.Yes
