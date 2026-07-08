from PyQt6.QtWidgets import QWidget

from app.logger import log_warning
from app.services.tier_add_service import TierAddOutcome, TierAddStatus
from app.widgets.tier_messages import (
    show_duplicate_tier_title_information,
    show_missing_tier_title_warning,
)


def handle_tier_add_outcome(
    parent: QWidget | None,
    outcome: TierAddOutcome,
) -> None:
    if outcome.status == TierAddStatus.MISSING_RESULT:
        log_warning("tier_board", "add_entry_aborted: missing latest_result")
        return

    if outcome.status == TierAddStatus.EMPTY_TITLE:
        log_warning("tier_board", "add_entry_rejected: empty_title")
        show_missing_tier_title_warning(parent)
        return

    if outcome.status == TierAddStatus.REJECTED:
        log_warning(
            "tier_board",
            f"add_entry_rejected: duplicate_or_invalid title='{outcome.title}'",
        )
        show_duplicate_tier_title_information(parent)
