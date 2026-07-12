from app.services.clipboard_service import copy_text_to_clipboard
from app.services.profile_mix_service import get_selected_profiles_and_ratios
from app.services.scoring_pipeline import build_export_text


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
    selected, ratios = get_selected_profiles_and_ratios(
        profile_combos,
        weight_spins,
        mix_mode,
        mix_modes,
    )

    text = build_export_text(
        profiles=profiles,
        selected=selected,
        ratios=ratios,
        states=states,
        tier_thresholds=tier_thresholds,
        title=title.strip(),
    )

    copy_text_to_clipboard(text)
    return text
