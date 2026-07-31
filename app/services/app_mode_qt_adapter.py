from collections.abc import Callable

from app.services.app_mode_service import (
    APP_MODE_FREEHAND,
    APP_MODE_SCORED,
    AppModeCapabilities,
    ScoredEditorSnapshot,
)
from app.services.localization_service import translate


MODE_BUTTON_TEXTS = {
    APP_MODE_SCORED: translate("app_mode.scored.label"),
    APP_MODE_FREEHAND: translate("app_mode.freehand.label"),
}

MODE_BUTTON_TOOLTIPS = {
    APP_MODE_SCORED: translate("app_mode.scored.switch_tooltip"),
    APP_MODE_FREEHAND: translate("app_mode.freehand.switch_tooltip"),
}


def capture_scored_editor(window) -> ScoredEditorSnapshot:
    return ScoredEditorSnapshot(
        title=window.title_edit.text(),
        title_input_mode=window.title_input_mode,
        selected_anime_result=window.selected_anime_result,
        selected_cover_image=window.selected_cover_pixmap,
    )


def restore_scored_editor(
    window,
    snapshot: ScoredEditorSnapshot | None,
) -> bool:
    if snapshot is None:
        return False

    window.title_input_mode = snapshot.title_input_mode
    previous_block_state = window.title_edit.blockSignals(True)
    window.title_edit.setText(snapshot.title)
    window.title_edit.blockSignals(previous_block_state)
    window.selected_anime_result = snapshot.selected_anime_result
    window.selected_cover_pixmap = snapshot.selected_cover_image
    window._sync_title_mode_ui(
        log_change=False,
        refresh_results_on_enable=False,
    )
    return True


def apply_app_mode_to_window(
    window,
    *,
    capabilities: AppModeCapabilities,
    log_debug_func: Callable[[str, str], None],
) -> None:
    mode = window.app_mode_state.mode
    scoring_enabled = capabilities.scoring_enabled

    window.mode_btn.setText(translate(f"app_mode.{mode}.label"))
    window.mode_btn.setToolTip(
        translate(
            "app_mode.scored.switch_tooltip"
            if mode == APP_MODE_SCORED
            else "app_mode.freehand.switch_tooltip"
        )
    )
    window.mix_combo.setEnabled(scoring_enabled)
    window.profile_mix_panel.setEnabled(scoring_enabled)
    window.dimensions_panel.setEnabled(scoring_enabled)
    window.copy_img_btn.setEnabled(scoring_enabled)
    window.copy_btn.setEnabled(scoring_enabled)
    window.update_add_tier_button_state(window.title_edit.text())
    window.result_panel.setVisible(scoring_enabled)
    window.tier_panel.set_flip_enabled(scoring_enabled)
    window.tier_board.set_score_display_enabled(scoring_enabled)
    window.tier_board.set_drag_enabled(capabilities.drag_enabled)
    window.tier_board.set_preview_visible(True)
    if not scoring_enabled:
        window.tier_board.update_manual_preview(
            window.title_edit.text(),
            cover_pixmap=window.selected_cover_pixmap,
        )

    fronted_card_count = (
        0 if scoring_enabled else window.tier_board.show_all_front_sides()
    )
    for index, stretch in enumerate(capabilities.layout_stretches):
        window.main_layout.setStretch(index, stretch)
    window.tier_board.schedule_reflow()

    log_debug_func(
        "ui",
        "app_mode_ui_applied: "
        f"mode='{mode}' "
        f"mix_combo={window.mix_combo.isEnabled()} "
        f"profile_mix={window.profile_mix_panel.isEnabled()} "
        f"dimensions={window.dimensions_panel.isEnabled()} "
        f"add_tier={window.add_tier_btn.isEnabled()} "
        f"copy_result={window.copy_img_btn.isEnabled()} "
        f"copy_details={window.copy_btn.isEnabled()} "
        f"result_panel_visible={not window.result_panel.isHidden()} "
        f"layout_stretches={capabilities.layout_stretches} "
        f"tier_flip={window.flip_all_tier_cards_btn.isEnabled()} "
        f"tier_cards_fronted={fronted_card_count} "
        f"tier_preview_visible={window.tier_board.has_visible_preview()} "
        f"tier_score_visible={window.tier_board.score_display_enabled}",
    )
