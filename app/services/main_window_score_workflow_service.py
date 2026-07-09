from __future__ import annotations

from collections.abc import Callable

from app.services.dimension_input_workflow_service import (
    apply_dimension_slider_change,
    apply_dimension_spin_change,
)
from app.services.profile_mix_service import default_profile_selection_memory
from app.services.profile_mix_workflow_service import (
    apply_mix_mode_change_workflow,
    apply_profile_selection_change_workflow,
    apply_profile_weight_change_workflow,
    remember_active_profile_selections,
    restore_profile_combo_selection,
    update_profile_combo_options,
)
from app.services.profile_weight_reset_service import apply_initial_profile_weights
from app.services.reset_workflow_service import reset_score_inputs_to_initial_state
from app.services.result_recompute_service import recompute_result_and_update_views
from app.services.tier_add_workflow_service import add_current_result_to_tier_board


def apply_initial_profile_weights_to_window(
    *,
    weight_spins,
    total_weight: int,
    set_building: Callable[[bool], None],
):
    set_building(True)
    apply_initial_profile_weights(weight_spins, total_weight)
    set_building(False)


def build_default_profile_selection_memory(profiles) -> list:
    return default_profile_selection_memory(list(profiles.keys()))


def remember_profile_selections_from_window(
    *,
    profile_combos,
    profiles,
    selection_memory,
    mix_mode: str,
    mix_modes,
    needed: int | None = None,
):
    return remember_active_profile_selections(
        profile_combos=profile_combos,
        profiles=profiles,
        selection_memory=selection_memory,
        mix_mode=mix_mode,
        mix_modes=mix_modes,
        needed=needed,
    )


def restore_profile_selection_from_window(
    *,
    combo,
    index: int,
    selection_memory,
    profiles,
):
    restore_profile_combo_selection(
        combo=combo,
        index=index,
        selection_memory=selection_memory,
        profiles=profiles,
    )


def handle_mix_mode_change_from_window(
    *,
    profile_combos,
    weight_spins,
    profiles,
    selection_memory,
    current_mix_needed: int,
    mix_mode: str,
    mix_modes,
    total_weight: int,
    set_building: Callable[[bool], None],
):
    return apply_mix_mode_change_workflow(
        profile_combos=profile_combos,
        weight_spins=weight_spins,
        profiles=profiles,
        selection_memory=selection_memory,
        current_mix_needed=current_mix_needed,
        mix_mode=mix_mode,
        mix_modes=mix_modes,
        total_weight=total_weight,
        set_building=set_building,
    )


def handle_profile_selection_change_from_window(
    *,
    is_building: bool,
    profile_combos,
    weight_spins,
    profiles,
    selection_memory,
    mix_mode: str,
    mix_modes,
    set_building: Callable[[bool], None],
):
    if is_building:
        return None

    return apply_profile_selection_change_workflow(
        profile_combos=profile_combos,
        weight_spins=weight_spins,
        profiles=profiles,
        selection_memory=selection_memory,
        mix_mode=mix_mode,
        mix_modes=mix_modes,
        set_building=set_building,
    )


def update_profile_options_from_window(
    *,
    profile_combos,
    profiles,
    mix_mode: str,
    mix_modes,
):
    update_profile_combo_options(
        profile_combos=profile_combos,
        profiles=profiles,
        mix_mode=mix_mode,
        mix_modes=mix_modes,
    )


def handle_profile_weight_change_from_window(
    *,
    is_building: bool,
    weight_spins,
    changed_idx: int,
    new_value: int,
    mix_mode: str,
    mix_modes,
    set_building: Callable[[bool], None],
) -> bool:
    if is_building:
        return False

    return apply_profile_weight_change_workflow(
        weight_spins=weight_spins,
        changed_idx=changed_idx,
        new_value=new_value,
        mix_mode=mix_mode,
        mix_modes=mix_modes,
        set_building=set_building,
    )


def handle_dimension_slider_change_from_window(
    *,
    is_building: bool,
    set_building: Callable[[bool], None],
    state,
    spin_widget,
    slider_value: int,
) -> bool:
    return apply_dimension_slider_change(
        is_building=is_building,
        set_building=set_building,
        state=state,
        spin_widget=spin_widget,
        slider_value=slider_value,
    )


def handle_dimension_spin_change_from_window(
    *,
    is_building: bool,
    set_building: Callable[[bool], None],
    state,
    slider_widget,
    spin_value: float,
) -> bool:
    return apply_dimension_spin_change(
        is_building=is_building,
        set_building=set_building,
        state=state,
        slider_widget=slider_widget,
        spin_value=spin_value,
    )


def reset_score_inputs_from_window(
    *,
    set_building: Callable[[bool], None],
    title_edit,
    title_search_controller,
    mix_combo,
    states,
    slider_widgets,
    spin_widgets,
    profile_combos,
    weight_spins,
    profile_names,
    total_weight: int,
    update_profile_combo_options_func: Callable[[], None],
):
    return reset_score_inputs_to_initial_state(
        set_building=set_building,
        title_edit=title_edit,
        title_search_controller=title_search_controller,
        mix_combo=mix_combo,
        states=states,
        slider_widgets=slider_widgets,
        spin_widgets=spin_widgets,
        profile_combos=profile_combos,
        weight_spins=weight_spins,
        profile_names=list(profile_names),
        total_weight=total_weight,
        update_profile_combo_options=update_profile_combo_options_func,
    )


def recompute_from_window(
    *,
    profiles,
    profile_combos,
    weight_spins,
    mix_mode: str,
    mix_modes,
    states,
    tier_thresholds,
    ui_cfg,
    title: str,
    result_panel,
    tier_board,
    cover_pixmap,
    build_result_payload_func,
):
    return recompute_result_and_update_views(
        profiles=profiles,
        profile_combos=profile_combos,
        weight_spins=weight_spins,
        mix_mode=mix_mode,
        mix_modes=mix_modes,
        states=states,
        tier_thresholds=tier_thresholds,
        ui_cfg=ui_cfg,
        title=title,
        result_panel=result_panel,
        tier_board=tier_board,
        cover_pixmap=cover_pixmap,
        build_result_payload_func=build_result_payload_func,
    )


def add_current_result_from_window(
    *,
    parent,
    tier_board,
    title: str,
    latest_result,
    recompute: Callable[[], None],
    get_latest_result: Callable[[], dict | None],
    cover_pixmap,
):
    add_current_result_to_tier_board(
        parent=parent,
        tier_board=tier_board,
        title=title,
        latest_result=latest_result,
        recompute=recompute,
        get_latest_result=get_latest_result,
        cover_pixmap=cover_pixmap,
    )
