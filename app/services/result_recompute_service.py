from collections.abc import Callable
from typing import Any

from app.logger import log_debug
from app.services.profile_mix_service import get_selected_profiles_and_ratios
from app.services.tier_preview_service import update_tier_preview_entry


def recompute_result_and_update_views(
    *,
    profiles,
    profile_combos,
    weight_spins,
    mix_mode: str,
    mix_modes,
    states,
    tier_thresholds,
    ui_cfg,
    title: str,
    result_panel,
    tier_board,
    cover_pixmap=None,
    build_result_payload_func: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    selected, ratios = get_selected_profiles_and_ratios(
        profile_combos,
        weight_spins,
        mix_mode,
        mix_modes,
    )

    cleaned_title = title.strip()

    result = build_result_payload_func(
        profiles=profiles,
        selected=selected,
        ratios=ratios,
        states=states,
        tier_thresholds=tier_thresholds,
        ui_cfg=ui_cfg,
        title=cleaned_title,
    )

    log_debug(
        "recompute",
        f"title='{cleaned_title}' selected={result['selected']} ratios={result['ratios']} "
        f"vals={result['values']} score={result['score']:.4f} "
        f"tier={result['tier']} display={result['display_score']:.2f}",
    )

    result_panel.update_result(result, states)
    update_tier_preview_entry(
        tier_board=tier_board,
        title=title,
        result=result,
        cover_pixmap=cover_pixmap,
    )

    return result
