from app.services.clipboard_service import copy_text_to_clipboard
from app.presenters.details_export_presenter import build_export_text
from app.services.profile_mix_qt_adapter import read_profile_mix
from app.services.scoring_pipeline import (
    build_result_payload,
    build_scoring_input,
)


def copy_details_to_clipboard(
    *,
    profiles: dict,
    profile_combos,
    weight_spins,
    mix_mode: str,
    mix_modes: dict,
    states,
    tier_thresholds: dict,
    title: str,
) -> str:
    selected, ratios = read_profile_mix(
        profile_combos,
        weight_spins,
        mix_mode,
        mix_modes,
    )

    scoring_input = build_scoring_input(
        title=title.strip(),
        selected=selected,
        ratios=ratios,
        states=states,
    )
    result = build_result_payload(
        profiles=profiles,
        selected=selected,
        ratios=ratios,
        states=states,
        tier_thresholds=tier_thresholds,
        title=title.strip(),
    )
    text = build_export_text(scoring_input, result)

    copy_text_to_clipboard(text)
    return text
