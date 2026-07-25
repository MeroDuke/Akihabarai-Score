from PyQt6.QtWidgets import QMessageBox, QWidget
from app.adapters.qt_desktop_adapter import (
    show_critical,
    show_information,
    show_warning,
)


MISSING_TIER_TITLE_DIALOG_TITLE = "Hiányzó cím"
MISSING_TIER_TITLE_DIALOG_TEXT = (
    "Tier listához csak megadott címmel lehet elemet hozzáadni."
)
DUPLICATE_TIER_TITLE_DIALOG_TITLE = "Már szerepel"
DUPLICATE_TIER_TITLE_DIALOG_TEXT = "Ez a cím már szerepel a Tier listában."
TIER_IMAGE_COPY_ERROR_DIALOG_TITLE = "Másolási hiba"
TIER_IMAGE_COPY_ERROR_DIALOG_TEXT = (
    "Nem sikerült a Tier listát képként vágólapra másolni."
)


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
