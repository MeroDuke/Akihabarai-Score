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

    values = [int(sp.value()) for sp in spins]
    total = sum(values)

    if total == TOTAL_WEIGHT:
        return

    def pick_target_index(candidates, current_values):
        # Először a legnagyobb értékből dolgozunk.
        # Holtversenynél a balról első (kisebb index) nyer.
        return max(candidates, key=lambda i: (current_values[i], -i))

    if total < TOTAL_WEIGHT:
        deficit = TOTAL_WEIGHT - total
        candidates = [i for i in range(needed) if i != changed_idx]

        if not candidates:
            spins[changed_idx].setValue(values[changed_idx] + deficit)
            return

        target_idx = pick_target_index(candidates, values)
        spins[target_idx].setValue(values[target_idx] + deficit)
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

        target_idx = pick_target_index(candidates, current_values)
        spins[target_idx].setValue(current_values[target_idx] - 1)
        overflow -= 1
