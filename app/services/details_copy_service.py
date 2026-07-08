from app.services.details_export_service import copy_details_to_clipboard
from app.widgets.copy_button_feedback import (
    COPY_DETAILS_DEFAULT_TEXT,
    COPY_DETAILS_SUCCESS_TEXT,
    show_temporary_copy_feedback,
)


def copy_details_with_feedback(
    *,
    profiles,
    profile_combos,
    weight_spins,
    mix_mode,
    mix_modes,
    states,
    tier_thresholds,
    title,
    copy_btn,
) -> None:
    copy_details_to_clipboard(
        profiles=profiles,
        profile_combos=profile_combos,
        weight_spins=weight_spins,
        mix_mode=mix_mode,
        mix_modes=mix_modes,
        states=states,
        tier_thresholds=tier_thresholds,
        title=title,
    )

    show_temporary_copy_feedback(
        copy_btn,
        COPY_DETAILS_SUCCESS_TEXT,
        COPY_DETAILS_DEFAULT_TEXT,
    )
