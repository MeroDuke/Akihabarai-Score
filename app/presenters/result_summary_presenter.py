import html

from app.core.formatters import format_score
from app.core.models import ScoringResult
from app.services.result_content_service import (
    HUNGARIAN_RESULT_TEXT,
    ResultSummaryContent,
    ResultTextCatalog,
    build_result_summary_content,
    build_result_text_catalog,
)
from app.services.localization_service import translate


def _dimension_label(dimension, translate_func) -> str:
    key = f"dimension.{dimension.name}"
    translated = translate_func(key)
    return dimension.display_name if translated == key else translated


def build_result_summary_html(
    result: ScoringResult,
    ui_cfg: dict,
    *,
    text_catalog: ResultTextCatalog | None = None,
    translate_func=translate,
) -> str:
    if text_catalog is None:
        text_catalog = build_result_text_catalog(translate_func)
    return render_result_summary_html(
        build_result_summary_content(result),
        ui_cfg,
        text_catalog=text_catalog,
        translate_func=translate_func,
    )


def render_result_summary_html(
    content: ResultSummaryContent,
    ui_cfg: dict,
    *,
    text_catalog: ResultTextCatalog = HUNGARIAN_RESULT_TEXT,
    translate_func=translate,
) -> str:
    summary_rows = []
    if content.strengths:
        strengths_text = ", ".join(
            f"{_dimension_label(dimension, translate_func)} "
            f"({format_score(dimension.value)})"
            for dimension in content.strengths
        )
        summary_rows.append(
            f"{html.escape(text_catalog.strengths_label)}: "
            f"{html.escape(strengths_text)}"
        )
    if content.weakness is not None:
        weakness_text = (
            f"{_dimension_label(content.weakness, translate_func)} "
            f"({format_score(content.weakness.value)})"
        )
        summary_rows.append(
            f"{html.escape(text_catalog.weakness_label)}: "
            f"{html.escape(weakness_text)}"
        )

    title_config = ui_cfg.get("result_title", {})
    body_config = ui_cfg.get("result_body", {})
    title_css = (
        f"font-size: {int(title_config.get('font_pt', 14))}pt; "
        f"font-weight: {'700' if bool(title_config.get('bold', True)) else '400'}; "
        f"color: {str(title_config.get('color', '#444'))}; "
        f"margin-bottom: {int(title_config.get('margin_bottom_px', 6))}px;"
    )
    body_css = f"color: {str(body_config.get('color', '#666'))};"
    gap_html = (
        "<br>" * max(0, int(title_config.get("gap_lines_after", 1)))
        if summary_rows
        else ""
    )
    title_html = ""
    if content.title:
        title_html = (
            f'<div style="{title_css}">{html.escape(content.title)}</div>'
            f"{gap_html}"
        )

    if not title_html and not summary_rows:
        return ""

    summary_html = "<br>".join(summary_rows)
    return f'<div style="{body_css}">{title_html}{summary_html}</div>'
