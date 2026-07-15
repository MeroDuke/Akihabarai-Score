from collections.abc import Callable


APP_MODE_SCORED = "scored"
APP_MODE_FREEHAND = "freehand"
DEFAULT_APP_MODE = APP_MODE_SCORED

MODE_BUTTON_TEXTS = {
    APP_MODE_SCORED: "Adatvezérelt",
    APP_MODE_FREEHAND: "Szabadkezes",
}

MODE_BUTTON_TOOLTIPS = {
    APP_MODE_SCORED: "Váltás Szabadkezes módra",
    APP_MODE_FREEHAND: "Váltás Adatvezérelt módra",
}


def apply_app_mode_for_window(window) -> None:
    scoring_enabled = window.current_mode == APP_MODE_SCORED

    window.mode_btn.setText(MODE_BUTTON_TEXTS[window.current_mode])
    window.mode_btn.setToolTip(MODE_BUTTON_TOOLTIPS[window.current_mode])
    window.mix_combo.setEnabled(scoring_enabled)
    window.profile_mix_panel.setEnabled(scoring_enabled)
    window.dimensions_panel.setEnabled(scoring_enabled)
    window.update_add_tier_button_state(window.title_edit.text())


def toggle_app_mode_for_window(
    window,
    *,
    log_info_func: Callable[[str, str], None],
) -> None:
    log_info_func("ui", "button_click: toggle_app_mode")
    window.current_mode = (
        APP_MODE_FREEHAND
        if window.current_mode == APP_MODE_SCORED
        else APP_MODE_SCORED
    )
    apply_app_mode_for_window(window)
    log_info_func("ui", f"app_mode_changed: mode='{window.current_mode}'")
