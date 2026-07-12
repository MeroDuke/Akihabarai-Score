from types import SimpleNamespace

from app.services.main_window_lifecycle_service import (
    apply_main_window_config_to_window,
    bind_main_window_layout_widgets,
    finish_main_window_startup,
    initialize_main_window_after_layout,
    initialize_main_window_runtime_state,
)


def test_apply_main_window_config_sets_runtime_config_fields():
    window = SimpleNamespace(TITLE_INPUT_MODE_OFFLINE="offline")
    config = SimpleNamespace(
        dimensions=["Történet / plot"],
        profiles={"Balanced": [1.0]},
        tier_thresholds={"A": 8.0},
        ui_cfg={"dummy": True},
        anilist_integration_enabled=False,
        title_placeholder_offline="Offline cím",
        title_placeholder_online="Online cím",
        title_search_debounce_ms=750,
        title_max_length=120,
        default_window_size=(1600, 720),
        minimum_window_size=(1280, 720),
    )

    apply_main_window_config_to_window(window, config)

    assert window.dimensions == ["Történet / plot"]
    assert window.profiles == {"Balanced": [1.0]}
    assert window.anilist_integration_enabled is False
    assert window.title_placeholder_offline == "Offline cím"
    assert window.title_placeholder_online == "Online cím"
    assert window.title_input_mode == "offline"
    assert window.selected_anime_result is None
    assert window.selected_cover_pixmap is None
    assert window.title_search_controller is None


def test_initialize_main_window_runtime_state_sets_defaults():
    window = SimpleNamespace(
        dimensions=["Történet / plot", "Karakterek"],
        profiles={"Balanced": [1.0, 1.0]},
    )

    initialize_main_window_runtime_state(
        window,
        lambda name: SimpleNamespace(name=name, value=5.0),
    )

    assert [state.name for state in window.states] == [
        "Történet / plot",
        "Karakterek",
    ]
    assert window._building is True
    assert window.profile_combos == []
    assert window.weight_spins == []
    assert window.slider_widgets == []
    assert window.spin_widgets == []
    assert window.profile_names == ["Balanced"]
    assert window.profile_selection_memory == ["Balanced", "Balanced", "Balanced"]
    assert window.current_mix_needed == 1


def test_bind_main_window_layout_widgets_copies_panel_references():
    top_inputs_panel = SimpleNamespace(
        title_edit=object(),
        title_mode_btn=object(),
        mix_combo=object(),
    )
    profile_mix_panel = SimpleNamespace(
        profile_combos=[object()],
        weight_spins=[object()],
    )
    dimensions_panel = SimpleNamespace(
        slider_widgets=[object()],
        spin_widgets=[object()],
    )
    action_buttons_panel = SimpleNamespace(
        version_btn=object(),
        reset_btn=object(),
        add_tier_btn=object(),
    )
    result_panel = SimpleNamespace(
        score_label=object(),
        tier_label=object(),
        summary_label=object(),
        result_card=object(),
        copy_img_btn=object(),
        table=object(),
        copy_btn=object(),
    )
    tier_panel = SimpleNamespace(
        tier_board=object(),
        tier_scroll_area=object(),
        flip_all_tier_cards_btn=object(),
        clear_all_tier_cards_btn=object(),
        copy_tier_btn=object(),
    )
    layout = SimpleNamespace(
        main_layout=object(),
        left_box=object(),
        left_layout=object(),
        top_inputs_panel=top_inputs_panel,
        profile_mix_panel=profile_mix_panel,
        dimensions_panel=dimensions_panel,
        action_buttons_panel=action_buttons_panel,
        result_panel=result_panel,
        right_box=result_panel,
        tier_panel=tier_panel,
        tier_box=tier_panel,
    )
    window = SimpleNamespace()

    bind_main_window_layout_widgets(window, layout)

    assert window.top_inputs_panel is top_inputs_panel
    assert window.profile_mix_panel is profile_mix_panel
    assert window.dimensions_panel is dimensions_panel
    assert window.action_buttons_panel is action_buttons_panel
    assert window.result_panel is result_panel
    assert window.tier_panel is tier_panel
    assert window.title_edit is top_inputs_panel.title_edit
    assert window.version_btn is action_buttons_panel.version_btn
    assert window.table is result_panel.table
    assert window.copy_tier_btn is tier_panel.copy_tier_btn


def test_initialize_main_window_after_layout_runs_title_setup_steps():
    events = []
    window = SimpleNamespace(
        title_edit=SimpleNamespace(text=lambda: "Cowboy Bebop"),
        _setup_title_autocomplete=lambda: events.append("setup"),
        _sync_title_mode_ui=lambda log_change: events.append(("sync", log_change)),
        update_add_tier_button_state=lambda title: events.append(
            ("add_button", title)
        ),
    )

    initialize_main_window_after_layout(window)

    assert events == ["setup", ("sync", False), ("add_button", "Cowboy Bebop")]


def test_finish_main_window_startup_preserves_startup_order():
    events = []
    window = SimpleNamespace(
        _building=True,
        _post_init_config_messages=lambda profiles_error, ui_error: events.append(
            ("messages", profiles_error, ui_error)
        ),
        _apply_initial_weights=lambda: events.append("weights"),
        on_mix_changed=lambda: events.append("mix"),
        check_for_updates=lambda: events.append("updates"),
    )

    finish_main_window_startup(
        window,
        profiles_error="profiles warning",
        ui_error="ui warning",
        schedule_update_check=lambda delay, callback: events.append(
            ("schedule", delay, callback)
        ),
    )

    assert window._building is False
    assert events[:4] == [
        ("messages", "profiles warning", "ui warning"),
        "weights",
        "mix",
        ("schedule", 250, window.check_for_updates),
    ]
