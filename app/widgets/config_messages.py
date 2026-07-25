from PyQt6.QtWidgets import QMessageBox, QWidget
from app.adapters.qt_desktop_adapter import show_warning


PROFILES_CONFIG_ERROR_TITLE = "Konfigurációs hiba"
UI_CONFIG_ERROR_TITLE = "Felületkonfigurációs hiba"


def show_profiles_config_error(parent: QWidget | None, message: str) -> None:
    show_warning(
        parent,
        PROFILES_CONFIG_ERROR_TITLE,
        message,
        message_box=QMessageBox,
    )


def show_ui_config_error(parent: QWidget | None, message: str) -> None:
    show_warning(
        parent,
        UI_CONFIG_ERROR_TITLE,
        message,
        message_box=QMessageBox,
    )
