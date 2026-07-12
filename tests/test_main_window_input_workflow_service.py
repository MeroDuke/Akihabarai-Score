from types import SimpleNamespace

from app.services import main_window_input_workflow_service as workflow


class FakeCombo:
    def __init__(self, text="1 profil"):
        self._text = text

    def currentText(self):
        return self._text


def _make_window():
    window = SimpleNamespace()
    window._building = False
    window.profile_combos = ["combo"]
    window.weight_spins = ["weight"]
    window.profiles = {"Balanced": [1.0]}
    window.profile_selection_memory = ["Balanced"]
    window.current_mix_needed = 1
    window.mix_combo = FakeCombo("1 profil")
    window.states = ["state"]
    window.slider_widgets = ["slider"]
    window.spin_widgets = ["spin"]
    window.recompute_calls = 0
    window.recompute = lambda: setattr(
        window,
        "recompute_calls",
        window.recompute_calls + 1,
    )
    return window


def test_handle_mix_change_updates_state_and_recomputes(monkeypatch):
    window = _make_window()
    returned_state = SimpleNamespace(
        selection_memory=["Visual"],
        current_mix_needed=2,
    )
    calls = []
    monkeypatch.setattr(
        workflow,
        "handle_mix_mode_change_from_window",
        lambda **kwargs: calls.append(kwargs) or returned_state,
    )

    workflow.handle_mix_change_for_window(
        window,
        mix_modes={"1 profil": 1, "2 profil": 2},
        total_weight=100,
    )

    assert calls[0]["profile_combos"] == ["combo"]
    assert calls[0]["mix_mode"] == "1 profil"
    assert calls[0]["current_mix_needed"] == 1
    assert window.profile_selection_memory == ["Visual"]
    assert window.current_mix_needed == 2
    assert window.recompute_calls == 1


def test_handle_profile_change_skips_recompute_when_state_is_none(monkeypatch):
    window = _make_window()
    monkeypatch.setattr(
        workflow,
        "handle_profile_selection_change_from_window",
        lambda **kwargs: None,
    )

    workflow.handle_profile_change_for_window(window, mix_modes={"1 profil": 1})

    assert window.profile_selection_memory == ["Balanced"]
    assert window.recompute_calls == 0


def test_handle_profile_change_updates_memory_and_recomputes(monkeypatch):
    window = _make_window()
    monkeypatch.setattr(
        workflow,
        "handle_profile_selection_change_from_window",
        lambda **kwargs: SimpleNamespace(selection_memory=["Drama"]),
    )

    workflow.handle_profile_change_for_window(window, mix_modes={"1 profil": 1})

    assert window.profile_selection_memory == ["Drama"]
    assert window.recompute_calls == 1


def test_weight_and_dimension_changes_recompute_only_when_handled(monkeypatch):
    window = _make_window()
    calls = []
    monkeypatch.setattr(
        workflow,
        "handle_profile_weight_change_from_window",
        lambda **kwargs: calls.append(("weight", kwargs)) or True,
    )
    monkeypatch.setattr(
        workflow,
        "handle_dimension_slider_change_from_window",
        lambda **kwargs: calls.append(("slider", kwargs)) or False,
    )
    monkeypatch.setattr(
        workflow,
        "handle_dimension_spin_change_from_window",
        lambda **kwargs: calls.append(("spin", kwargs)) or True,
    )

    workflow.handle_profile_weight_change_for_window(
        window,
        changed_idx=0,
        new_value=70,
        mix_modes={"1 profil": 1},
    )
    workflow.handle_dimension_slider_change_for_window(
        window,
        index=0,
        slider_value=73,
    )
    workflow.handle_dimension_spin_change_for_window(
        window,
        index=0,
        spin_value=8.2,
    )

    assert calls[0][1]["changed_idx"] == 0
    assert calls[0][1]["new_value"] == 70
    assert calls[1][1]["slider_value"] == 73
    assert calls[2][1]["spin_value"] == 8.2
    assert window.recompute_calls == 2


def test_reset_score_inputs_updates_window_state_and_reruns_mix(monkeypatch):
    window = _make_window()
    window.title_edit = object()
    window.title_search_controller = object()
    window.on_mix_calls = 0
    window.on_mix_changed = lambda: setattr(
        window,
        "on_mix_calls",
        window.on_mix_calls + 1,
    )
    window._update_profile_combo_options_internal = lambda: None
    returned_state = SimpleNamespace(
        selected_anime_result=None,
        selected_cover_pixmap=None,
        profile_selection_memory=["Balanced"],
        current_mix_needed=1,
    )
    calls = []
    monkeypatch.setattr(
        workflow,
        "reset_score_inputs_from_window",
        lambda **kwargs: calls.append(kwargs) or returned_state,
    )

    workflow.reset_score_inputs_for_window(
        window,
        total_weight=100,
    )

    assert calls[0]["profile_names"] == ["Balanced"]
    assert calls[0]["total_weight"] == 100
    assert window.selected_anime_result is None
    assert window.selected_cover_pixmap is None
    assert window.profile_selection_memory == ["Balanced"]
    assert window.current_mix_needed == 1
    assert window.on_mix_calls == 1
