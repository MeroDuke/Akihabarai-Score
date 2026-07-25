"""UI-independent result and export content models."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.models import ScoredDimension, ScoringInput, ScoringResult


@dataclass(frozen=True)
class ResultTextCatalog:
    strengths_label: str = "Erősségek"
    weakness_label: str = "Gyengeség"
    profile_label: str = "Profil"
    tier_label: str = "Tier"
    missing_title: str = "(nincs cím)"
    empty_value: str = "—"


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
