from app.core.models import DimState, ScoringInput, ScoringResult
from app.presenters.details_export_presenter import build_export_text
from app.presenters.result_summary_presenter import build_result_summary_html
from app.services.scoring_pipeline import (
    build_result_payload,
    build_scoring_input,
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


def _states_with_value(value: float):
    return [
        DimState(name, value)
        for name in (
            "Történet",
            "Karakterek",
            "Világépítés",
            "Tempó",
            "Hangulat",
            "Zene",
            "Látvány",
            "Emocionális hatás",
        )
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
        "result_body": {"color": "#666"},
    }


def _result(*, states=None, title="Re:Zero S3"):
    return build_result_payload(
        profiles=_sample_profiles(),
        selected=["Fantasy", "Drama"],
        ratios=[0.6, 0.4],
        states=states or _sample_states(),
        tier_thresholds=_sample_tiers(),
        title=title,
    )


def test_build_scoring_input_returns_immutable_structured_snapshot():
    states = _sample_states()

    scoring_input = build_scoring_input(
        title="Re:Zero S3",
        selected=["Fantasy", "Drama"],
        ratios=[0.6, 0.4],
        states=states,
    )
    states[0].value = 1.0

    assert isinstance(scoring_input, ScoringInput)
    assert scoring_input.title == "Re:Zero S3"
    assert scoring_input.selected_profiles == ("Fantasy", "Drama")
    assert scoring_input.profile_ratios == (0.6, 0.4)
    assert scoring_input.dimensions[0].name == "Történet"
    assert scoring_input.dimensions[0].value == 8.0


def test_build_result_payload_returns_structured_result():
    result = _result()

    assert isinstance(result, ScoringResult)
    assert isinstance(result.score, float)
    assert isinstance(result.display_score, float)
    assert result.tier in _sample_tiers()
    assert result.selected == ["Fantasy", "Drama"]
    assert result.ratios == [0.6, 0.4]
    assert result.input.title == "Re:Zero S3"


def test_result_vectors_match_dimension_count():
    result = _result()

    assert len(result.values) == 8
    assert len(result.relevances) == 8
    assert len(result.contributions) == 8


def test_result_summary_contains_structured_strengths_and_weakness():
    result = _result()

    assert [
        (dimension.name, dimension.value)
        for dimension in result.summary.strengths
    ] == [("Látvány", 9.5), ("Karakterek", 9.0)]
    assert result.summary.weakness.name == "Tempó"
    assert result.summary.weakness.value == 6.5


def test_all_max_values_have_no_weakness():
    result = _result(states=_states_with_value(10.0))

    assert [item.name for item in result.summary.strengths] == [
        "Történet",
        "Karakterek",
    ]
    assert result.summary.weakness is None


def test_all_min_values_have_no_strengths_and_keep_last_tie_as_weakness():
    result = _result(states=_states_with_value(1.0))

    assert result.summary.strengths == ()
    assert result.summary.weakness.name == "Emocionális hatás"


def test_equal_middle_values_keep_stable_summary_order():
    result = _result(states=_states_with_value(5.0))

    assert [item.name for item in result.summary.strengths] == [
        "Történet",
        "Karakterek",
    ]
    assert result.summary.weakness.name == "Emocionális hatás"


def test_summary_presenter_keeps_existing_hungarian_output():
    result = _result(states=_states_with_value(5.0), title="Middle Test")

    html = build_result_summary_html(result, _sample_ui_cfg())

    assert "Middle Test" in html
    assert "Erősségek: Történet (5), Karakterek (5)" in html
    assert "Gyengeség: Emocionális hatás (5)" in html


def test_summary_presenter_escapes_title_and_dimension_names():
    states = _states_with_value(5.0)
    states[0].name = "<Story>"
    result = _result(states=states, title="<script>")

    html = build_result_summary_html(result, _sample_ui_cfg())

    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "&lt;Story&gt;" in html


def test_summary_presenter_works_with_empty_title():
    html = build_result_summary_html(
        _result(title=""),
        _sample_ui_cfg(),
    )

    assert "Erősségek:" in html
    assert "Gyengeség:" in html


def test_summary_presenter_preserves_all_max_and_min_messages():
    max_html = build_result_summary_html(
        _result(states=_states_with_value(10.0)),
        _sample_ui_cfg(),
    )
    min_html = build_result_summary_html(
        _result(states=_states_with_value(1.0)),
        _sample_ui_cfg(),
    )

    assert "Erősségek: Történet (10), Karakterek (10)" in max_html
    assert "Gyengeség: —" in max_html
    assert "Erősségek: —" in min_html
    assert "Gyengeség: Emocionális hatás (1)" in min_html


def test_export_presenter_keeps_existing_hungarian_output():
    result = _result()

    text = build_export_text(result.input, result)

    assert "Re:Zero S3" in text
    assert "Profil:" in text
    assert "Fantasy (60%)" in text
    assert "Drama (40%)" in text
    assert "- Történet: 8" in text


def test_export_presenter_uses_missing_title_fallback():
    result = _result(title="")

    assert "(nincs cím)" in build_export_text(result.input, result)
