from app.core.formatters import format_score
from app.core.models import ScoringInput, ScoringResult
from app.services.result_content_service import (
    DetailsExportContent,
    HUNGARIAN_RESULT_TEXT,
    ResultTextCatalog,
    build_details_export_content,
)


def build_export_text(
    scoring_input: ScoringInput,
    result: ScoringResult,
    *,
    text_catalog: ResultTextCatalog = HUNGARIAN_RESULT_TEXT,
) -> str:
    return render_export_text(
        build_details_export_content(scoring_input, result),
        text_catalog=text_catalog,
    )


def render_export_text(
    content: DetailsExportContent,
    *,
    text_catalog: ResultTextCatalog = HUNGARIAN_RESULT_TEXT,
) -> str:
    safe_title = content.title or text_catalog.missing_title
    profile_text = " + ".join(
        f"{profile.name} ({profile.percent}%)" for profile in content.profiles
    )
    lines = [
        f"{safe_title} — {format_score(content.score)}/10 "
        f"({text_catalog.tier_label}: {content.tier})",
        f"{text_catalog.profile_label}: {profile_text}",
        "",
    ]
    lines.extend(
        f"- {dimension.name}: {format_score(dimension.value)}"
        for dimension in content.dimensions
    )
    return "\n".join(lines)
