from dataclasses import dataclass
from typing import Optional

from PyQt6.QtWidgets import QComboBox, QSpinBox

from app.services.profile_mix_service import default_profile_selection_memory
from app.services.reset_controls_service import reset_profile_combos_to_first_item


@dataclass(frozen=True)
class InitialProfileResetState:
    selection_memory: list[Optional[str]]
    current_mix_needed: int


def apply_initial_profile_weights(
    weight_spins: list[QSpinBox],
    total_weight: int,
) -> None:
    if not weight_spins:
        return

    weight_spins[0].setValue(total_weight)
    for spin in weight_spins[1:]:
        spin.setValue(0)


def reset_profile_inputs_to_initial_state(
    profile_combos: list[QComboBox],
    weight_spins: list[QSpinBox],
    profile_names: list[str],
    total_weight: int,
) -> InitialProfileResetState:
    apply_initial_profile_weights(weight_spins, total_weight)

    if profile_combos:
        reset_profile_combos_to_first_item(profile_combos)

    return InitialProfileResetState(
        selection_memory=default_profile_selection_memory(profile_names),
        current_mix_needed=1,
    )
