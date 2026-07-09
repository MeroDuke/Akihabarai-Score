from app.services.main_window_config_service import load_main_window_config


def _load_profiles_config():
    return (
        ["Story", "Visuals"],
        {"Balanced": [1.0, 1.0]},
        {"A": 8.0},
        None,
    )


def test_load_main_window_config_reads_ui_settings():
    ui_cfg = {
        "window": {
            "default_width": "1800",
            "default_height": 900,
            "minimum_width": 1280,
            "minimum_height": "720",
        },
        "features": {
            "anilist_enabled": False,
        },
        "anilist": {
            "title_placeholder_offline": "Offline cím",
            "title_placeholder_online": "Online cím",
            "title_search_debounce_ms": "750",
            "title_max_length": "120",
        },
    }

    config = load_main_window_config(
        load_profiles_config_func=_load_profiles_config,
        load_ui_config_func=lambda: (ui_cfg, None),
        default_title_placeholder_offline="offline fallback",
        default_title_placeholder_online="online fallback",
        default_title_search_debounce_ms=1000,
        default_title_max_length=80,
        default_window_width=1600,
        default_window_height=720,
        default_minimum_window_width=1600,
        default_minimum_window_height=720,
    )

    assert config.profiles_config_loaded is True
    assert config.anilist_integration_enabled is False
    assert config.title_placeholder_offline == "Offline cím"
    assert config.title_placeholder_online == "Online cím"
    assert config.title_search_debounce_ms == 750
    assert config.title_max_length == 120
    assert config.default_window_size == (1800, 900)
    assert config.minimum_window_size == (1280, 720)


def test_load_main_window_config_falls_back_for_missing_ui_settings():
    config = load_main_window_config(
        load_profiles_config_func=_load_profiles_config,
        load_ui_config_func=lambda: ({}, "ui warning"),
        default_title_placeholder_offline="offline fallback",
        default_title_placeholder_online="online fallback",
        default_title_search_debounce_ms=1000,
        default_title_max_length=80,
        default_window_width=1600,
        default_window_height=720,
        default_minimum_window_width=1600,
        default_minimum_window_height=720,
    )

    assert config.ui_error == "ui warning"
    assert config.anilist_integration_enabled is True
    assert config.title_placeholder_offline == "offline fallback"
    assert config.title_placeholder_online == "online fallback"
    assert config.title_search_debounce_ms == 1000
    assert config.title_max_length == 80
    assert config.default_window_size == (1600, 720)
    assert config.minimum_window_size == (1600, 720)


def test_load_main_window_config_reports_missing_profiles_config():
    config = load_main_window_config(
        load_profiles_config_func=lambda: (None, None, None, "broken profiles"),
        load_ui_config_func=lambda: ({}, None),
        default_title_placeholder_offline="offline fallback",
        default_title_placeholder_online="online fallback",
        default_title_search_debounce_ms=1000,
        default_title_max_length=80,
        default_window_width=1600,
        default_window_height=720,
        default_minimum_window_width=1600,
        default_minimum_window_height=720,
    )

    assert config.profiles_config_loaded is False
    assert config.profiles_error == "broken profiles"
