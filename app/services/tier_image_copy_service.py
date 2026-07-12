from PyQt6.QtWidgets import QWidget

from app.logger import log_info
from app.services.tier_image_export_outcome_service import (
    handle_tier_image_export_outcome,
)
from app.services.tier_image_export_service import copy_tier_board_image_to_clipboard


def copy_tier_image_with_feedback(
    *,
    parent: QWidget | None,
    tier_board,
    copy_tier_btn,
    update_tier_buttons_state,
) -> None:
    if tier_board.saved_entry_count() <= 0:
        log_info("tier_board", "export_skipped: count=0")
        update_tier_buttons_state()
        return

    log_info("tier_board", "export_started: copy_tier_board_as_image")

    outcome = copy_tier_board_image_to_clipboard(tier_board)
    handle_tier_image_export_outcome(
        parent=parent,
        copy_tier_btn=copy_tier_btn,
        update_tier_buttons_state=update_tier_buttons_state,
        outcome=outcome,
    )
