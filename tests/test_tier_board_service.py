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
