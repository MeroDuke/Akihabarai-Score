from app.services.profile_mix_service import (
    get_selected_profiles_and_ratios,
    force_total_weight,
)


class DummyCombo:
    def __init__(self, text: str):
        self._text = text

    def currentText(self) -> str:
        return self._text


class DummySpin:
    def __init__(self, value: int):
        self._value = value

    def value(self) -> int:
        return self._value

    def setValue(self, value: int) -> None:
        self._value = value


def test_get_selected_profiles_and_ratios_single_profile():
    combos = [DummyCombo("Fantasy"), DummyCombo("Drama"), DummyCombo("Action")]
    spins = [DummySpin(100), DummySpin(0), DummySpin(0)]
    mix_modes = {"1 profile": 1, "2 profiles": 2, "3 profiles": 3}

    selected, ratios = get_selected_profiles_and_ratios(
        combos, spins, "1 profile", mix_modes
    )

    assert selected == ["Fantasy"]
    assert ratios == [1.0]


def test_get_selected_profiles_and_ratios_two_profiles():
    combos = [DummyCombo("Fantasy"), DummyCombo("Drama"), DummyCombo("Action")]
    spins = [DummySpin(60), DummySpin(40), DummySpin(0)]
    mix_modes = {"1 profile": 1, "2 profiles": 2, "3 profiles": 3}

    selected, ratios = get_selected_profiles_and_ratios(
        combos, spins, "2 profiles", mix_modes
    )

    assert selected == ["Fantasy", "Drama"]
    assert ratios == [0.6, 0.4]


def test_get_selected_profiles_and_ratios_zero_weights_fallback_equal_split():
    combos = [DummyCombo("Fantasy"), DummyCombo("Drama"), DummyCombo("Action")]
    spins = [DummySpin(0), DummySpin(0), DummySpin(0)]
    mix_modes = {"1 profile": 1, "2 profiles": 2, "3 profiles": 3}

    selected, ratios = get_selected_profiles_and_ratios(
        combos, spins, "2 profiles", mix_modes
    )

    assert selected == ["Fantasy", "Drama"]
    assert ratios == [1.0, 0.0]


def test_force_total_weight_single_profile_forces_100():
    spins = [DummySpin(25), DummySpin(0), DummySpin(0)]

    force_total_weight(spins, needed=1, changed_idx=0)

    assert spins[0].value() == 100


def test_force_total_weight_two_profiles_adjusts_other_spin():
    spins = [DummySpin(70), DummySpin(20), DummySpin(0)]

    force_total_weight(spins, needed=2, changed_idx=0)

    assert spins[0].value() == 70
    assert spins[1].value() == 30
    assert spins[0].value() + spins[1].value() == 100


def test_force_total_weight_three_profiles_fills_deficit_into_smallest_other():
    spins = [DummySpin(50), DummySpin(30), DummySpin(10)]

    force_total_weight(spins, needed=3, changed_idx=1)

    assert spins[0].value() == 50
    assert spins[1].value() == 30
    assert spins[2].value() == 20
    assert sum(sp.value() for sp in spins[:3]) == 100


def test_force_total_weight_overflow_reduces_largest_other_not_changed_spin():
    spins = [DummySpin(10), DummySpin(80), DummySpin(50)]

    force_total_weight(spins, needed=3, changed_idx=2)

    assert spins[0].value() == 10
    assert spins[1].value() == 40
    assert spins[2].value() == 50
    assert sum(sp.value() for sp in spins[:3]) == 100


def test_force_total_weight_tie_break_prefers_leftmost_largest_spin():
    spins = [DummySpin(34), DummySpin(34), DummySpin(34)]

    force_total_weight(spins, needed=3, changed_idx=2)

    assert spins[0].value() == 33
    assert spins[1].value() == 33
    assert spins[2].value() == 34
    assert sum(sp.value() for sp in spins) == 100


def test_force_total_weight_deficit_increases_smallest_other_stepwise():
    spins = [DummySpin(98), DummySpin(0), DummySpin(0)]

    force_total_weight(spins, needed=3, changed_idx=0)

    assert spins[0].value() == 98
    assert spins[1].value() == 1
    assert spins[2].value() == 1
    assert sum(sp.value() for sp in spins[:3]) == 100


def test_force_total_weight_deficit_tie_break_prefers_leftmost_smallest_spin():
    spins = [DummySpin(99), DummySpin(0), DummySpin(0)]

    force_total_weight(spins, needed=3, changed_idx=0)

    assert spins[0].value() == 99
    assert spins[1].value() == 1
    assert spins[2].value() == 0
    assert sum(sp.value() for sp in spins[:3]) == 100


def test_force_total_weight_deficit_after_reduction_keeps_distribution_balanced():
    spins = [DummySpin(97), DummySpin(0), DummySpin(0)]

    force_total_weight(spins, needed=3, changed_idx=0)

    assert spins[0].value() == 97
    assert spins[1].value() == 2
    assert spins[2].value() == 1
    assert sum(sp.value() for sp in spins[:3]) == 100