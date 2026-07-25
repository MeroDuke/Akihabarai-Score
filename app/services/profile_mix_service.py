from dataclasses import dataclass
from typing import List, Optional, Tuple

from app.scoring import normalize_ratios
from app.core.constants import TOTAL_WEIGHT


@dataclass(frozen=True)
class ProfileWeightChange:
    handled: bool
    weights: list[int]


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


def select_profiles_and_ratios(
    profile_names: list[str],
    weights: list[int | float],
    mix_mode: str,
    mix_modes: dict[str, int],
) -> Tuple[List[str], List[float]]:
    needed = mix_modes.get(mix_mode, 1)
    selected = list(profile_names[:needed])
    active_weights = [float(value) for value in weights[:needed]]
    return selected, normalize_ratios(active_weights)


def rebalance_profile_weights(
    weights: list[int],
    needed: int,
    changed_idx: int,
    total_weight: int = TOTAL_WEIGHT,
) -> list[int]:
    balanced = list(weights)
    active = balanced[:needed]

    if needed <= 1:
        if active:
            balanced[0] = total_weight
        return balanced

    total = sum(active)

    if total == total_weight:
        return balanced

    def pick_largest_index(candidates, current_values):
        return max(candidates, key=lambda i: (current_values[i], -i))

    def pick_smallest_index(candidates, current_values):
        return min(candidates, key=lambda i: (current_values[i], i))

    if total < total_weight:
        deficit = total_weight - total

        while deficit > 0:
            current_values = balanced[:needed]
            candidates = [i for i in range(needed) if i != changed_idx]

            if not candidates:
                balanced[changed_idx] += deficit
                return balanced

            target_idx = pick_smallest_index(candidates, current_values)
            balanced[target_idx] += 1
            deficit -= 1

        return balanced

    overflow = total - total_weight

    while overflow > 0:
        current_values = balanced[:needed]
        candidates = [
            i for i in range(needed)
            if i != changed_idx and current_values[i] > 0
        ]

        if not candidates:
            balanced[changed_idx] = max(0, balanced[changed_idx] - overflow)
            return balanced

        target_idx = pick_largest_index(candidates, current_values)
        balanced[target_idx] -= 1
        overflow -= 1

    return balanced


def normalize_profile_weights(
    weights: list[int],
    needed: int,
    total_weight: int,
) -> list[int]:
    normalized = list(weights)
    active_sum = sum(normalized[:needed])
    if active_sum <= 0:
        if not normalized or needed <= 0:
            return normalized
        normalized[0] = total_weight
        for index in range(1, needed):
            normalized[index] = 0
        return normalized

    return rebalance_profile_weights(
        normalized,
        needed,
        changed_idx=0,
        total_weight=total_weight,
    )


def change_profile_weight(
    weights: list[int],
    changed_idx: int,
    mix_mode: str,
    mix_modes: dict[str, int],
    total_weight: int = TOTAL_WEIGHT,
) -> ProfileWeightChange:
    needed = mix_modes.get(mix_mode, 1)

    if changed_idx < 0 or changed_idx >= needed or changed_idx >= len(weights):
        return ProfileWeightChange(handled=False, weights=list(weights))

    return ProfileWeightChange(
        handled=True,
        weights=rebalance_profile_weights(
            list(weights),
            needed,
            changed_idx,
            total_weight,
        ),
    )
