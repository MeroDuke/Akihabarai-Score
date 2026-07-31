from app.widgets.tier_preview_presenter import build_tier_preview_title


def test_tier_preview_title_uses_trimmed_title():
    assert build_tier_preview_title("  Cowboy Bebop  ") == "Cowboy Bebop"


def test_tier_preview_title_keeps_blank_title_as_stable_empty_data():
    assert build_tier_preview_title("") == ""
    assert build_tier_preview_title("   ") == ""
