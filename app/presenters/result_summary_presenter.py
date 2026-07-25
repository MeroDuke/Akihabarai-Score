import html

from app.core.formatters import format_score
from app.core.models import ScoringResult


def build_result_summary_html(
    result: ScoringResult,
    ui_cfg: dict,
) -> str:
    strengths_text = (
        ", ".join(
            f"{dimension.name} ({format_score(dimension.value)})"
            for dimension in result.summary.strengths
        )
        or "—"
    )
    weakness = result.summary.weakness
    weakness_text = (
        f"{weakness.name} ({format_score(weakness.value)})"
        if weakness is not None
        else "—"
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
    gap_html = "<br>" * max(
        0,
        int(title_config.get("gap_lines_after", 1)),
    )
    title_html = ""
    if result.input.title:
        title_html = (
            f'<div style="{title_css}">{html.escape(result.input.title)}</div>'
            f"{gap_html}"
        )

    return (
        f'<div style="{body_css}">'
        f"{title_html}"
        f"Erősségek: {html.escape(strengths_text)}<br>"
        f"Gyengeség: {html.escape(weakness_text)}"
        f"</div>"
    )
