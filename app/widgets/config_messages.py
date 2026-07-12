from PyQt6.QtWidgets import QMessageBox, QWidget


PROFILES_CONFIG_ERROR_TITLE = "Konfigurációs hiba"
UI_CONFIG_ERROR_TITLE = "Felületkonfigurációs hiba"


def show_profiles_config_error(parent: QWidget | None, message: str) -> None:
    QMessageBox.warning(parent, PROFILES_CONFIG_ERROR_TITLE, message)


def show_ui_config_error(parent: QWidget | None, message: str) -> None:
    QMessageBox.warning(parent, UI_CONFIG_ERROR_TITLE, message)
