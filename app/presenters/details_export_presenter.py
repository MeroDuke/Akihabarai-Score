from app.core.formatters import format_score
from app.core.models import ScoringInput, ScoringResult


def build_export_text(
    scoring_input: ScoringInput,
    result: ScoringResult,
) -> str:
    safe_title = scoring_input.title or "(nincs cím)"
    profile_text = " + ".join(
        f"{profile} ({int(round(ratio * 100))}%)"
        for profile, ratio in zip(
            scoring_input.selected_profiles,
            scoring_input.profile_ratios,
        )
    )
    lines = [
        f"{safe_title} — {format_score(result.score)}/10 (Tier: {result.tier})",
        f"Profil: {profile_text}",
        "",
    ]
    lines.extend(
        f"- {dimension.name}: {format_score(dimension.value)}"
        for dimension in scoring_input.dimensions
    )
    return "\n".join(lines)
