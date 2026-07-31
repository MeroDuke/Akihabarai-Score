from collections.abc import Callable

from app.services.profile_mix_service import (
    build_profile_combo_options,
    change_profile_weight,
    normalize_profile_weights,
    select_profiles_and_ratios,
)
from app.services.selection_id_service import (
    add_identifier_items,
    current_identifier,
)


INACTIVE_PROFILE_LABEL = "—"


def read_profile_mix(
    profile_combos,
    weight_spins,
    mix_mode: str,
    mix_modes: dict[str, int],
) -> tuple[list[str], list[float]]:
    return select_profiles_and_ratios(
        [current_identifier(combo) for combo in profile_combos],
        [spin.value() for spin in weight_spins],
        mix_mode,
        mix_modes,
    )


def apply_balanced_weights(weight_spins, weights: list[int]) -> None:
    for spin, value in zip(weight_spins, weights):
        spin.setValue(value)


def normalize_active_profile_weights(
    weight_spins,
    needed: int,
    total_weight: int,
) -> None:
    weights = normalize_profile_weights(
        [spin.value() for spin in weight_spins],
        needed,
        total_weight,
    )
    apply_balanced_weights(weight_spins, weights)


def apply_profile_weight_change(
    weight_spins,
    changed_idx: int,
    mix_mode: str,
    mix_modes: dict[str, int],
) -> bool:
    outcome = change_profile_weight(
        [spin.value() for spin in weight_spins],
        changed_idx,
        mix_mode,
        mix_modes,
    )
    if outcome.handled:
        apply_balanced_weights(weight_spins, outcome.weights)
    return outcome.handled


def apply_profile_mix_row_states(
    profile_combos,
    weight_spins,
    profile_names: list[str],
    needed: int,
    restore_profile_selection: Callable[[object, int], None] | None = None,
    inactive_label: str = INACTIVE_PROFILE_LABEL,
) -> None:
    for index, combo in enumerate(profile_combos):
        enabled = index < needed
        weight_spins[index].setEnabled(enabled)
        combo.setEnabled(enabled)

        combo.blockSignals(True)
        try:
            combo.clear()

            if not enabled:
                weight_spins[index].setValue(0)
                combo.addItem(inactive_label)
                combo.setCurrentIndex(0)
                continue

            add_identifier_items(combo, profile_names)
            if restore_profile_selection is not None:
                restore_profile_selection(combo, index)
        finally:
            combo.blockSignals(False)


def refresh_active_profile_combo_options(
    profile_combos,
    all_profiles: list[str],
    needed: int,
) -> None:
    if not all_profiles:
        return

    combo_options = build_profile_combo_options(
        all_profiles=all_profiles,
        current_profiles=[current_identifier(combo) for combo in profile_combos],
        needed=needed,
        slots=len(profile_combos),
    )

    for index, combo in enumerate(profile_combos):
        if index >= needed:
            continue

        allowed, selected_profile = combo_options[index]

        combo.blockSignals(True)
        try:
            combo.clear()
            add_identifier_items(combo, allowed)
            combo.setCurrentText(selected_profile or all_profiles[0])
        finally:
            combo.blockSignals(False)
