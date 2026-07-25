"""UI-independent lifecycle for editing one scored Tier Board card."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from app.core.models import TierCardData


@dataclass(frozen=True)
class TierCardEditSession:
    card_id: str
    original_card: TierCardData


@dataclass(frozen=True)
class TierCardEditSessionState:
    active: TierCardEditSession | None = None
    last_finish_reason: str | None = None

    @property
    def is_active(self) -> bool:
        return self.active is not None


@dataclass(frozen=True)
class TierCardEditTransition:
    state: TierCardEditSessionState
    changed: bool
    reason: str | None = None


def begin_tier_card_edit_session(
    state: TierCardEditSessionState,
    card: TierCardData,
) -> TierCardEditTransition:
    if card.card_type != TierCardData.TYPE_SCORED:
        return TierCardEditTransition(state, False, "manual_card_not_editable")
    if card.input_snapshot is None:
        return TierCardEditTransition(state, False, "missing_input_snapshot")

    session = TierCardEditSession(
        card_id=card.card_id,
        original_card=deepcopy(card),
    )
    return TierCardEditTransition(
        TierCardEditSessionState(active=session),
        True,
    )


def finish_tier_card_edit_session(
    state: TierCardEditSessionState,
    *,
    reason: str,
    card_id: str | None = None,
) -> TierCardEditTransition:
    if state.active is None:
        return TierCardEditTransition(state, False, "no_active_session")
    if card_id is not None and card_id != state.active.card_id:
        return TierCardEditTransition(state, False, "different_card")
    return TierCardEditTransition(
        TierCardEditSessionState(active=None, last_finish_reason=reason),
        True,
    )


def can_save_tier_card_edit(
    state: TierCardEditSessionState,
    card_id: str | None,
) -> bool:
    return (
        state.active is not None
        and card_id is not None
        and state.active.card_id == card_id
    )
