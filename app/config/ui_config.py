import copy
import json

from app.core.constants import DEFAULT_UI
from app.core.runtime import app_dir
from app.logger import log_debug, log_warning, log_error


DEFAULT_WINDOW_CONFIG = {
    "default_width": 1600,
    "default_height": 720,
    "minimum_width": 1600,
    "minimum_height": 720,
}


def _merge_dicts(base: dict, override: dict) -> dict:
    merged = copy.deepcopy(base)

    for key, value in override.items():
        if (
            isinstance(value, dict)
            and isinstance(merged.get(key), dict)
        ):
            merged[key] = _merge_dicts(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)

    return merged


def _default_ui_config() -> dict:
    cfg = copy.deepcopy(DEFAULT_UI)
    cfg["window"] = _merge_dicts(DEFAULT_WINDOW_CONFIG, cfg.get("window", {}))
    return cfg


def load_ui_config():
    """
    Load UI configuration from config/ui.json.
    Returns: (ui_config, error_message)
    """
    config_path = app_dir() / "config" / "ui.json"

    if not config_path.exists():
        msg = f"UI config not found, using defaults: {config_path}"
        log_warning("config", msg)
        return _default_ui_config(), msg

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        log_debug("config", f"UI config loaded from {config_path}")

        merged = _merge_dicts(_default_ui_config(), data)
        return merged, None

    except Exception as e:
        msg = f"Failed to load UI config: {e}"
        log_error("config", msg)
        return _default_ui_config(), msg
