import json

from app.core.constants import DEFAULT_DIMENSIONS, DEFAULT_TIERS
from app.core.runtime import app_dir
from app.logger import log_debug, log_warning, log_error


def load_profiles_config():
    """
    Load profiles configuration from config/profiles.json.
    Returns: (dimensions, profiles, tier_thresholds, error_message)
    """
    config_path = app_dir() / "config" / "profiles.json"

    if not config_path.exists():
        msg = f"Profiles config not found, using defaults: {config_path}"
        log_warning("config", msg)
        return DEFAULT_DIMENSIONS, {}, DEFAULT_TIERS, msg

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        log_debug("config", f"Profiles config loaded from {config_path}")

        dimensions = data.get("dimensions", DEFAULT_DIMENSIONS)
        profiles = data.get("profiles", {})
        tiers = data.get("tiers", DEFAULT_TIERS)

        return dimensions, profiles, tiers, None

    except Exception as e:
        msg = f"Failed to load profiles config: {e}"
        log_error("config", msg)
        return DEFAULT_DIMENSIONS, {}, DEFAULT_TIERS, msg