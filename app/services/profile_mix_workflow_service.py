from collections.abc import Callable
from dataclasses import dataclass
from typing import Optional

from app.logger import log_info
from app.services.profile_mix_service import (
    apply_profile_mix_row_states,
    apply_profile_weight_change,
    get_selected_profiles_and_ratios,
    normalize_active_profile_weights,
    refresh_active_profile_combo_options,
    remember_profile_selections,
)


@dataclass(frozen=True)
class ProfileMixWorkflowState:
    selection_memory: list[Optional[str]]
    current_mix_needed: int


@dataclass(frozen=True)
class ProfileSelectionWorkflowState:
    selection_memory: list[Optional[str]]
    selected: list[str]
    ratios: list[float]


def remember_active_profile_selections(
    *,
    profile_combos,
    profiles,
    selection_memory: list[Optional[str]],
    mix_mode: str,
    mix_modes: dict[str, int],
    needed: int | None = None,
) -> list[Optional[str]]:
    if not profile_combos:
        return selection_memory

    all_profiles = list(profiles.keys())
    if not all_profiles:
        return selection_memory

    if needed is None:
        needed = mix_modes.get(mix_mode, 1)

    return remember_profile_selections(
        memory=selection_memory,
        current_profiles=[combo.currentText() for combo in profile_combos],
        all_profiles=all_profiles,
        needed=needed,
    )


def restore_profile_combo_selection(
    *,
    combo,
    index: int,
    selection_memory: list[Optional[str]],
    profiles,
) -> None:
    remembered_profile = None
    if index < len(selection_memory):
        remembered_profile = selection_memory[index]

    if remembered_profile in profiles:
        combo.setCurrentText(remembered_profile)


def update_profile_combo_options(
    *,
    profile_combos,
    profiles,
    mix_mode: str,
    mix_modes: dict[str, int],
) -> None:
    if not profiles:
        return

    all_profiles = list(profiles.keys())
    if not all_profiles:
        return

    needed = mix_modes.get(mix_mode, 1)

    refresh_active_profile_combo_options(
        profile_combos=profile_combos,
        all_profiles=all_profiles,
        needed=needed,
    )


def apply_mix_mode_change_workflow(
    *,
    profile_combos,
    weight_spins,
    profiles,
    selection_memory: list[Optional[str]],
    current_mix_needed: int,
    mix_mode: str,
    mix_modes: dict[str, int],
    total_weight: int,
    set_building: Callable[[bool], None],
) -> ProfileMixWorkflowState:
    updated_memory = remember_active_profile_selections(
        profile_combos=profile_combos,
        profiles=profiles,
        selection_memory=selection_memory,
        mix_mode=mix_mode,
        mix_modes=mix_modes,
        needed=current_mix_needed,
    )

    log_info("ui", f"mix_mode_changed: mode='{mix_mode}'")
    needed = mix_modes.get(mix_mode, 1)

    set_building(True)
    try:
        apply_profile_mix_row_states(
            profile_combos,
            weight_spins,
            list(profiles.keys()),
            needed,
            lambda combo, index: restore_profile_combo_selection(
                combo=combo,
                index=index,
                selection_memory=updated_memory,
                profiles=profiles,
            ),
        )

        normalize_active_profile_weights(
            weight_spins,
            needed,
            total_weight,
        )

        update_profile_combo_options(
            profile_combos=profile_combos,
            profiles=profiles,
            mix_mode=mix_mode,
            mix_modes=mix_modes,
        )
        updated_memory = remember_active_profile_selections(
            profile_combos=profile_combos,
            profiles=profiles,
            selection_memory=updated_memory,
            mix_mode=mix_mode,
            mix_modes=mix_modes,
            needed=needed,
        )

        return ProfileMixWorkflowState(
            selection_memory=updated_memory,
            current_mix_needed=needed,
        )
    finally:
        set_building(False)


def apply_profile_selection_change_workflow(
    *,
    profile_combos,
    weight_spins,
    profiles,
    selection_memory: list[Optional[str]],
    mix_mode: str,
    mix_modes: dict[str, int],
    set_building: Callable[[bool], None],
) -> ProfileSelectionWorkflowState:
    selected, ratios = get_selected_profiles_and_ratios(
        profile_combos,
        weight_spins,
        mix_mode,
        mix_modes,
    )
    log_info("ui", f"profile_changed: selected={selected} ratios={ratios}")

    set_building(True)
    try:
        update_profile_combo_options(
            profile_combos=profile_combos,
            profiles=profiles,
            mix_mode=mix_mode,
            mix_modes=mix_modes,
        )
        updated_memory = remember_active_profile_selections(
            profile_combos=profile_combos,
            profiles=profiles,
            selection_memory=selection_memory,
            mix_mode=mix_mode,
            mix_modes=mix_modes,
        )
    finally:
        set_building(False)

    return ProfileSelectionWorkflowState(
        selection_memory=updated_memory,
        selected=selected,
        ratios=ratios,
    )


def apply_profile_weight_change_workflow(
    *,
    weight_spins,
    changed_idx: int,
    new_value: int,
    mix_mode: str,
    mix_modes: dict[str, int],
    set_building: Callable[[bool], None],
) -> bool:
    log_info("ui", f"weight_changed: idx={changed_idx} value={new_value}")

    set_building(True)
    try:
        return apply_profile_weight_change(
            weight_spins,
            changed_idx,
            mix_mode,
            mix_modes,
        )
    finally:
        set_building(False)
