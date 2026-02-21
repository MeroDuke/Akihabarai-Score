from __future__ import annotations
from typing import Dict, List, Optional, Tuple


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def tier_from_score(score: float, thresholds: Dict[str, float]) -> str:
    order = ["S", "A", "B", "C", "D", "E", "F"]
    for t in order:
        if score >= float(thresholds.get(t, 0.0)):
            return t
    return "F"


def normalize_ratios(ratios: List[float]) -> List[float]:
    s = sum(ratios)
    if s <= 0:
        return [1.0] + [0.0] * (len(ratios) - 1)
    return [r / s for r in ratios]


def mixed_relevances(
    profiles: Dict[str, List[float]],
    selected: List[str],
    ratios: List[float],
) -> Optional[List[float]]:
    """
    Mixeli a relevanciákat a kiválasztott profilok és arányok alapján.
    Visszaad 8 elemű listát (0.0..1.0 clamp), vagy None-t, ha nincs profil.
    """
    if not profiles:
        return None

    ratios = normalize_ratios(ratios)
    rel = [0.0] * 8

    for pname, r in zip(selected, ratios):
        weights = profiles.get(pname)
        if not weights:
            continue
        if len(weights) != 8:
            raise ValueError(f"Hibás profil relevancia hossz: {pname}")
        for i in range(8):
            rel[i] += float(weights[i]) * float(r)

    return [clamp(x, 0.0, 1.0) for x in rel]


def compute_score(
    dim_values: List[float],
    relevances: Optional[List[float]],
) -> Tuple[float, List[float], List[float]]:
    """
    score = Σ(dim_i * rel_i) / Σ(rel_i)
    Ha relevances None -> egyszerű átlag.
    Returns: (score_0..10, used_relevances(8), contributions(8))
    """
    if len(dim_values) != 8:
        raise ValueError("dim_values must have length 8")

    if relevances is None:
        score = sum(dim_values) / 8.0
        score = clamp(score, 1.0, 10.0)
        return score, [1.0] * 8, dim_values[:]

    if len(relevances) != 8:
        raise ValueError("relevances must have length 8")

    num = 0.0
    den = 0.0
    contrib: List[float] = []
    for v, w in zip(dim_values, relevances):
        c = float(v) * float(w)
        contrib.append(c)
        num += c
        den += float(w)

    score = (num / den) if den > 0 else 0.0
    score = clamp(score, 1.0, 10.0)
    return score, relevances[:], contrib

def display_score_consistent(
    raw_score: float,
    tier: str,
    thresholds: Dict[str, float],
    step: float = 0.1,
) -> float:
    """
    A kijelzett pontszámot úgy korrigálja,
    hogy biztosan a Tier intervallumán belül maradjon.
    """

    # Tier sorrend
    order = ["S", "A", "B", "C", "D", "E", "F"]
    idx = order.index(tier)

    min_incl = float(thresholds.get(tier, 0.0))

    # felső határ = a következő (jobb) tier küszöbe
    if idx > 0:
        higher = order[idx - 1]
        max_excl = float(thresholds.get(higher, 10.0))
    else:
        max_excl = 10.0001

    # alap kerekítés
    disp = round(raw_score, 1)

    # ha átcsúszna a határon, visszakényszerítjük
    if disp < min_incl:
        disp = min_incl

    if disp >= max_excl:
        disp = max_excl - step

    return round(disp, 1)