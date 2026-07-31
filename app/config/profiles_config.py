import json
from dataclasses import dataclass, field

from app.core.runtime import app_dir
from app.logger import log_debug, log_error


@dataclass
class ProfilesConfigResult:
    dimensions: list[str] | None
    profiles: dict | None
    tier_thresholds: dict | None
    error: str | None
    dimension_labels: dict[str, str] = field(default_factory=dict)
    profile_labels: dict[str, str] = field(default_factory=dict)

    def __iter__(self):
        yield self.dimensions
        yield self.profiles
        yield self.tier_thresholds
        yield self.error


def _parse_dimensions(payload) -> tuple[list[str], dict[str, str]]:
    if not isinstance(payload, list) or not payload:
        raise ValueError("Invalid 'dimensions' list in profiles.json")

    identifiers = []
    labels = {}
    for item in payload:
        if isinstance(item, str) and item.strip():
            identifier = item
            label = item
        elif isinstance(item, dict):
            identifier = item.get("id")
            label = item.get("label")
            if not isinstance(identifier, str) or not identifier.strip():
                raise ValueError("Dimension entries must have a non-empty 'id'")
            if not isinstance(label, str) or not label.strip():
                raise ValueError(
                    f"Dimension '{identifier}' must have a non-empty 'label'"
                )
        else:
            raise ValueError("Invalid dimension entry in profiles.json")

        if identifier in labels:
            raise ValueError(f"Duplicate dimension id: {identifier}")
        identifiers.append(identifier)
        labels[identifier] = label

    return identifiers, labels


def _parse_profiles(payload) -> tuple[dict[str, list], dict[str, str]]:
    if not isinstance(payload, dict) or not payload:
        raise ValueError("Invalid 'profiles' section in profiles.json")

    profiles = {}
    labels = {}
    for identifier, item in payload.items():
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError("Profile ids must be non-empty strings")

        if isinstance(item, list):
            weights = item
            label = identifier
        elif isinstance(item, dict):
            weights = item.get("weights")
            label = item.get("label")
            if not isinstance(label, str) or not label.strip():
                raise ValueError(
                    f"Profile '{identifier}' must have a non-empty 'label'"
                )
        else:
            raise ValueError(
                f"Profile '{identifier}' must be a weight list or object"
            )

        if not isinstance(weights, list):
            raise ValueError(f"Profile '{identifier}' weights must be a list")
        profiles[identifier] = weights
        labels[identifier] = label

    return profiles, labels


def load_profiles_config():
    """
    Load profiles configuration from config/profiles.json.
    Returns: (dimensions, profiles, tier_thresholds, error_message)
    """
    config_path = app_dir() / "config" / "profiles.json"

    if not config_path.exists():
        msg = f"Profiles config file not found: {config_path}"
        log_error("config", msg)
        return ProfilesConfigResult(None, None, None, msg)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        log_debug("config", f"Profiles config loaded from {config_path}")

        dimensions, dimension_labels = _parse_dimensions(data.get("dimensions"))
        profiles, profile_labels = _parse_profiles(data.get("profiles"))
        tier_thresholds = data.get("tier_thresholds")

        if not isinstance(tier_thresholds, dict) or not tier_thresholds:
            raise ValueError("Invalid 'tier_thresholds' section in profiles.json")

        dim_count = len(dimensions)

        for profile_name, weights in profiles.items():
            if len(weights) != dim_count:
                raise ValueError(
                    f"Profile '{profile_name}' has {len(weights)} weights but "
                    f"{dim_count} dimensions exist"
                )

        return ProfilesConfigResult(
            dimensions,
            profiles,
            tier_thresholds,
            None,
            dimension_labels=dimension_labels,
            profile_labels=profile_labels,
        )

    except Exception as e:
        msg = f"Failed to load profiles config: {e}"
        log_error("config", msg)
        return ProfilesConfigResult(None, None, None, msg)
