from PyQt6.QtWidgets import QMessageBox, QWidget
from app.adapters.qt_desktop_adapter import show_warning
from app.services.localization_service import translate


def show_profiles_config_error(parent: QWidget | None, message: str) -> None:
    show_warning(
        parent,
        translate("dialog.config_profiles.title"),
        message,
        message_box=QMessageBox,
    )


def show_ui_config_error(parent: QWidget | None, message: str) -> None:
    show_warning(
        parent,
        translate("dialog.config_ui.title"),
        message,
        message_box=QMessageBox,
    )
