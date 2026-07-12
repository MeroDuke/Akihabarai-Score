from app.widgets.tier_preview_presenter import build_tier_preview_title


def test_tier_preview_title_uses_trimmed_title():
    assert build_tier_preview_title("  Cowboy Bebop  ") == "Cowboy Bebop"


def test_tier_preview_title_uses_hungarian_fallback_for_blank_title():
    assert build_tier_preview_title("") == "(nincs cím)"
    assert build_tier_preview_title("   ") == "(nincs cím)"
