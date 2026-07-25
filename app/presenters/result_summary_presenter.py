import html

from app.core.formatters import format_score
from app.core.models import ScoringResult
from app.services.result_content_service import (
    HUNGARIAN_RESULT_TEXT,
    ResultSummaryContent,
    ResultTextCatalog,
    build_result_summary_content,
)


def build_result_summary_html(
    result: ScoringResult,
    ui_cfg: dict,
    *,
    text_catalog: ResultTextCatalog = HUNGARIAN_RESULT_TEXT,
) -> str:
    return render_result_summary_html(
        build_result_summary_content(result),
        ui_cfg,
        text_catalog=text_catalog,
    )


def render_result_summary_html(
    content: ResultSummaryContent,
    ui_cfg: dict,
    *,
    text_catalog: ResultTextCatalog = HUNGARIAN_RESULT_TEXT,
) -> str:
    strengths_text = (
        ", ".join(
            f"{dimension.name} ({format_score(dimension.value)})"
            for dimension in content.strengths
        )
        or text_catalog.empty_value
    )
    weakness_text = (
        f"{content.weakness.name} ({format_score(content.weakness.value)})"
        if content.weakness is not None
        else text_catalog.empty_value
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
        f"{html.escape(text_catalog.strengths_label)}: "
        f"{html.escape(strengths_text)}<br>"
        f"{html.escape(text_catalog.weakness_label)}: "
        f"{html.escape(weakness_text)}"
        f"</div>"
    )
