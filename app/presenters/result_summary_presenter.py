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


def _rank_group_text(dimensions, text_catalog, translate_func) -> str:
    if len(dimensions) > 2:
        return text_catalog.tied_dimensions_template.format(
            score=format_score(dimensions[0].value),
            count=len(dimensions),
        )
    return ", ".join(
        f"{_dimension_label(dimension, translate_func)} "
        f"({format_score(dimension.value)})"
        for dimension in dimensions
    )


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
    if content.equal_score is not None:
        summary_html = html.escape(
            text_catalog.equal_scores_template.format(
                score=format_score(content.equal_score)
            )
        )
    else:
        highest_text = _rank_group_text(
            content.highest_dimensions,
            text_catalog,
            translate_func,
        )
        lowest_text = _rank_group_text(
            content.lowest_dimensions,
            text_catalog,
            translate_func,
        )
        summary_html = (
            f"{html.escape(text_catalog.highest_score_label)}: "
            f"{html.escape(highest_text)}<br>"
            f"{html.escape(text_catalog.lowest_score_label)}: "
            f"{html.escape(lowest_text)}"
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
    gap_html = "<br>" * max(0, int(title_config.get("gap_lines_after", 1)))
    title_html = ""
    if content.title:
        title_html = (
            f'<div style="{title_css}">{html.escape(content.title)}</div>'
            f"{gap_html}"
        )

    return (
        f'<div style="{body_css}">'
        f"{title_html}"
        f"{summary_html}"
        f"</div>"
    )
