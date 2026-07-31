from PyQt6.QtWidgets import QMessageBox, QWidget
from app.adapters.qt_desktop_adapter import (
    show_critical,
    show_information,
    show_warning,
)
from app.services.localization_service import translate


def show_missing_tier_title_warning(parent: QWidget | None) -> None:
    show_warning(
        parent,
        translate("dialog.tier_missing.title"),
        translate("dialog.tier_missing.message"),
        message_box=QMessageBox,
    )


def show_duplicate_tier_title_information(parent: QWidget | None) -> None:
    show_information(
        parent,
        translate("dialog.tier_duplicate.title"),
        translate("dialog.tier_duplicate.message"),
        message_box=QMessageBox,
    )


def show_tier_image_copy_error(parent: QWidget | None) -> None:
    show_critical(
        parent,
        translate("dialog.tier_copy_error.title"),
        translate("dialog.tier_copy_error.message"),
        message_box=QMessageBox,
    )
