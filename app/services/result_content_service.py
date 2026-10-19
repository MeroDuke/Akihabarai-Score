"""UI-independent result and export content models."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.models import ScoredDimension, ScoringInput, ScoringResult
from app.services.localization_service import translate


@dataclass(frozen=True)
class ResultTextCatalog:
    highest_score_label: str = translate("result.highest_score")
    lowest_score_label: str = translate("result.lowest_score")
    tied_dimensions_template: str = translate("result.tied_dimensions")
    equal_scores_template: str = translate("result.equal_scores")
    profile_label: str = translate("result.profile")
    tier_label: str = translate("result.tier")
    missing_title: str = translate("result.missing_title")
    empty_value: str = translate("result.empty_value")


HUNGARIAN_RESULT_TEXT = ResultTextCatalog()


def build_result_text_catalog(translate_func=translate) -> ResultTextCatalog:
    return ResultTextCatalog(
        highest_score_label=translate_func("result.highest_score"),
        lowest_score_label=translate_func("result.lowest_score"),
        tied_dimensions_template=translate_func("result.tied_dimensions"),
        equal_scores_template=translate_func("result.equal_scores"),
        profile_label=translate_func("result.profile"),
        tier_label=translate_func("result.tier"),
        missing_title=translate_func("result.missing_title"),
        empty_value=translate_func("result.empty_value"),
    )


@dataclass(frozen=True)
class ResultSummaryContent:
    title: str
    highest_dimensions: tuple[ScoredDimension, ...]
    lowest_dimensions: tuple[ScoredDimension, ...]
    equal_score: float | None


@dataclass(frozen=True)
class ProfileShare:
    name: str
    percent: int


@dataclass(frozen=True)
class DetailsExportContent:
    title: str
    score: float
    tier: str
    profiles: tuple[ProfileShare, ...]
    dimensions: tuple[ScoredDimension, ...]


def build_result_summary_content(result: ScoringResult) -> ResultSummaryContent:
    dimensions = result.input.dimensions
    dimension_values = [dimension.value for dimension in dimensions]
    equal_score = (
        dimension_values[0]
        if dimension_values
        and all(value == dimension_values[0] for value in dimension_values)
        else None
    )
    highest_dimensions = (
        tuple(
            dimension
            for dimension in dimensions
            if dimension.value == max(dimension_values)
        )
        if dimension_values and equal_score is None
        else ()
    )
    lowest_dimensions = (
        tuple(
            dimension
            for dimension in dimensions
            if dimension.value == min(dimension_values)
        )
        if dimension_values and equal_score is None
        else ()
    )
    return ResultSummaryContent(
        title=result.input.title,
        highest_dimensions=highest_dimensions,
        lowest_dimensions=lowest_dimensions,
        equal_score=equal_score,
    )


def build_details_export_content(
    scoring_input: ScoringInput,
    result: ScoringResult,
) -> DetailsExportContent:
    return DetailsExportContent(
        title=scoring_input.title,
        score=result.score,
        tier=result.tier,
        profiles=tuple(
            ProfileShare(name, int(round(ratio * 100)))
            for name, ratio in zip(
                scoring_input.selected_profiles,
                scoring_input.profile_ratios,
            )
        ),
        dimensions=scoring_input.dimensions,
    )
