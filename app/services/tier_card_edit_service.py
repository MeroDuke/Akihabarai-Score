from __future__ import annotations

from app.core.models import TierCardInputSnapshot
from app.services.main_window_mode_service import APP_MODE_SCORED


def capture_tier_card_input_snapshot(window) -> TierCardInputSnapshot:
    return TierCardInputSnapshot(
        mix_mode=window.mix_combo.currentText(),
        profile_names=[combo.currentText() for combo in window.profile_combos],
        profile_weights=[spin.value() for spin in window.weight_spins],
        dimension_values=[state.value for state in window.states],
    )


def begin_tier_card_edit(window, entry, *, mix_modes) -> bool:
    snapshot = entry.card_data.input_snapshot
    if snapshot is None or entry.is_manual:
        return False

    if window.current_mode != APP_MODE_SCORED:
        window.current_mode = APP_MODE_SCORED
        window.apply_app_mode()

    window._building = True
    try:
        mix_index = window.mix_combo.findText(snapshot.mix_mode)
        if mix_index >= 0:
            window.mix_combo.setCurrentIndex(mix_index)
        window.current_mix_needed = mix_modes.get(
            window.mix_combo.currentText(), len(snapshot.profile_names)
        )
        window._update_profile_combo_options_internal()
        for combo, profile_name in zip(window.profile_combos, snapshot.profile_names):
            profile_index = combo.findText(profile_name)
            if profile_index >= 0:
                combo.setCurrentIndex(profile_index)
        for spin, weight in zip(window.weight_spins, snapshot.profile_weights):
            spin.setValue(weight)
        for index, value in enumerate(snapshot.dimension_values):
            if index >= len(window.states):
                break
            window.states[index].value = value
            window.spin_widgets[index].setValue(value)
            window.slider_widgets[index].setValue(round(value * 10))
        window.title_edit.setText(entry.raw_title)
        window.selected_anime_result = None
        window.selected_cover_pixmap = entry.cover_pixmap
    finally:
        window._building = False

    window.editing_tier_entry = entry
    window.add_tier_btn.setText("Szerkesztés mentése")
    window.cancel_edit_btn.show()
    window.mode_btn.setEnabled(False)
    window.recompute()
    return True


def finish_tier_card_edit(window) -> None:
    window.editing_tier_entry = None
    window.tier_board.set_editing_entry(None)
    window.add_tier_btn.setText("Hozzáadás Tier listához")
    window.cancel_edit_btn.hide()
    window.mode_btn.setEnabled(True)


def save_tier_card_edit(window) -> bool:
    entry = getattr(window, "editing_tier_entry", None)
    result = getattr(window, "latest_result", None)
    if entry is None or result is None:
        return False
    updated = window.tier_board.update_saved_scored_entry(
        entry,
        title=window.title_edit.text(),
        score=result["display_score"],
        tier=result["tier"],
        cover_pixmap=window.selected_cover_pixmap,
        input_snapshot=capture_tier_card_input_snapshot(window),
        anilist_id=(
            window.selected_anime_result.anilist_id
            if window.selected_anime_result is not None
            else entry.card_data.anilist_id
        ),
    )
    if updated:
        finish_tier_card_edit(window)
    return updated
