from dataclasses import dataclass
from enum import Enum
from typing import Callable

from PyQt6.QtWidgets import QApplication


class TierImageExportStatus(Enum):
    EMPTY = "empty"
    COPIED = "copied"
    FAILED = "failed"


@dataclass(frozen=True)
class TierImageExportOutcome:
    status: TierImageExportStatus
    error: Exception | None = None


def copy_tier_board_image_to_clipboard(
    tier_board,
    *,
    process_events: Callable[[], None] | None = None,
    clipboard_provider: Callable | None = None,
) -> TierImageExportOutcome:
    if tier_board.saved_entry_count() <= 0:
        return TierImageExportOutcome(status=TierImageExportStatus.EMPTY)

    if process_events is None:
        process_events = QApplication.processEvents

    if clipboard_provider is None:
        clipboard_provider = QApplication.clipboard

    tier_board.prepare_export_mode(True)
    process_events()

    try:
        clipboard_provider().setPixmap(tier_board.grab())
    except Exception as exc:
        return TierImageExportOutcome(
            status=TierImageExportStatus.FAILED,
            error=exc,
        )
    finally:
        tier_board.prepare_export_mode(False)

    return TierImageExportOutcome(status=TierImageExportStatus.COPIED)
