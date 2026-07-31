from __future__ import annotations

from app.core.models import TierCardInputSnapshot
from app.logger import log_info, log_warning
from app.services.app_mode_service import APP_MODE_SCORED
from app.services.tier_card_edit_session_service import (
    TierCardEditSessionState,
    begin_tier_card_edit_session,
    can_save_tier_card_edit,
    finish_tier_card_edit_session,
)
from app.services.selection_id_service import current_identifier, find_identifier


def capture_tier_card_input_snapshot(window) -> TierCardInputSnapshot:
    return TierCardInputSnapshot(
        mix_mode=current_identifier(window.mix_combo),
        profile_names=[
            current_identifier(combo) for combo in window.profile_combos
        ],
        profile_weights=[spin.value() for spin in window.weight_spins],
        dimension_values=[state.value for state in window.states],
    )


def begin_tier_card_edit(window, entry, *, mix_modes) -> bool:
    snapshot = entry.card_data.input_snapshot
    current_state = getattr(
        window, "tier_card_edit_state", TierCardEditSessionState()
    )
    transition = begin_tier_card_edit_session(current_state, entry.card_data)
    if not transition.changed:
        log_warning(
            "tier_board",
            f"card_edit_rejected: reason='{transition.reason}'",
        )
        return False
    window.tier_card_edit_state = transition.state

    if window.current_mode != APP_MODE_SCORED:
        window.current_mode = APP_MODE_SCORED
        window.apply_app_mode()

    window._building = True
    try:
        mix_index = find_identifier(window.mix_combo, snapshot.mix_mode)
        if mix_index >= 0:
            window.mix_combo.setCurrentIndex(mix_index)
        window.current_mix_needed = mix_modes.get(
            current_identifier(window.mix_combo), len(snapshot.profile_names)
        )
        window._update_profile_combo_options_internal()
        for combo, profile_name in zip(window.profile_combos, snapshot.profile_names):
            profile_index = find_identifier(combo, profile_name)
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
    log_info(
        "tier_board",
        f"card_edit_started: card_id='{entry.card_data.card_id}'",
    )
    return True


def finish_tier_card_edit(
    window,
    *,
    reason: str | None = None,
    card_id: str | None = None,
) -> None:
    entry = getattr(window, "editing_tier_entry", None)
    if reason is None:
        saved_entries = (
            entry_item
            for entries in window.tier_board.saved_entries_by_tier.values()
            for entry_item in entries
        )
        reason = (
            "card_deleted"
            if entry is not None and entry not in saved_entries
            else "cancelled"
        )
    current_state = getattr(
        window, "tier_card_edit_state", TierCardEditSessionState()
    )
    transition = finish_tier_card_edit_session(
        current_state,
        reason=reason,
        card_id=card_id,
    )
    window.tier_card_edit_state = transition.state
    window.editing_tier_entry = None
    window.tier_board.set_editing_entry(None)
    window.add_tier_btn.setText("Hozzáadás Tier listához")
    window.cancel_edit_btn.hide()
    window.mode_btn.setEnabled(True)
    if transition.changed:
        log_info(
            "tier_board",
            f"card_edit_finished: reason='{reason}'",
        )
    else:
        log_warning(
            "tier_board",
            f"card_edit_finish_skipped: reason='{transition.reason}'",
        )


def save_tier_card_edit(window) -> bool:
    entry = getattr(window, "editing_tier_entry", None)
    result = getattr(window, "latest_result", None)
    edit_state = getattr(
        window, "tier_card_edit_state", TierCardEditSessionState()
    )
    if (
        entry is None
        or result is None
        or not can_save_tier_card_edit(edit_state, entry.card_data.card_id)
    ):
        log_warning("tier_board", "card_edit_save_rejected: invalid_session_state")
        return False
    edited_card_id = entry.card_data.card_id
    updated = window.tier_board.update_saved_scored_entry(
        entry,
        title=window.title_edit.text(),
        score=result.display_score,
        tier=result.tier,
        cover_pixmap=window.selected_cover_pixmap,
        input_snapshot=capture_tier_card_input_snapshot(window),
        anilist_id=(
            window.selected_anime_result.anilist_id
            if window.selected_anime_result is not None
            else entry.card_data.anilist_id
        ),
    )
    if updated:
        finish_tier_card_edit(
            window,
            reason="saved",
            card_id=edited_card_id,
        )
        log_info("tier_board", f"card_edit_saved: card_id='{edited_card_id}'")
    else:
        log_warning("tier_board", f"card_edit_save_rejected: card_id='{edited_card_id}'")
    return updated
