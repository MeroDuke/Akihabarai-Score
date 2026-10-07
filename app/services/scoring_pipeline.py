from statistics import fmean

from app.core.models import (
    ScoredDimension,
    ScoringInput,
    ScoringResult,
    ScoringSummary,
)
from app.scoring import (
    compute_score,
    display_score_consistent,
    mixed_relevances,
    tier_from_score,
)


SUMMARY_DEVIATION_THRESHOLD = 0.5


def build_scoring_input(
    *,
    title: str,
    selected: list[str],
    ratios: list[float],
    states,
) -> ScoringInput:
    return ScoringInput(
        title=title,
        selected_profiles=tuple(selected),
        profile_ratios=tuple(ratios),
        dimensions=tuple(
            ScoredDimension(
                name=state.name,
                value=state.value,
                label=getattr(state, "label", None),
            )
            for state in states
        ),
    )


def calculate_scoring_result(
    *,
    profiles: dict,
    scoring_input: ScoringInput,
    tier_thresholds: dict,
) -> ScoringResult:
    relevances = mixed_relevances(
        profiles,
        list(scoring_input.selected_profiles),
        list(scoring_input.profile_ratios),
    )
    values = [dimension.value for dimension in scoring_input.dimensions]
    score, used_relevances, contributions = compute_score(values, relevances)
    tier = tier_from_score(round(score, 3), tier_thresholds)
    display_score = display_score_consistent(score, tier, tier_thresholds)

    indexed_dimensions = list(enumerate(scoring_input.dimensions))
    sorted_dimensions = sorted(
        indexed_dimensions,
        key=lambda item: item[1].value,
        reverse=True,
    )
    average_value = fmean(values) if values else 0.0
    strengths = tuple(
        dimension
        for _, dimension in sorted_dimensions
        if dimension.value - average_value >= SUMMARY_DEVIATION_THRESHOLD
    )[:2]
    weakness_candidates = [
        item
        for item in indexed_dimensions
        if average_value - item[1].value >= SUMMARY_DEVIATION_THRESHOLD
    ]
    weakness = (
        min(
            weakness_candidates,
            key=lambda item: (item[1].value, -item[0]),
        )[1]
        if weakness_candidates
        else None
    )

    return ScoringResult(
        score=score,
        display_score=display_score,
        tier=tier,
        input=scoring_input,
        relevances=tuple(used_relevances),
        contributions=tuple(contributions),
        summary=ScoringSummary(
            strengths=strengths,
            weakness=weakness,
        ),
    )


def build_result_payload(
    *,
    profiles: dict,
    selected: list[str],
    ratios: list[float],
    states,
    tier_thresholds: dict,
    title: str,
) -> ScoringResult:
    return calculate_scoring_result(
        profiles=profiles,
        scoring_input=build_scoring_input(
            title=title,
            selected=selected,
            ratios=ratios,
            states=states,
        ),
        tier_thresholds=tier_thresholds,
    )
