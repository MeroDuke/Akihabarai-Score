from collections.abc import Callable
from typing import Any

from PyQt6.QtWidgets import QWidget

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
    latest_result: dict[str, Any] | None,
    recompute: Callable[[], None],
    get_latest_result: Callable[[], dict[str, Any] | None],
    cover_pixmap=None,
) -> None:
    result = latest_result
    if result is None:
        recompute()
        result = get_latest_result()

    outcome = add_result_to_tier_board(
        tier_board=tier_board,
        title=title,
        result=result,
        cover_pixmap=cover_pixmap,
    )
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
