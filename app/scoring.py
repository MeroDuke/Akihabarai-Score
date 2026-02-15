from __future__ import annotations
from dataclasses import dataclass
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
    if not profiles:
        return None
    ratios = normalize_ratios(ratios)
    rel = [0.0] * 8
    for pname, r in zip(selected, ratios):
        weights = profiles.get(pname)
        if not weights:
            continue
        for i in range(8):
            rel[i] += float(weights[i]) * float(r)
    # safety clamp (your spec typically 0.2..1.0)
    return [clamp(x, 0.0, 1.0) for x in rel]

def compute_score(
    dim_values: List[float],
    relevances: Optional[List[float]],
) -> Tuple[float, List[float], List[float]]:
    """
    Returns (score_0to10, used_relevances, contributions)
    score = Σ(dim_i * rel_i) / Σ(rel_i)
    If relevances is None -> simple average with rel=1.0
    """
    if len(dim_values) != 8:
        raise ValueError("dim_values must have length 8")

    if relevances is None:
        score = sum(dim_values) / 8.0
        return clamp(score, 0.0, 10.0), [1.0] * 8, dim_values[:]

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
    return clamp(score, 0.0, 10.0), relevances[:], contrib
