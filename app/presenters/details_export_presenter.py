from app.core.formatters import format_score
from app.core.models import ScoringInput, ScoringResult
from app.services.result_content_service import (
    DetailsExportContent,
    HUNGARIAN_RESULT_TEXT,
    ResultTextCatalog,
    build_details_export_content,
    build_result_text_catalog,
)
from app.services.localization_service import translate


def _localized_name(prefix: str, identifier: str, fallback: str, translate_func) -> str:
    key = f"{prefix}.{identifier}"
    translated = translate_func(key)
    return fallback if translated == key else translated


def build_export_text(
    scoring_input: ScoringInput,
    result: ScoringResult,
    *,
    text_catalog: ResultTextCatalog | None = None,
    translate_func=translate,
) -> str:
    if text_catalog is None:
        text_catalog = build_result_text_catalog(translate_func)
    return render_export_text(
        build_details_export_content(scoring_input, result),
        text_catalog=text_catalog,
        translate_func=translate_func,
    )


def render_export_text(
    content: DetailsExportContent,
    *,
    text_catalog: ResultTextCatalog = HUNGARIAN_RESULT_TEXT,
    translate_func=translate,
) -> str:
    safe_title = content.title or text_catalog.missing_title
    profile_text = " + ".join(
        f"{_localized_name('profile', profile.name, profile.name, translate_func)} "
        f"({profile.percent}%)"
        for profile in content.profiles
    )
    lines = [
        f"{safe_title} — {format_score(content.score)}/10 "
        f"({text_catalog.tier_label}: {content.tier})",
        f"{text_catalog.profile_label}: {profile_text}",
        "",
    ]
    lines.extend(
        f"- {_localized_name('dimension', dimension.name, dimension.display_name, translate_func)}: "
        f"{format_score(dimension.value)}"
        for dimension in content.dimensions
    )
    return "\n".join(lines)
