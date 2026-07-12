from types import SimpleNamespace

from app.services import main_window_score_workflow_service as workflow


def test_apply_initial_profile_weights_to_window_toggles_building(monkeypatch):
    calls = []
    weights = object()

    monkeypatch.setattr(
        workflow,
        "apply_initial_profile_weights",
        lambda weight_spins, total_weight: calls.append(
            ("apply", weight_spins, total_weight)
        ),
    )

    workflow.apply_initial_profile_weights_to_window(
        weight_spins=weights,
        total_weight=100,
        set_building=lambda value: calls.append(("building", value)),
    )

    assert calls == [
        ("building", True),
        ("apply", weights, 100),
        ("building", False),
    ]


def test_profile_selection_change_skips_while_building(monkeypatch):
    monkeypatch.setattr(
        workflow,
        "apply_profile_selection_change_workflow",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("should not run")),
    )

    state = workflow.handle_profile_selection_change_from_window(
        is_building=True,
        profile_combos=[],
        weight_spins=[],
        profiles={},
        selection_memory=[],
        mix_mode="1 profil",
        mix_modes={"1 profil": 1},
        set_building=lambda value: None,
    )

    assert state is None


def test_profile_weight_change_skips_while_building(monkeypatch):
    monkeypatch.setattr(
        workflow,
        "apply_profile_weight_change_workflow",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("should not run")),
    )

    handled = workflow.handle_profile_weight_change_from_window(
        is_building=True,
        weight_spins=[],
        changed_idx=0,
        new_value=50,
        mix_mode="1 profil",
        mix_modes={"1 profil": 1},
        set_building=lambda value: None,
    )

    assert handled is False


def test_reset_score_inputs_from_window_delegates(monkeypatch):
    expected = SimpleNamespace(
        selected_anime_result=None,
        selected_cover_pixmap=None,
        profile_selection_memory=["Balanced"],
        current_mix_needed=1,
    )
    calls = []
    monkeypatch.setattr(
        workflow,
        "reset_score_inputs_to_initial_state",
        lambda **kwargs: calls.append(kwargs) or expected,
    )

    result = workflow.reset_score_inputs_from_window(
        set_building=lambda value: None,
        title_edit=object(),
        title_search_controller=object(),
        mix_combo=object(),
        states=[],
        slider_widgets=[],
        spin_widgets=[],
        profile_combos=[],
        weight_spins=[],
        profile_names=("Balanced",),
        total_weight=100,
        update_profile_combo_options_func=lambda: None,
    )

    assert result is expected
    assert calls[0]["profile_names"] == ["Balanced"]
    assert calls[0]["total_weight"] == 100


def test_recompute_from_window_delegates(monkeypatch):
    expected = {"display_score": 8.0}
    calls = []
    monkeypatch.setattr(
        workflow,
        "recompute_result_and_update_views",
        lambda **kwargs: calls.append(kwargs) or expected,
    )

    result = workflow.recompute_from_window(
        profiles={},
        profile_combos=[],
        weight_spins=[],
        mix_mode="1 profil",
        mix_modes={"1 profil": 1},
        states=[],
        tier_thresholds={},
        ui_cfg={},
        title="Title",
        result_panel=object(),
        tier_board=object(),
        cover_pixmap=None,
        build_result_payload_func=lambda **kwargs: {},
    )

    assert result is expected
    assert calls[0]["title"] == "Title"
    assert calls[0]["mix_mode"] == "1 profil"


def test_add_current_result_from_window_delegates(monkeypatch):
    calls = []
    monkeypatch.setattr(
        workflow,
        "add_current_result_to_tier_board",
        lambda **kwargs: calls.append(kwargs),
    )

    workflow.add_current_result_from_window(
        parent=object(),
        tier_board=object(),
        title="Title",
        latest_result={"tier": "A"},
        recompute=lambda: None,
        get_latest_result=lambda: None,
        cover_pixmap=None,
    )

    assert calls[0]["title"] == "Title"
    assert calls[0]["latest_result"] == {"tier": "A"}
