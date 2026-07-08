from app.widgets.tier_preview_presenter import build_tier_preview_title


def update_tier_preview_entry(
    tier_board,
    title: str,
    result: dict,
    cover_pixmap=None,
) -> None:
    tier_board.update_current_entry(
        title=build_tier_preview_title(title),
        score=result["display_score"],
        tier=result["tier"],
        cover_pixmap=cover_pixmap,
    )
