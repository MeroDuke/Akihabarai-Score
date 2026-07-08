from app.services.tier_preview_service import update_tier_preview_entry


class FakeTierBoard:
    def __init__(self):
        self.calls = []

    def update_current_entry(self, title, score, tier, cover_pixmap=None):
        self.calls.append(
            {
                "title": title,
                "score": score,
                "tier": tier,
                "cover_pixmap": cover_pixmap,
            }
        )


def _result():
    return {
        "display_score": 8.5,
        "tier": "A",
    }


def test_update_tier_preview_entry_updates_board_with_trimmed_title():
    board = FakeTierBoard()
    cover_pixmap = object()

    update_tier_preview_entry(
        tier_board=board,
        title="  Cowboy Bebop  ",
        result=_result(),
        cover_pixmap=cover_pixmap,
    )

    assert board.calls == [
        {
            "title": "Cowboy Bebop",
            "score": 8.5,
            "tier": "A",
            "cover_pixmap": cover_pixmap,
        }
    ]


def test_update_tier_preview_entry_uses_hungarian_fallback_for_blank_title():
    board = FakeTierBoard()

    update_tier_preview_entry(
        tier_board=board,
        title="   ",
        result=_result(),
    )

    assert board.calls[0]["title"] == "(nincs cím)"
