import json

from app.core.constants import DEFAULT_UI
from app.core.runtime import app_dir
from app.logger import log_debug, log_warning, log_error


def load_ui_config():
    """
    Load UI configuration from config/ui.json.
    Returns: (ui_config, error_message)
    """
    config_path = app_dir() / "config" / "ui.json"

    if not config_path.exists():
        msg = f"UI config not found, using defaults: {config_path}"
        log_warning("config", msg)
        return DEFAULT_UI.copy(), msg

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        log_debug("config", f"UI config loaded from {config_path}")

        merged = DEFAULT_UI.copy()
        merged.update(data)
        return merged, None

    except Exception as e:
        msg = f"Failed to load UI config: {e}"
        log_error("config", msg)
        return DEFAULT_UI.copy(), msg