from app.core.models import TierCardData, TierCardInputSnapshot
import app.services.tier_board_service as tier_board_service
from app.services.tier_board_service import TierBoardState


def test_board_starts_with_stable_empty_tier_rows():
    board = TierBoardState()
    assert tuple(board.cards_by_tier) == ("S", "A", "B", "C", "D", "E", "F")
    assert board.card_count() == 0
    assert not board.has_cards()
    assert "PyQt6" not in tier_board_service.__dict__


def test_scored_card_is_added_with_score_derived_metadata():
    board = TierBoardState()
    snapshot = TierCardInputSnapshot("1 profil", ["Balanced"], [100], [8.5])
    result = board.add_card(
        title="  Frieren  ",
        tier="A",
        card_type=TierCardData.TYPE_SCORED,
        score=8.5,
        anilist_id=154587,
        input_snapshot=snapshot,
    )
    assert result.changed
    assert result.card.title == "Frieren"
    assert result.card.score_tier == "A"
    assert board.cards_by_tier["A"] == [result.card]


def test_manual_card_is_scoreless_and_has_no_score_tier():
    board = TierBoardState()
    result = board.add_card(
        title="Manual",
        tier="C",
        card_type=TierCardData.TYPE_MANUAL,
    )
    assert result.changed
    assert result.card.score is None
    assert result.card.score_tier is None


def test_card_type_invariants_reject_invalid_score_combinations():
    board = TierBoardState()
    manual = board.add_card(
        title="Manual",
        tier="C",
        card_type=TierCardData.TYPE_MANUAL,
        score=5.0,
    )
    scored = board.add_card(
        title="Scored",
        tier="C",
        card_type=TierCardData.TYPE_SCORED,
    )
    assert manual.reason == "manual_card_has_score"
    assert scored.reason == "scored_card_missing_score"
    assert board.card_count() == 0


def test_duplicate_title_is_case_insensitive_and_released_after_delete():
    board = TierBoardState()
    first = board.add_card(
        title="Cowboy Bebop",
        tier="A",
        card_type=TierCardData.TYPE_SCORED,
        score=8.5,
    )
    duplicate = board.add_card(
        title="cowboy bebop",
        tier="B",
        card_type=TierCardData.TYPE_MANUAL,
    )
    assert duplicate.reason == "duplicate_title"
    assert board.remove_card(first.card.card_id).changed
    assert board.add_card(
        title="COWBOY BEBOP",
        tier="C",
        card_type=TierCardData.TYPE_MANUAL,
    ).changed


def test_invalid_title_tier_and_type_have_structured_reasons():
    board = TierBoardState()
    assert board.add_card(
        title=" ", tier="C", card_type=TierCardData.TYPE_MANUAL
    ).reason == "empty_title"
    assert board.add_card(
        title="Title", tier="Z", card_type=TierCardData.TYPE_MANUAL
    ).reason == "invalid_tier"
    assert board.add_card(
        title="Title", tier="C", card_type="other"
    ).reason == "invalid_card_type"


def test_scored_replacement_preserves_card_identity_and_rejects_manual_card():
    board = TierBoardState()
    scored = board.add_card(
        title="Before",
        tier="D",
        card_type=TierCardData.TYPE_SCORED,
        score=5.0,
    ).card
    manual = board.add_card(
        title="Manual",
        tier="C",
        card_type=TierCardData.TYPE_MANUAL,
    ).card
    updated = board.replace_scored_card(
        scored.card_id,
        title="After",
        score=9.0,
        tier="S",
        anilist_id=None,
        input_snapshot=None,
    )
    assert updated.changed
    assert updated.card.card_id == scored.card_id
    assert board.cards_by_tier["S"] == [updated.card]
    assert board.replace_scored_card(
        manual.card_id,
        title="No",
        score=1.0,
        tier="F",
        anilist_id=None,
        input_snapshot=None,
    ).reason == "manual_card_not_editable_as_scored"


def test_clear_returns_removed_count_and_resets_indexes():
    board = TierBoardState()
    for title in ("One", "Two"):
        board.add_card(title=title, tier="C", card_type=TierCardData.TYPE_MANUAL)
    result = board.clear()
    assert result.changed
    assert result.removed_count == 2
    assert board.card_count() == 0
    assert board.normalized_titles == set()
    assert board.clear().reason == "board_empty"


def test_move_card_requires_enabled_movement_and_valid_target():
    board = TierBoardState()
    card = board.add_card(
        title="Card", tier="C", card_type=TierCardData.TYPE_MANUAL
    ).card
    assert board.move_card(card.card_id, "A", movement_enabled=False).reason == (
        "movement_disabled"
    )
    assert board.move_card(card.card_id, "Z", movement_enabled=True).reason == (
        "invalid_tier"
    )
    assert board.cards_by_tier["C"] == [card]


def test_move_card_appends_cross_tier_and_updates_current_tier():
    board = TierBoardState()
    existing = board.add_card(
        title="Existing", tier="A", card_type=TierCardData.TYPE_MANUAL
    ).card
    moved = board.add_card(
        title="Moved", tier="C", card_type=TierCardData.TYPE_MANUAL
    ).card
    result = board.move_card(moved.card_id, "A", movement_enabled=True)
    assert result.changed
    assert result.action == "card_moved"
    assert result.target_index == 1
    assert board.cards_by_tier["A"] == [existing, moved]
    assert moved.current_tier == "A"


def test_move_card_reorders_within_tier_and_rejects_unchanged_position():
    board = TierBoardState()
    cards = [
        board.add_card(
            title=title, tier="C", card_type=TierCardData.TYPE_MANUAL
        ).card
        for title in ("First", "Second", "Third")
    ]
    assert board.move_card(
        cards[0].card_id, "C", movement_enabled=True
    ).reason == "position_unchanged"
    result = board.move_card(
        cards[2].card_id, "C", 0, movement_enabled=True
    )
    assert result.action == "card_reordered"
    assert board.cards_by_tier["C"] == [cards[2], cards[0], cards[1]]


def test_restore_scored_order_uses_scores_and_keeps_manual_tier():
    board = TierBoardState()
    manual = board.add_card(
        title="Manual", tier="A", card_type=TierCardData.TYPE_MANUAL
    ).card
    low = board.add_card(
        title="Low A", tier="F", card_type=TierCardData.TYPE_SCORED, score=8.1
    ).card
    high = board.add_card(
        title="High A", tier="C", card_type=TierCardData.TYPE_SCORED, score=8.8
    ).card
    summary = board.restore_scored_order(
        {"S": 9, "A": 8, "B": 7, "C": 6, "D": 5, "E": 4, "F": 0}
    )
    assert board.cards_by_tier["A"] == [high, low, manual]
    assert summary.scored_count == 2
    assert summary.manual_count == 1
    assert summary.moved_count == 2
