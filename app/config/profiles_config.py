import json

from app.core.runtime import app_dir
from app.logger import log_debug, log_error


def load_profiles_config():
    """
    Load profiles configuration from config/profiles.json.
    Returns: (dimensions, profiles, tier_thresholds, error_message)
    """
    config_path = app_dir() / "config" / "profiles.json"

    if not config_path.exists():
        msg = f"Profiles config file not found: {config_path}"
        log_error("config", msg)
        return None, None, None, msg

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        log_debug("config", f"Profiles config loaded from {config_path}")

        dimensions = data.get("dimensions")
        profiles = data.get("profiles")
        tier_thresholds = data.get("tier_thresholds")

        if not isinstance(dimensions, list) or not dimensions:
            raise ValueError("Invalid 'dimensions' list in profiles.json")

        if not isinstance(profiles, dict) or not profiles:
            raise ValueError("Invalid 'profiles' section in profiles.json")

        if not isinstance(tier_thresholds, dict) or not tier_thresholds:
            raise ValueError("Invalid 'tier_thresholds' section in profiles.json")

        dim_count = len(dimensions)

        for profile_name, weights in profiles.items():
            if not isinstance(weights, list):
                raise ValueError(f"Profile '{profile_name}' weights must be a list")
            if len(weights) != dim_count:
                raise ValueError(
                    f"Profile '{profile_name}' has {len(weights)} weights but "
                    f"{dim_count} dimensions exist"
                )

        return dimensions, profiles, tier_thresholds, None

    except Exception as e:
        msg = f"Failed to load profiles config: {e}"
        log_error("config", msg)
        return None, None, None, msg