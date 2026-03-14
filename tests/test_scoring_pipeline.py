from app.core.models import DimState
from app.services.scoring_pipeline import (
    build_result_payload,
    build_export_text,
)


def _sample_states():
    return [
        DimState("Történet", 8.0),
        DimState("Karakterek", 9.0),
        DimState("Világépítés", 7.5),
        DimState("Tempó", 6.5),
        DimState("Hangulat", 8.5),
        DimState("Zene", 7.0),
        DimState("Látvány", 9.5),
        DimState("Emocionális hatás", 8.0),
    ]


def _sample_profiles():
    return {
        "Fantasy": [1.0, 0.9, 0.8, 0.7, 0.8, 0.6, 0.8, 0.7],
        "Drama": [0.8, 1.0, 0.6, 0.7, 0.9, 0.6, 0.7, 1.0],
        "Action": [0.7, 0.7, 0.6, 0.9, 0.6, 0.6, 1.0, 0.6],
    }


def _sample_tiers():
    return {
        "S+": 9.5,
        "S": 9.0,
        "A": 8.0,
        "B": 7.0,
        "C": 6.0,
        "D": 5.0,
        "E": 4.0,
        "F": 0.0,
    }


def _sample_ui_cfg():
    return {
        "result_title": {
            "font_pt": 14,
            "bold": True,
            "color": "#444",
            "margin_bottom_px": 6,
            "gap_lines_after": 1,
        },
        "result_body": {
            "color": "#666",
        },
    }


def test_build_result_payload_returns_expected_keys():
    result = build_result_payload(
        profiles=_sample_profiles(),
        selected=["Fantasy", "Drama"],
        ratios=[0.6, 0.4],
        states=_sample_states(),
        tier_thresholds=_sample_tiers(),
        ui_cfg=_sample_ui_cfg(),
        title="Re:Zero S3",
    )

    assert set(result.keys()) == {
        "score",
        "display_score",
        "tier",
        "selected",
        "ratios",
        "values",
        "relevances",
        "contributions",
        "summary_html",
    }


def test_build_result_payload_contains_title_when_provided():
    result = build_result_payload(
        profiles=_sample_profiles(),
        selected=["Fantasy"],
        ratios=[1.0],
        states=_sample_states(),
        tier_thresholds=_sample_tiers(),
        ui_cfg=_sample_ui_cfg(),
        title="Re:Zero S3",
    )

    assert "Re:Zero S3" in result["summary_html"]


def test_build_result_payload_works_with_empty_title():
    result = build_result_payload(
        profiles=_sample_profiles(),
        selected=["Fantasy"],
        ratios=[1.0],
        states=_sample_states(),
        tier_thresholds=_sample_tiers(),
        ui_cfg=_sample_ui_cfg(),
        title="",
    )

    assert result["summary_html"]
    assert "Erősségek:" in result["summary_html"]
    assert "Gyengeség:" in result["summary_html"]


def test_build_result_payload_relevances_and_contributions_match_state_count():
    states = _sample_states()

    result = build_result_payload(
        profiles=_sample_profiles(),
        selected=["Fantasy", "Drama"],
        ratios=[0.5, 0.5],
        states=states,
        tier_thresholds=_sample_tiers(),
        ui_cfg=_sample_ui_cfg(),
        title="Test",
    )

    assert len(result["values"]) == len(states)
    assert len(result["relevances"]) == len(states)
    assert len(result["contributions"]) == len(states)


def test_build_result_payload_returns_valid_tier_and_numeric_scores():
    result = build_result_payload(
        profiles=_sample_profiles(),
        selected=["Fantasy"],
        ratios=[1.0],
        states=_sample_states(),
        tier_thresholds=_sample_tiers(),
        ui_cfg=_sample_ui_cfg(),
        title="Test",
    )

    assert isinstance(result["score"], float)
    assert isinstance(result["display_score"], float)
    assert result["tier"] in _sample_tiers()


def test_build_export_text_contains_title_profile_and_dimensions():
    text = build_export_text(
        profiles=_sample_profiles(),
        selected=["Fantasy", "Drama"],
        ratios=[0.6, 0.4],
        states=_sample_states(),
        tier_thresholds=_sample_tiers(),
        title="Re:Zero S3",
    )

    assert "Re:Zero S3" in text
    assert "Profil:" in text
    assert "Fantasy (60%)" in text
    assert "Drama (40%)" in text
    assert "- Történet:" in text
    assert "- Karakterek:" in text


def test_build_export_text_uses_missing_title_fallback():
    text = build_export_text(
        profiles=_sample_profiles(),
        selected=["Fantasy"],
        ratios=[1.0],
        states=_sample_states(),
        tier_thresholds=_sample_tiers(),
        title="",
    )

    assert "(nincs cím)" in text