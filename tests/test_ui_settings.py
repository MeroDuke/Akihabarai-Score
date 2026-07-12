from app.config.ui_settings import (
    get_anilist_int_setting,
    get_anilist_text_setting,
    get_config_section,
    get_positive_int_setting,
    get_text_setting,
    get_window_size,
    is_anilist_integration_enabled,
)


def test_get_config_section_returns_dict_section():
    assert get_config_section({"window": {"default_width": 1600}}, "window") == {
        "default_width": 1600,
    }


def test_get_config_section_falls_back_for_missing_or_invalid_section():
    assert get_config_section({}, "window") == {}
    assert get_config_section({"window": []}, "window") == {}


def test_get_positive_int_setting_accepts_positive_int_like_values():
    section = {
        "int_value": 42,
        "string_value": "43",
    }

    assert get_positive_int_setting(section, "int_value", 1) == 42
    assert get_positive_int_setting(section, "string_value", 1) == 43


def test_get_positive_int_setting_falls_back_for_invalid_values():
    section = {
        "bool_value": True,
        "zero_value": 0,
        "negative_value": -1,
        "text_value": "invalid",
        "none_value": None,
    }

    assert get_positive_int_setting(section, "bool_value", 99) == 99
    assert get_positive_int_setting(section, "zero_value", 99) == 99
    assert get_positive_int_setting(section, "negative_value", 99) == 99
    assert get_positive_int_setting(section, "text_value", 99) == 99
    assert get_positive_int_setting(section, "none_value", 99) == 99
    assert get_positive_int_setting(section, "missing_value", 99) == 99


def test_get_text_setting_accepts_non_empty_strings():
    assert get_text_setting({"placeholder": "AniList keresés..."}, "placeholder", "fallback") == "AniList keresés..."


def test_get_text_setting_falls_back_for_blank_or_non_string_values():
    assert get_text_setting({"placeholder": ""}, "placeholder", "fallback") == "fallback"
    assert get_text_setting({"placeholder": "   "}, "placeholder", "fallback") == "fallback"
    assert get_text_setting({"placeholder": 123}, "placeholder", "fallback") == "fallback"
    assert get_text_setting({}, "placeholder", "fallback") == "fallback"


def test_is_anilist_integration_enabled_defaults_to_true():
    assert is_anilist_integration_enabled({}) is True
    assert is_anilist_integration_enabled({"features": []}) is True


def test_is_anilist_integration_enabled_reads_feature_flag():
    assert is_anilist_integration_enabled({"features": {"anilist_enabled": True}}) is True
    assert is_anilist_integration_enabled({"features": {"anilist_enabled": False}}) is False


def test_get_window_size_reads_positive_config_values():
    ui_cfg = {
        "window": {
            "default_width": "1920",
            "default_height": 1080,
        }
    }

    assert get_window_size(
        ui_cfg,
        width_key="default_width",
        height_key="default_height",
        default_width=1600,
        default_height=720,
    ) == (1920, 1080)


def test_get_window_size_falls_back_for_invalid_config_values():
    ui_cfg = {
        "window": {
            "default_width": False,
            "default_height": 0,
        }
    }

    assert get_window_size(
        ui_cfg,
        width_key="default_width",
        height_key="default_height",
        default_width=1600,
        default_height=720,
    ) == (1600, 720)


def test_anilist_settings_read_from_anilist_section():
    ui_cfg = {
        "anilist": {
            "title_placeholder_online": "Online keresés",
            "title_search_debounce_ms": "750",
        }
    }

    assert get_anilist_text_setting(
        ui_cfg,
        "title_placeholder_online",
        "fallback",
    ) == "Online keresés"
    assert get_anilist_int_setting(
        ui_cfg,
        "title_search_debounce_ms",
        1000,
    ) == 750
