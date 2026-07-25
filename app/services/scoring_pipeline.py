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
            ScoredDimension(name=state.name, value=state.value)
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
    all_min_values = all(
        dimension.value == 1.0
        for dimension in scoring_input.dimensions
    )
    all_max_values = all(
        dimension.value == 10.0
        for dimension in scoring_input.dimensions
    )

    strengths = (
        ()
        if all_min_values
        else tuple(dimension for _, dimension in sorted_dimensions[:2])
    )
    weakness = (
        None
        if all_max_values
        else min(
            indexed_dimensions,
            key=lambda item: (item[1].value, -item[0]),
        )[1]
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
