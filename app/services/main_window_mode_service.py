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

SCORED_LAYOUT_STRETCHES = (4, 2, 3)
FREEHAND_LAYOUT_STRETCHES = (4, 0, 5)


def apply_app_mode_for_window(
    window,
    *,
    log_debug_func: Callable[[str, str], None],
) -> None:
    scoring_enabled = window.current_mode == APP_MODE_SCORED

    window.mode_btn.setText(MODE_BUTTON_TEXTS[window.current_mode])
    window.mode_btn.setToolTip(MODE_BUTTON_TOOLTIPS[window.current_mode])
    window.mix_combo.setEnabled(scoring_enabled)
    window.profile_mix_panel.setEnabled(scoring_enabled)
    window.dimensions_panel.setEnabled(scoring_enabled)
    window.update_add_tier_button_state(window.title_edit.text())
    window.result_panel.setVisible(scoring_enabled)
    window.tier_panel.set_flip_enabled(scoring_enabled)
    fronted_card_count = 0
    if not scoring_enabled:
        fronted_card_count = window.tier_board.show_all_front_sides()

    layout_stretches = (
        SCORED_LAYOUT_STRETCHES if scoring_enabled else FREEHAND_LAYOUT_STRETCHES
    )
    for index, stretch in enumerate(layout_stretches):
        window.main_layout.setStretch(index, stretch)

    log_debug_func(
        "ui",
        "app_mode_ui_applied: "
        f"mode='{window.current_mode}' "
        f"mix_combo={window.mix_combo.isEnabled()} "
        f"profile_mix={window.profile_mix_panel.isEnabled()} "
        f"dimensions={window.dimensions_panel.isEnabled()} "
        f"add_tier={window.add_tier_btn.isEnabled()} "
        f"result_panel_visible={not window.result_panel.isHidden()} "
        f"layout_stretches={layout_stretches} "
        f"tier_flip={window.flip_all_tier_cards_btn.isEnabled()} "
        f"tier_cards_fronted={fronted_card_count}",
    )


def toggle_app_mode_for_window(
    window,
    *,
    log_info_func: Callable[[str, str], None],
    log_debug_func: Callable[[str, str], None],
) -> None:
    log_info_func("ui", "button_click: toggle_app_mode")
    window.current_mode = (
        APP_MODE_FREEHAND
        if window.current_mode == APP_MODE_SCORED
        else APP_MODE_SCORED
    )
    apply_app_mode_for_window(window, log_debug_func=log_debug_func)
    log_info_func("ui", f"app_mode_changed: mode='{window.current_mode}'")
