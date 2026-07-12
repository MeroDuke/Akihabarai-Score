from PyQt6.QtWidgets import QWidget

from app.logger import log_error, log_info
from app.services.tier_image_export_service import (
    TierImageExportOutcome,
    TierImageExportStatus,
)
from app.widgets.copy_button_feedback import (
    COPY_SUCCESS_TEXT,
    COPY_TIER_IMAGE_DEFAULT_TEXT,
    show_temporary_copy_feedback,
)
from app.widgets.tier_messages import show_tier_image_copy_error


def handle_tier_image_export_outcome(
    parent: QWidget | None,
    copy_tier_btn,
    update_tier_buttons_state,
    outcome: TierImageExportOutcome,
) -> None:
    if outcome.status == TierImageExportStatus.EMPTY:
        log_info("tier_board", "export_skipped: count=0")
        update_tier_buttons_state()
        return

    if outcome.status == TierImageExportStatus.FAILED:
        log_error("tier_board", f"export_failed: {outcome.error}")
        show_tier_image_copy_error(parent)
        return

    log_info("tier_board", "export_completed: copied_tier_board_to_clipboard")

    show_temporary_copy_feedback(
        copy_tier_btn,
        COPY_SUCCESS_TEXT,
        COPY_TIER_IMAGE_DEFAULT_TEXT,
    )
