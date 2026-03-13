import html
from typing import List, Dict, Any

from app.scoring import (
    tier_from_score,
    mixed_relevances,
    compute_score,
    display_score_consistent,
)


def build_result_payload(
    *,
    profiles: dict,
    selected: List[str],
    ratios: List[float],
    states,
    tier_thresholds: dict,
    ui_cfg: dict,
    title: str,
) -> Dict[str, Any]:
    rel = mixed_relevances(profiles, selected, ratios)

    vals = [s.value for s in states]
    score, used_rel, contrib = compute_score(vals, rel)

    score_for_tier = round(score, 3)
    tier = tier_from_score(score_for_tier, tier_thresholds)

    display_score = display_score_consistent(
        score,
        tier,
        tier_thresholds,
    )

    values = [(i, states[i].value) for i in range(len(states))]
    values_sorted = sorted(values, key=lambda x: x[1], reverse=True)
    top2 = values_sorted[:2]
    low1 = values_sorted[-1]

    top_str = ", ".join([f"{states[i].name} ({v:.1f})" for i, v in top2])
    low_str = f"{states[low1[0]].name} ({low1[1]:.1f})"

    t = ui_cfg.get("result_title", {})
    b = ui_cfg.get("result_body", {})

    font_pt = int(t.get("font_pt", 14))
    bold = bool(t.get("bold", True))
    title_color = str(t.get("color", "#444"))
    margin_bottom = int(t.get("margin_bottom_px", 6))
    gap_lines = int(t.get("gap_lines_after", 1))
    body_color = str(b.get("color", "#666"))

    title_css = (
        f"font-size: {font_pt}pt; "
        f"font-weight: {'700' if bold else '400'}; "
        f"color: {title_color}; "
        f"margin-bottom: {margin_bottom}px;"
    )
    body_css = f"color: {body_color};"
    gap_html = "<br>" * max(0, gap_lines)

    if title:
        safe_title = html.escape(title)
        summary_html = (
            f'<div style="{body_css}">'
            f'<div style="{title_css}">{safe_title}</div>'
            f"{gap_html}"
            f"Erősségek: {html.escape(top_str)}<br>"
            f"Gyengeség: {html.escape(low_str)}"
            f"</div>"
        )
    else:
        summary_html = (
            f'<div style="{body_css}">'
            f"Erősségek: {html.escape(top_str)}<br>"
            f"Gyengeség: {html.escape(low_str)}"
            f"</div>"
        )

    return {
        "score": score,
        "display_score": display_score,
        "tier": tier,
        "selected": selected,
        "ratios": ratios,
        "values": vals,
        "relevances": used_rel,
        "contributions": contrib,
        "summary_html": summary_html,
    }