from app.core.models import TierCardData, TierCardInputSnapshot
from app.services.tier_card_edit_session_service import (
    TierCardEditSessionState,
    begin_tier_card_edit_session,
    can_save_tier_card_edit,
    finish_tier_card_edit_session,
)


def _card(*, manual=False, snapshot=True):
    return TierCardData.create(
        title="Editable",
        current_tier="B",
        card_type=TierCardData.TYPE_MANUAL if manual else TierCardData.TYPE_SCORED,
        score=None if manual else 7.5,
        score_tier=None if manual else "B",
        input_snapshot=(
            TierCardInputSnapshot("1 profil", ["Balanced"], [100], [7.5])
            if snapshot
            else None
        ),
    )


def test_begin_preserves_independent_original_card_state():
    card = _card()
    transition = begin_tier_card_edit_session(TierCardEditSessionState(), card)
    assert transition.changed
    assert transition.state.active.card_id == card.card_id
    assert transition.state.active.original_card == card
    card.title = "Changed outside session"
    card.input_snapshot.dimension_values[0] = 9.0
    assert transition.state.active.original_card.title == "Editable"
    assert transition.state.active.original_card.input_snapshot.dimension_values == [7.5]


def test_manual_or_snapshotless_card_cannot_start_session():
    state = TierCardEditSessionState()
    assert begin_tier_card_edit_session(state, _card(manual=True)).reason == (
        "manual_card_not_editable"
    )
    assert begin_tier_card_edit_session(state, _card(snapshot=False)).reason == (
        "missing_input_snapshot"
    )


def test_new_begin_replaces_previous_active_session():
    first = _card()
    second = _card()
    active = begin_tier_card_edit_session(TierCardEditSessionState(), first).state
    replaced = begin_tier_card_edit_session(active, second)
    assert replaced.changed
    assert replaced.state.active.card_id == second.card_id
    assert replaced.state.active.original_card.card_id == second.card_id


def test_save_is_allowed_only_for_active_card():
    card = _card()
    state = begin_tier_card_edit_session(TierCardEditSessionState(), card).state
    assert can_save_tier_card_edit(state, card.card_id)
    assert not can_save_tier_card_edit(state, "other")
    assert not can_save_tier_card_edit(TierCardEditSessionState(), card.card_id)


def test_finish_records_save_cancel_delete_and_clear_reasons():
    for reason in ("saved", "cancelled", "card_deleted", "board_cleared"):
        card = _card()
        state = begin_tier_card_edit_session(TierCardEditSessionState(), card).state
        finished = finish_tier_card_edit_session(
            state, reason=reason, card_id=card.card_id
        )
        assert finished.changed
        assert not finished.state.is_active
        assert finished.state.last_finish_reason == reason


def test_finish_ignores_missing_session_or_different_card():
    card = _card()
    empty = TierCardEditSessionState()
    assert finish_tier_card_edit_session(empty, reason="cancelled").reason == (
        "no_active_session"
    )
    active = begin_tier_card_edit_session(empty, card).state
    unchanged = finish_tier_card_edit_session(
        active, reason="card_deleted", card_id="other"
    )
    assert not unchanged.changed
    assert unchanged.reason == "different_card"
    assert unchanged.state is active
