from app.services.profile_mix_service import (
    build_profile_combo_options,
    change_profile_weight,
    default_profile_selection_memory,
    normalize_profile_weights,
    rebalance_profile_weights,
    remember_profile_selections,
    select_profiles_and_ratios,
)


def test_get_selected_profiles_and_ratios_single_profile():
    profiles = ["Fantasy", "Drama", "Action"]
    weights = [100, 0, 0]
    mix_modes = {"1 profil": 1, "2 profil": 2, "3 profil": 3}

    selected, ratios = select_profiles_and_ratios(
        profiles, weights, "1 profil", mix_modes
    )

    assert selected == ["Fantasy"]
    assert ratios == [1.0]


def test_default_profile_selection_memory_prefills_available_profiles():
    memory = default_profile_selection_memory(["Balanced", "Visual"], slots=3)

    assert memory == ["Balanced", "Visual", "Balanced"]


def test_default_profile_selection_memory_handles_missing_profiles():
    memory = default_profile_selection_memory([], slots=3)

    assert memory == [None, None, None]


def test_remember_profile_selections_updates_only_active_valid_profiles():
    memory = ["Balanced", "Visual", "Drama"]

    updated = remember_profile_selections(
        memory=memory,
        current_profiles=["Action", "Invalid", "Story"],
        all_profiles=["Balanced", "Visual", "Drama", "Action", "Story"],
        needed=2,
    )

    assert updated == ["Action", "Visual", "Drama"]
    assert memory == ["Balanced", "Visual", "Drama"]


def test_build_profile_combo_options_keeps_unique_current_profiles():
    options = build_profile_combo_options(
        all_profiles=["Balanced", "Visual", "Drama"],
        current_profiles=["Drama", "Visual", "Balanced"],
        needed=3,
    )

    assert options == [
        (["Drama"], "Drama"),
        (["Visual"], "Visual"),
        (["Balanced"], "Balanced"),
    ]


def test_build_profile_combo_options_replaces_duplicate_and_invalid_profiles():
    options = build_profile_combo_options(
        all_profiles=["Balanced", "Visual", "Drama"],
        current_profiles=["Balanced", "Balanced", "Missing"],
        needed=3,
    )

    assert options == [
        (["Balanced"], "Balanced"),
        (["Visual"], "Visual"),
        (["Drama"], "Drama"),
    ]


def test_build_profile_combo_options_marks_inactive_rows_without_options():
    options = build_profile_combo_options(
        all_profiles=["Balanced", "Visual", "Drama"],
        current_profiles=["Balanced", "Visual", "Drama"],
        needed=1,
    )

    assert options == [
        (["Balanced", "Visual", "Drama"], "Balanced"),
        ([], "Balanced"),
        ([], "Balanced"),
    ]


def test_get_selected_profiles_and_ratios_two_profiles():
    profiles = ["Fantasy", "Drama", "Action"]
    weights = [60, 40, 0]
    mix_modes = {"1 profil": 1, "2 profil": 2, "3 profil": 3}

    selected, ratios = select_profiles_and_ratios(
        profiles, weights, "2 profil", mix_modes
    )

    assert selected == ["Fantasy", "Drama"]
    assert ratios == [0.6, 0.4]


def test_get_selected_profiles_and_ratios_zero_weights_fallback_equal_split():
    profiles = ["Fantasy", "Drama", "Action"]
    weights = [0, 0, 0]
    mix_modes = {"1 profil": 1, "2 profil": 2, "3 profil": 3}

    selected, ratios = select_profiles_and_ratios(
        profiles, weights, "2 profil", mix_modes
    )

    assert selected == ["Fantasy", "Drama"]
    assert ratios == [1.0, 0.0]


def test_force_total_weight_single_profile_forces_100():
    result = rebalance_profile_weights([25, 0, 0], needed=1, changed_idx=0)
    assert result == [100, 0, 0]


def test_force_total_weight_two_profiles_adjusts_other_spin():
    result = rebalance_profile_weights([70, 20, 0], needed=2, changed_idx=0)
    assert result == [70, 30, 0]


def test_force_total_weight_three_profiles_fills_deficit_into_smallest_other():
    result = rebalance_profile_weights([50, 30, 10], needed=3, changed_idx=1)
    assert result == [50, 30, 20]


def test_force_total_weight_overflow_reduces_largest_other_not_changed_spin():
    result = rebalance_profile_weights([10, 80, 50], needed=3, changed_idx=2)
    assert result == [10, 40, 50]


def test_force_total_weight_tie_break_prefers_leftmost_largest_spin():
    result = rebalance_profile_weights([34, 34, 34], needed=3, changed_idx=2)
    assert result == [33, 33, 34]


def test_force_total_weight_deficit_increases_smallest_other_stepwise():
    result = rebalance_profile_weights([98, 0, 0], needed=3, changed_idx=0)
    assert result == [98, 1, 1]


def test_force_total_weight_deficit_tie_break_prefers_leftmost_smallest_spin():
    result = rebalance_profile_weights([99, 0, 0], needed=3, changed_idx=0)
    assert result == [99, 1, 0]


def test_force_total_weight_deficit_after_reduction_keeps_distribution_balanced():
    result = rebalance_profile_weights([97, 0, 0], needed=3, changed_idx=0)
    assert result == [97, 2, 1]


def test_normalize_active_profile_weights_restores_total_when_active_sum_is_zero():
    result = normalize_profile_weights([0, 0, 25], needed=2, total_weight=100)
    assert result == [100, 0, 25]


def test_normalize_active_profile_weights_forces_active_weights_to_total():
    result = normalize_profile_weights([70, 20, 50], needed=2, total_weight=100)
    assert result == [70, 30, 50]


def test_apply_profile_weight_change_forces_active_weights_to_total():
    mix_modes = {"1 profil": 1, "2 profil": 2, "3 profil": 3}

    outcome = change_profile_weight(
        [70, 20, 50],
        changed_idx=0,
        mix_mode="2 profil",
        mix_modes=mix_modes,
    )

    assert outcome.handled is True
    assert outcome.weights == [70, 30, 50]


def test_apply_profile_weight_change_ignores_inactive_weight():
    mix_modes = {"1 profil": 1, "2 profil": 2, "3 profil": 3}

    outcome = change_profile_weight(
        [70, 30, 50],
        changed_idx=2,
        mix_mode="2 profil",
        mix_modes=mix_modes,
    )

    assert outcome.handled is False
    assert outcome.weights == [70, 30, 50]


def test_change_profile_weight_ignores_negative_index():
    original = [70, 30, 50]

    outcome = change_profile_weight(
        original,
        changed_idx=-1,
        mix_mode="2 profil",
        mix_modes={"2 profil": 2},
    )

    assert outcome.handled is False
    assert outcome.weights == original
    assert outcome.weights is not original


def test_rebalance_profile_weights_does_not_mutate_input():
    original = [50, 30, 10]

    result = rebalance_profile_weights(
        original,
        needed=3,
        changed_idx=1,
    )

    assert result == [50, 30, 20]
    assert original == [50, 30, 10]


def test_normalize_profile_weights_supports_custom_total():
    result = normalize_profile_weights(
        [30, 10, 25],
        needed=2,
        total_weight=50,
    )

    assert result == [30, 20, 25]
