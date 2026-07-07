def get_config_section(ui_cfg: dict, key: str) -> dict:
    section = ui_cfg.get(key)
    if not isinstance(section, dict):
        return {}

    return section


def get_positive_int_setting(section: dict, key: str, default: int) -> int:
    value = section.get(key, default)
    if isinstance(value, bool):
        return default

    try:
        parsed_value = int(value)
    except (TypeError, ValueError):
        return default

    if parsed_value <= 0:
        return default

    return parsed_value


def get_text_setting(section: dict, key: str, default: str) -> str:
    value = section.get(key, default)
    if not isinstance(value, str) or not value.strip():
        return default

    return value


def is_anilist_integration_enabled(ui_cfg: dict) -> bool:
    features = get_config_section(ui_cfg, "features")
    if not features:
        return True

    return bool(features.get("anilist_enabled", True))


def get_window_size(
    ui_cfg: dict,
    *,
    width_key: str,
    height_key: str,
    default_width: int,
    default_height: int,
) -> tuple[int, int]:
    window_cfg = get_config_section(ui_cfg, "window")
    return (
        get_positive_int_setting(window_cfg, width_key, default_width),
        get_positive_int_setting(window_cfg, height_key, default_height),
    )


def get_anilist_text_setting(ui_cfg: dict, key: str, default: str) -> str:
    return get_text_setting(
        get_config_section(ui_cfg, "anilist"),
        key,
        default,
    )


def get_anilist_int_setting(ui_cfg: dict, key: str, default: int) -> int:
    return get_positive_int_setting(
        get_config_section(ui_cfg, "anilist"),
        key,
        default,
    )
