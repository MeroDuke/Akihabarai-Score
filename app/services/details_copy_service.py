from app.services.details_export_service import copy_details_to_clipboard
from app.widgets.copy_button_feedback import (
    show_localized_copy_feedback,
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
    log_info("clipboard", "copy_details_started")
    try:
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
    except Exception as exc:
        log_error("clipboard", f"copy_details_failed: {type(exc).__name__}")
        raise

    show_localized_copy_feedback(
        copy_btn,
        "copy.details.success",
        "copy.details.action",
    )
    log_info("clipboard", "copy_details_completed")
from app.logger import log_error, log_info
