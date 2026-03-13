from typing import List, Tuple
from app.scoring import normalize_ratios
from app.core.constants import TOTAL_WEIGHT


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

    buffer_idx = needed - 1

    if changed_idx == buffer_idx:
        buffer_idx = 0

    others_sum = 0

    for i, sp in enumerate(spins):
        if i == buffer_idx:
            continue
        others_sum += int(sp.value())

    buffer_value = TOTAL_WEIGHT - others_sum

    if buffer_value >= 0:
        spins[buffer_idx].setValue(buffer_value)
        return

    spins[buffer_idx].setValue(0)

    fixed_sum = 0

    for i, sp in enumerate(spins):
        if i in (buffer_idx, changed_idx):
            continue
        fixed_sum += int(sp.value())

    max_for_changed = TOTAL_WEIGHT - fixed_sum

    if max_for_changed < 0:
        max_for_changed = 0

    current = int(spins[changed_idx].value())

    if current > max_for_changed:
        spins[changed_idx].setValue(max_for_changed)