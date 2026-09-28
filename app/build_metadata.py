"""Load immutable build identity without importing the Qt application."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


UNKNOWN = "unknown"
BUILD_INFO_FILENAME = "build-info.json"
EXPECTED_SCHEMA_VERSION = 1


def bundled_build_info_path() -> Path:
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root) / BUILD_INFO_FILENAME
    return Path(__file__).resolve().parents[1] / BUILD_INFO_FILENAME


def load_build_info(path: Path | None = None) -> dict[str, str]:
    """Return validated build identity, falling back to explicit unknowns."""
    defaults = {
        "build_commit": UNKNOWN,
        "build_ref": UNKNOWN,
        "build_run_id": UNKNOWN,
        "build_timestamp": UNKNOWN,
    }
    target = path or bundled_build_info_path()
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
        if payload.get("schema_version") != EXPECTED_SCHEMA_VERSION:
            return defaults
        for key in defaults:
            value = payload.get(key.removeprefix("build_"), UNKNOWN)
            if isinstance(value, str) and value.strip():
                defaults[key] = value.strip()
    except (OSError, ValueError, TypeError):
        pass

    # Explicit environment values are useful for development and tests. The
    # packaged release normally reads the immutable embedded JSON instead.
    for key in defaults:
        environment_value = os.environ.get(f"AKIHABARAI_{key.upper()}")
        if environment_value:
            defaults[key] = environment_value.strip()
    return defaults
