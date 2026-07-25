from PyQt6.QtWidgets import QMessageBox, QWidget
from app.adapters.qt_desktop_adapter import (
    show_critical,
    show_information,
    show_warning,
)
from app.services.localization_service import translate


MISSING_TIER_TITLE_DIALOG_TITLE = translate("dialog.tier_missing.title")
MISSING_TIER_TITLE_DIALOG_TEXT = translate("dialog.tier_missing.message")
DUPLICATE_TIER_TITLE_DIALOG_TITLE = translate("dialog.tier_duplicate.title")
DUPLICATE_TIER_TITLE_DIALOG_TEXT = translate("dialog.tier_duplicate.message")
TIER_IMAGE_COPY_ERROR_DIALOG_TITLE = translate("dialog.tier_copy_error.title")
TIER_IMAGE_COPY_ERROR_DIALOG_TEXT = translate("dialog.tier_copy_error.message")


def show_missing_tier_title_warning(parent: QWidget | None) -> None:
    show_warning(
        parent,
        MISSING_TIER_TITLE_DIALOG_TITLE,
        MISSING_TIER_TITLE_DIALOG_TEXT,
        message_box=QMessageBox,
    )


def show_duplicate_tier_title_information(parent: QWidget | None) -> None:
    show_information(
        parent,
        DUPLICATE_TIER_TITLE_DIALOG_TITLE,
        DUPLICATE_TIER_TITLE_DIALOG_TEXT,
        message_box=QMessageBox,
    )


def show_tier_image_copy_error(parent: QWidget | None) -> None:
    show_critical(
        parent,
        TIER_IMAGE_COPY_ERROR_DIALOG_TITLE,
        TIER_IMAGE_COPY_ERROR_DIALOG_TEXT,
        message_box=QMessageBox,
    )
