"""UI-independent result and export content models."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.models import ScoredDimension, ScoringInput, ScoringResult
from app.services.localization_service import translate


@dataclass(frozen=True)
class ResultTextCatalog:
    strengths_label: str = translate("result.strengths")
    weakness_label: str = translate("result.weakness")
    profile_label: str = translate("result.profile")
    tier_label: str = translate("result.tier")
    missing_title: str = translate("result.missing_title")
    empty_value: str = translate("result.empty_value")


HUNGARIAN_RESULT_TEXT = ResultTextCatalog()


@dataclass(frozen=True)
class ResultSummaryContent:
    title: str
    strengths: tuple[ScoredDimension, ...]
    weakness: ScoredDimension | None


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
    return ResultSummaryContent(
        title=result.input.title,
        strengths=result.summary.strengths,
        weakness=result.summary.weakness,
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
