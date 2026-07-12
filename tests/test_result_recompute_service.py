import app.services.result_recompute_service as recompute_service


class FakeResultPanel:
    def __init__(self):
        self.update_calls = []

    def update_result(self, result, states):
        self.update_calls.append((result, states))


def _result():
    return {
        "selected": ["Balanced"],
        "ratios": [1.0],
        "values": [5.0, 6.0],
        "score": 7.25,
        "display_score": 7.3,
        "tier": "B",
    }


def test_recompute_result_and_update_views_builds_result_and_updates_views(
    monkeypatch,
):
    result = _result()
    result_panel = FakeResultPanel()
    tier_board = object()
    cover_pixmap = object()
    states = object()
    profile_combos = object()
    weight_spins = object()
    payload_calls = []
    preview_calls = []
    log_messages = []
    monkeypatch.setattr(
        recompute_service,
        "get_selected_profiles_and_ratios",
        lambda combos, spins, mode, modes: (["Balanced"], [1.0]),
    )
    monkeypatch.setattr(
        recompute_service,
        "update_tier_preview_entry",
        lambda **kwargs: preview_calls.append(kwargs),
    )
    monkeypatch.setattr(
        recompute_service,
        "log_debug",
        lambda component, message: log_messages.append((component, message)),
    )

    recomputed = recompute_service.recompute_result_and_update_views(
        profiles={"Balanced": []},
        profile_combos=profile_combos,
        weight_spins=weight_spins,
        mix_mode="1 profil",
        mix_modes={"1 profil": 1},
        states=states,
        tier_thresholds={"B": 7.0},
        ui_cfg={"dummy": True},
        title="  Cowboy Bebop  ",
        result_panel=result_panel,
        tier_board=tier_board,
        cover_pixmap=cover_pixmap,
        build_result_payload_func=lambda **kwargs: payload_calls.append(kwargs)
        or result,
    )

    assert recomputed is result
    assert payload_calls == [
        {
            "profiles": {"Balanced": []},
            "selected": ["Balanced"],
            "ratios": [1.0],
            "states": states,
            "tier_thresholds": {"B": 7.0},
            "ui_cfg": {"dummy": True},
            "title": "Cowboy Bebop",
        },
    ]
    assert result_panel.update_calls == [(result, states)]
    assert preview_calls == [
        {
            "tier_board": tier_board,
            "title": "  Cowboy Bebop  ",
            "result": result,
            "cover_pixmap": cover_pixmap,
        },
    ]
    assert log_messages == [
        (
            "recompute",
            "title='Cowboy Bebop' selected=['Balanced'] ratios=[1.0] "
            "vals=[5.0, 6.0] score=7.2500 tier=B display=7.30",
        ),
    ]
