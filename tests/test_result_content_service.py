import app.services.result_content_service as content_service
from app.core.models import (
    ScoredDimension,
    ScoringInput,
    ScoringResult,
    ScoringSummary,
)
from app.presenters.details_export_presenter import render_export_text
from app.presenters.result_summary_presenter import render_result_summary_html
from app.services.result_content_service import (
    ResultTextCatalog,
    build_details_export_content,
    build_result_summary_content,
)
from app.services.localization_service import LocalizationService


def _result():
    scoring_input = ScoringInput(
        title="Example",
        selected_profiles=("Story", "Visual"),
        profile_ratios=(0.7, 0.3),
        dimensions=(
            ScoredDimension("Story", 8.0),
            ScoredDimension("Visual", 6.0),
        ),
    )
    return scoring_input, ScoringResult(
        input=scoring_input,
        score=7.4,
        display_score=7.4,
        tier="B",
        relevances=(1.0, 1.0),
        contributions=(4.0, 3.0),
        summary=ScoringSummary(
            strengths=(ScoredDimension("Story", 8.0),),
            weakness=ScoredDimension("Visual", 6.0),
        ),
    )


def test_content_models_are_qt_independent_structured_values():
    scoring_input, result = _result()
    summary = build_result_summary_content(result)
    details = build_details_export_content(scoring_input, result)
    assert summary.title == "Example"
    assert summary.strengths[0].name == "Story"
    assert details.profiles[0].percent == 70
    assert details.dimensions == scoring_input.dimensions
    assert "PyQt6" not in content_service.__dict__


def test_renderers_accept_alternative_text_catalog_without_recomputing():
    scoring_input, result = _result()
    catalog = ResultTextCatalog(
        strengths_label="Strengths",
        weakness_label="Weakness",
        profile_label="Profiles",
        tier_label="Rank",
        missing_title="Untitled",
        empty_value="None",
    )
    summary_html = render_result_summary_html(
        build_result_summary_content(result),
        {},
        text_catalog=catalog,
    )
    export_text = render_export_text(
        build_details_export_content(scoring_input, result),
        text_catalog=catalog,
    )
    assert "Strengths: Story (8)" in summary_html
    assert "Weakness: Visual (6)" in summary_html
    assert "Profiles: Story (70%) + Visual (30%)" in export_text
    assert "(Rank: B)" in export_text


def test_renderers_use_runtime_english_catalog_for_stable_ids():
    translator = LocalizationService(
        "config/locales",
        log_info_func=lambda *_: None,
        log_warning_func=lambda *_: None,
    )
    translator.switch_language("en", request_id="test", source="test")
    scoring_input = ScoringInput(
        title="Example",
        selected_profiles=("mystery",),
        profile_ratios=(1.0,),
        dimensions=(ScoredDimension("story_plot", 8.0),),
    )
    result = ScoringResult(
        input=scoring_input,
        score=8.0,
        display_score=8.0,
        tier="A",
        relevances=(1.0,),
        contributions=(8.0,),
        summary=ScoringSummary(
            strengths=(ScoredDimension("story_plot", 8.0),),
            weakness=ScoredDimension("story_plot", 8.0),
        ),
    )

    summary_html = render_result_summary_html(
        build_result_summary_content(result),
        {},
        text_catalog=content_service.build_result_text_catalog(
            translator.translate
        ),
        translate_func=translator.translate,
    )
    export_text = render_export_text(
        build_details_export_content(scoring_input, result),
        text_catalog=content_service.build_result_text_catalog(
            translator.translate
        ),
        translate_func=translator.translate,
    )

    assert "Strengths: Story / plot (8)" in summary_html
    assert "Weakness: Story / plot (8)" in summary_html
    assert "Profile: Mystery (100%)" in export_text
    assert "- Story / plot: 8" in export_text
