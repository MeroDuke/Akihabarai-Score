from app.services.tier_add_service import (
    TierAddOutcome,
    TierAddStatus,
    add_manual_card_to_tier_board,
    add_result_to_tier_board,
)


class FakeTierBoard:
    def __init__(self, add_result=True):
        self.add_result = add_result
        self.calls = []

    def add_saved_entry(self, title, score, tier, cover_pixmap=None):
        self.calls.append(
            {
                "title": title,
                "score": score,
                "tier": tier,
                "cover_pixmap": cover_pixmap,
            }
        )
        return self.add_result

    def add_manual_entry(self, title, tier, cover_pixmap=None):
        self.calls.append(
            {
                "title": title,
                "tier": tier,
                "cover_pixmap": cover_pixmap,
                "manual": True,
            }
        )
        return self.add_result


def _result():
    return {
        "display_score": 8.5,
        "tier": "A",
    }


def test_add_result_to_tier_board_returns_missing_result_without_board_call():
    board = FakeTierBoard()

    outcome = add_result_to_tier_board(board, "Cowboy Bebop", None)

    assert outcome.status == TierAddStatus.MISSING_RESULT
    assert board.calls == []


def test_add_result_to_tier_board_returns_empty_title_without_board_call():
    board = FakeTierBoard()

    outcome = add_result_to_tier_board(board, "   ", _result())

    assert outcome.status == TierAddStatus.EMPTY_TITLE
    assert board.calls == []


def test_add_result_to_tier_board_adds_trimmed_title_and_cover():
    board = FakeTierBoard(add_result=True)
    cover_pixmap = object()

    outcome = add_result_to_tier_board(
        board,
        "  Cowboy Bebop  ",
        _result(),
        cover_pixmap=cover_pixmap,
    )

    assert outcome.status == TierAddStatus.ADDED
    assert outcome.title == "Cowboy Bebop"
    assert board.calls == [
        {
            "title": "Cowboy Bebop",
            "score": 8.5,
            "tier": "A",
            "cover_pixmap": cover_pixmap,
        }
    ]


def test_add_result_to_tier_board_returns_rejected_when_board_rejects_entry():
    board = FakeTierBoard(add_result=False)

    outcome = add_result_to_tier_board(board, "Cowboy Bebop", _result())

    assert outcome.status == TierAddStatus.REJECTED
    assert outcome.title == "Cowboy Bebop"
    assert len(board.calls) == 1


def test_add_manual_card_uses_c_tier_and_has_no_score():
    board = FakeTierBoard()
    cover_pixmap = object()

    outcome = add_manual_card_to_tier_board(
        board,
        "  Frieren  ",
        cover_pixmap=cover_pixmap,
    )

    assert outcome == TierAddOutcome(
        status=TierAddStatus.ADDED,
        title="Frieren",
    )
    assert board.calls == [
        {
            "title": "Frieren",
            "tier": "C",
            "cover_pixmap": cover_pixmap,
            "manual": True,
        }
    ]


def test_add_manual_card_rejects_empty_and_duplicate_titles():
    board = FakeTierBoard(add_result=False)

    empty_outcome = add_manual_card_to_tier_board(board, "   ")
    duplicate_outcome = add_manual_card_to_tier_board(board, "Frieren")

    assert empty_outcome.status == TierAddStatus.EMPTY_TITLE
    assert duplicate_outcome.status == TierAddStatus.REJECTED
    assert len(board.calls) == 1
