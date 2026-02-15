import math
import pytest

from app.scoring import (
    mixed_relevances,
    compute_score,
    tier_from_score,
    normalize_ratios,
)

def test_normalize_ratios_basic():
    assert normalize_ratios([2.0, 1.0]) == [2/3, 1/3]

def test_normalize_ratios_zero_sum_fallback():
    assert normalize_ratios([0.0, 0.0]) == [1.0, 0.0]

def test_mixed_relevances_single_profile():
    profiles = {"Akció": [0.6,0.6,0.9,0.8,1.0,0.8,0.7,0.8]}
    rel = mixed_relevances(profiles, ["Akció"], [1.0])
    assert rel == profiles["Akció"]

def test_mixed_relevances_mix_two_profiles():
    profiles = {
        "A": [1.0]*8,
        "B": [0.0]*8,
    }
    rel = mixed_relevances(profiles, ["A", "B"], [0.7, 0.3])
    assert rel == [0.7]*8

def test_compute_score_simple_average():
    vals = [5.0]*8
    score, rel, contrib = compute_score(vals, None)
    assert score == 5.0
    assert rel == [1.0]*8
    assert contrib == vals

def test_compute_score_weighted_known_value():
    vals = [10.0] + [0.0]*7
    rel = [1.0]*8
    score, _, _ = compute_score(vals, rel)
    # 10/8 = 1.25
    assert math.isclose(score, 1.25, rel_tol=0, abs_tol=1e-12)

def test_tier_from_score():
    thresholds = {"S":9.0,"A":8.0,"B":7.0,"C":6.0,"D":5.0,"E":4.0,"F":1.0}
    assert tier_from_score(9.0, thresholds) == "S"
    assert tier_from_score(7.2, thresholds) == "B"
    assert tier_from_score(5.0, thresholds) == "D"

def test_compute_score_validates_length():
    with pytest.raises(ValueError):
        compute_score([1.0]*7, None)
