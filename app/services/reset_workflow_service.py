from collections.abc import Callable
from dataclasses import dataclass
from typing import Optional

from app.core.models import DimState
from app.services.dimension_controls_service import reset_dimension_controls
from app.services.profile_weight_reset_service import (
    reset_profile_inputs_to_initial_state,
)
from app.services.reset_controls_service import reset_combo_to_first_item
from app.services.title_reset_service import reset_title_input_state


@dataclass(frozen=True)
class ResetWorkflowState:
    selected_anime_result: object | None
    selected_cover_pixmap: object | None
    profile_selection_memory: list[Optional[str]]
    current_mix_needed: int


def reset_score_inputs_to_initial_state(
    *,
    set_building: Callable[[bool], None],
    title_edit,
    title_search_controller,
    mix_combo,
    states: list[DimState],
    slider_widgets,
    spin_widgets,
    profile_combos,
    weight_spins,
    profile_names: list[str],
    total_weight: int,
    update_profile_combo_options: Callable[[], None],
) -> ResetWorkflowState:
    set_building(True)
    try:
        title_reset_state = reset_title_input_state(
            title_edit,
            title_search_controller,
        )

        reset_combo_to_first_item(mix_combo)

        reset_dimension_controls(
            states,
            slider_widgets,
            spin_widgets,
        )

        profile_reset_state = reset_profile_inputs_to_initial_state(
            profile_combos=profile_combos,
            weight_spins=weight_spins,
            profile_names=profile_names,
            total_weight=total_weight,
        )

        update_profile_combo_options()
    finally:
        set_building(False)

    return ResetWorkflowState(
        selected_anime_result=title_reset_state.selected_anime_result,
        selected_cover_pixmap=title_reset_state.selected_cover_pixmap,
        profile_selection_memory=profile_reset_state.selection_memory,
        current_mix_needed=profile_reset_state.current_mix_needed,
    )
