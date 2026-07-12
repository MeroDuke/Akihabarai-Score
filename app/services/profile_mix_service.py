from collections.abc import Callable
from typing import List, Optional, Tuple
from app.scoring import normalize_ratios
from app.core.constants import TOTAL_WEIGHT


INACTIVE_PROFILE_LABEL = "—"


def default_profile_selection_memory(
    profile_names: List[str],
    slots: int = 3,
) -> List[Optional[str]]:
    if not profile_names:
        return [None] * slots

    remembered: List[Optional[str]] = []
    for index in range(slots):
        remembered.append(
            profile_names[index] if index < len(profile_names) else profile_names[0]
        )

    return remembered


def remember_profile_selections(
    memory: List[Optional[str]],
    current_profiles: List[str],
    all_profiles: List[str],
    needed: int,
) -> List[Optional[str]]:
    if not current_profiles or not all_profiles:
        return list(memory)

    valid_profiles = set(all_profiles)
    remembered = list(memory)

    limit = min(needed, len(current_profiles), len(remembered))
    for index in range(limit):
        current_profile = current_profiles[index]
        if current_profile in valid_profiles:
            remembered[index] = current_profile

    return remembered


def build_profile_combo_options(
    all_profiles: List[str],
    current_profiles: List[str],
    needed: int,
    slots: int = 3,
) -> List[Tuple[List[str], Optional[str]]]:
    if not all_profiles:
        return [([], None) for _ in range(slots)]

    used = set()
    chosen: List[Optional[str]] = [None] * slots

    for index in range(min(needed, slots)):
        current_profile = (
            current_profiles[index] if index < len(current_profiles) else ""
        )
        if current_profile in all_profiles and current_profile not in used:
            chosen[index] = current_profile
            used.add(current_profile)
        else:
            for profile in all_profiles:
                if profile not in used:
                    chosen[index] = profile
                    used.add(profile)
                    break
            if chosen[index] is None:
                chosen[index] = all_profiles[0]

    for index in range(needed, slots):
        chosen[index] = all_profiles[0]

    combo_options: List[Tuple[List[str], Optional[str]]] = []
    for index in range(slots):
        if index >= needed:
            combo_options.append(([], chosen[index]))
            continue

        other_used = set(chosen[:needed])
        other_used.discard(chosen[index])

        allowed = []
        for profile in all_profiles:
            if profile == chosen[index] or profile not in other_used:
                allowed.append(profile)

        combo_options.append((allowed, chosen[index]))

    return combo_options


def get_selected_profiles_and_ratios(
    profile_combos,
    weight_spins,
    mix_mode,
    mix_modes,
) -> Tuple[List[str], List[float]]:

    needed = mix_modes.get(mix_mode, 1)

    selected = []
    weights = []

    for i in range(needed):
        selected.append(profile_combos[i].currentText())
        weights.append(float(weight_spins[i].value()))

    ratios = normalize_ratios(weights)

    return selected, ratios

def force_total_weight(weight_spins, needed: int, changed_idx: int):
    spins = weight_spins[:needed]

    if needed <= 1:
        spins[0].setValue(TOTAL_WEIGHT)
        return

    values = [int(sp.value()) for sp in spins]
    total = sum(values)

    if total == TOTAL_WEIGHT:
        return

    def pick_largest_index(candidates, current_values):
        # Csökkentésnél a legnagyobb másikból veszünk el.
        # Holtversenynél a balról első nyer.
        return max(candidates, key=lambda i: (current_values[i], -i))

    def pick_smallest_index(candidates, current_values):
        # Növelésnél a legkisebb másikat növeljük.
        # Holtversenynél a balról első nyer.
        return min(candidates, key=lambda i: (current_values[i], i))

    if total < TOTAL_WEIGHT:
        deficit = TOTAL_WEIGHT - total

        while deficit > 0:
            current_values = [int(sp.value()) for sp in spins]
            candidates = [i for i in range(needed) if i != changed_idx]

            if not candidates:
                spins[changed_idx].setValue(current_values[changed_idx] + deficit)
                return

            target_idx = pick_smallest_index(candidates, current_values)
            spins[target_idx].setValue(current_values[target_idx] + 1)
            deficit -= 1

        return

    overflow = total - TOTAL_WEIGHT

    while overflow > 0:
        current_values = [int(sp.value()) for sp in spins]
        candidates = [
            i for i in range(needed)
            if i != changed_idx and current_values[i] > 0
        ]

        if not candidates:
            current = current_values[changed_idx]
            spins[changed_idx].setValue(max(0, current - overflow))
            return

        target_idx = pick_largest_index(candidates, current_values)
        spins[target_idx].setValue(current_values[target_idx] - 1)
        overflow -= 1


def normalize_active_profile_weights(
    weight_spins,
    needed: int,
    total_weight: int,
) -> None:
    active_sum = sum(weight_spins[i].value() for i in range(needed))
    if active_sum <= 0:
        weight_spins[0].setValue(total_weight)
        for index in range(1, needed):
            weight_spins[index].setValue(0)
        return

    force_total_weight(weight_spins, needed, 0)


def apply_profile_weight_change(
    weight_spins,
    changed_idx: int,
    mix_mode: str,
    mix_modes: dict[str, int],
) -> bool:
    needed = mix_modes.get(mix_mode, 1)

    if changed_idx >= needed:
        return False

    force_total_weight(weight_spins, needed, changed_idx)
    return True


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

            combo.addItems(profile_names)
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
        current_profiles=[combo.currentText() for combo in profile_combos],
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
            combo.addItems(allowed)
            combo.setCurrentText(selected_profile or all_profiles[0])
        finally:
            combo.blockSignals(False)
