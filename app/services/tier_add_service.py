from dataclasses import dataclass
from enum import Enum
from typing import Any


class TierAddStatus(Enum):
    MISSING_RESULT = "missing_result"
    EMPTY_TITLE = "empty_title"
    ADDED = "added"
    REJECTED = "rejected"


@dataclass(frozen=True)
class TierAddOutcome:
    status: TierAddStatus
    title: str = ""


def add_result_to_tier_board(
    tier_board,
    title: str,
    result: dict[str, Any] | None,
    cover_pixmap=None,
) -> TierAddOutcome:
    if result is None:
        return TierAddOutcome(status=TierAddStatus.MISSING_RESULT)

    cleaned_title = title.strip()
    if not cleaned_title:
        return TierAddOutcome(status=TierAddStatus.EMPTY_TITLE)

    was_added = tier_board.add_saved_entry(
        title=cleaned_title,
        score=result["display_score"],
        tier=result["tier"],
        cover_pixmap=cover_pixmap,
    )

    if was_added:
        return TierAddOutcome(status=TierAddStatus.ADDED, title=cleaned_title)

    return TierAddOutcome(status=TierAddStatus.REJECTED, title=cleaned_title)
