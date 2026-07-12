from __future__ import annotations

from app.services.main_window_score_workflow_service import (
    apply_initial_profile_weights_to_window,
    build_default_profile_selection_memory,
    handle_dimension_slider_change_from_window,
    handle_dimension_spin_change_from_window,
    handle_mix_mode_change_from_window,
    handle_profile_selection_change_from_window,
    handle_profile_weight_change_from_window,
    remember_profile_selections_from_window,
    reset_score_inputs_from_window,
    restore_profile_selection_from_window,
    update_profile_options_from_window,
)


def apply_initial_profile_weights_for_window(window, *, total_weight: int):
    apply_initial_profile_weights_to_window(
        weight_spins=window.weight_spins,
        total_weight=total_weight,
        set_building=lambda value: setattr(window, "_building", value),
    )


def build_default_profile_selection_memory_for_window(window) -> list:
    return build_default_profile_selection_memory(window.profiles)


def remember_active_profile_selections_for_window(
    window,
    *,
    mix_modes,
    needed: int | None = None,
):
    window.profile_selection_memory = remember_profile_selections_from_window(
        profile_combos=window.profile_combos,
        profiles=window.profiles,
        selection_memory=window.profile_selection_memory,
        mix_mode=window.mix_combo.currentText(),
        mix_modes=mix_modes,
        needed=needed,
    )


def restore_profile_combo_selection_for_window(window, combo, index: int):
    restore_profile_selection_from_window(
        combo=combo,
        index=index,
        selection_memory=window.profile_selection_memory,
        profiles=window.profiles,
    )


def handle_mix_change_for_window(window, *, mix_modes, total_weight: int):
    state = handle_mix_mode_change_from_window(
        profile_combos=window.profile_combos,
        weight_spins=window.weight_spins,
        profiles=window.profiles,
        selection_memory=window.profile_selection_memory,
        current_mix_needed=getattr(window, "current_mix_needed", 1),
        mix_mode=window.mix_combo.currentText(),
        mix_modes=mix_modes,
        total_weight=total_weight,
        set_building=lambda value: setattr(window, "_building", value),
    )
    window.profile_selection_memory = state.selection_memory
    window.current_mix_needed = state.current_mix_needed
    window.recompute()


def handle_profile_change_for_window(window, *, mix_modes):
    state = handle_profile_selection_change_from_window(
        is_building=window._building,
        profile_combos=window.profile_combos,
        weight_spins=window.weight_spins,
        profiles=window.profiles,
        selection_memory=window.profile_selection_memory,
        mix_mode=window.mix_combo.currentText(),
        mix_modes=mix_modes,
        set_building=lambda value: setattr(window, "_building", value),
    )
    if state is None:
        return

    window.profile_selection_memory = state.selection_memory
    window.recompute()


def update_profile_combo_options_for_window(window, *, mix_modes):
    update_profile_options_from_window(
        profile_combos=window.profile_combos,
        profiles=window.profiles,
        mix_mode=window.mix_combo.currentText(),
        mix_modes=mix_modes,
    )


def handle_profile_weight_change_for_window(
    window,
    *,
    changed_idx: int,
    new_value: int,
    mix_modes,
):
    handled = handle_profile_weight_change_from_window(
        is_building=window._building,
        weight_spins=window.weight_spins,
        changed_idx=changed_idx,
        new_value=new_value,
        mix_mode=window.mix_combo.currentText(),
        mix_modes=mix_modes,
        set_building=lambda value: setattr(window, "_building", value),
    )

    if handled:
        window.recompute()


def handle_dimension_slider_change_for_window(
    window,
    *,
    index: int,
    slider_value: int,
):
    handled = handle_dimension_slider_change_from_window(
        is_building=window._building,
        set_building=lambda value: setattr(window, "_building", value),
        state=window.states[index],
        spin_widget=window.spin_widgets[index],
        slider_value=slider_value,
    )

    if handled:
        window.recompute()


def handle_dimension_spin_change_for_window(
    window,
    *,
    index: int,
    spin_value: float,
):
    handled = handle_dimension_spin_change_from_window(
        is_building=window._building,
        set_building=lambda value: setattr(window, "_building", value),
        state=window.states[index],
        slider_widget=window.slider_widgets[index],
        spin_value=spin_value,
    )

    if handled:
        window.recompute()


def reset_score_inputs_for_window(window, *, total_weight: int):
    reset_state = reset_score_inputs_from_window(
        set_building=lambda value: setattr(window, "_building", value),
        title_edit=window.title_edit,
        title_search_controller=window.title_search_controller,
        mix_combo=window.mix_combo,
        states=window.states,
        slider_widgets=window.slider_widgets,
        spin_widgets=window.spin_widgets,
        profile_combos=window.profile_combos,
        weight_spins=window.weight_spins,
        profile_names=list(window.profiles.keys()),
        total_weight=total_weight,
        update_profile_combo_options_func=window._update_profile_combo_options_internal,
    )
    window.selected_anime_result = reset_state.selected_anime_result
    window.selected_cover_pixmap = reset_state.selected_cover_pixmap
    window.profile_selection_memory = reset_state.profile_selection_memory
    window.current_mix_needed = reset_state.current_mix_needed
    window.on_mix_changed()
