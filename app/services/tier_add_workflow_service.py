from collections.abc import Callable
from PyQt6.QtWidgets import QWidget

from app.core.models import ScoringResult
from app.services.tier_add_outcome_service import handle_tier_add_outcome
from app.services.tier_add_service import (
    add_manual_card_to_tier_board,
    add_result_to_tier_board,
)


def add_current_result_to_tier_board(
    *,
    parent: QWidget | None,
    tier_board,
    title: str,
    latest_result: ScoringResult | None,
    recompute: Callable[[], None],
    get_latest_result: Callable[[], ScoringResult | None],
    cover_pixmap=None,
    input_snapshot=None,
    anilist_id: int | None = None,
) -> None:
    result = latest_result
    if result is None:
        recompute()
        result = get_latest_result()

    add_kwargs = dict(
        tier_board=tier_board,
        title=title,
        result=result,
        cover_pixmap=cover_pixmap,
    )
    if input_snapshot is not None:
        add_kwargs["input_snapshot"] = input_snapshot
        add_kwargs["anilist_id"] = anilist_id
    outcome = add_result_to_tier_board(**add_kwargs)
    handle_tier_add_outcome(parent, outcome)


def add_manual_card_to_tier_board_from_input(
    *,
    parent: QWidget | None,
    tier_board,
    title: str,
    cover_pixmap=None,
) -> None:
    outcome = add_manual_card_to_tier_board(
        tier_board=tier_board,
        title=title,
        cover_pixmap=cover_pixmap,
    )
    handle_tier_add_outcome(parent, outcome)
