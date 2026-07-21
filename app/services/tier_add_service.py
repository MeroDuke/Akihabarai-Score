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


DEFAULT_FREEHAND_TIER = "C"


def add_result_to_tier_board(
    tier_board,
    title: str,
    result: dict[str, Any] | None,
    cover_pixmap=None,
    input_snapshot=None,
    anilist_id: int | None = None,
) -> TierAddOutcome:
    if result is None:
        return TierAddOutcome(status=TierAddStatus.MISSING_RESULT)

    cleaned_title = title.strip()
    if not cleaned_title:
        return TierAddOutcome(status=TierAddStatus.EMPTY_TITLE)

    add_kwargs = dict(
        title=cleaned_title,
        score=result["display_score"],
        tier=result["tier"],
        cover_pixmap=cover_pixmap,
    )
    if input_snapshot is not None:
        add_kwargs["input_snapshot"] = input_snapshot
        add_kwargs["anilist_id"] = anilist_id
    was_added = tier_board.add_saved_entry(**add_kwargs)

    if was_added:
        return TierAddOutcome(status=TierAddStatus.ADDED, title=cleaned_title)

    return TierAddOutcome(status=TierAddStatus.REJECTED, title=cleaned_title)


def add_manual_card_to_tier_board(
    tier_board,
    title: str,
    cover_pixmap=None,
    tier: str = DEFAULT_FREEHAND_TIER,
) -> TierAddOutcome:
    cleaned_title = title.strip()
    if not cleaned_title:
        return TierAddOutcome(status=TierAddStatus.EMPTY_TITLE)

    was_added = tier_board.add_manual_entry(
        title=cleaned_title,
        tier=tier,
        cover_pixmap=cover_pixmap,
    )
    if was_added:
        return TierAddOutcome(status=TierAddStatus.ADDED, title=cleaned_title)

    return TierAddOutcome(status=TierAddStatus.REJECTED, title=cleaned_title)
