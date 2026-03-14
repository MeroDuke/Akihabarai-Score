# tests/test_profiles_config.py
import json

import app.config.profiles_config as profiles_config_module
from app.config.profiles_config import load_profiles_config
from app.core.constants import DEFAULT_DIMENSIONS, DEFAULT_TIERS


def test_load_profiles_config_missing_file_returns_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr(profiles_config_module, "app_dir", lambda: tmp_path)

    dims, profiles, tiers, err = load_profiles_config()

    assert dims == DEFAULT_DIMENSIONS
    assert profiles == {}
    assert tiers == DEFAULT_TIERS
    assert err is not None


def test_load_profiles_config_valid_json_loads_successfully(tmp_path, monkeypatch):
    monkeypatch.setattr(profiles_config_module, "app_dir", lambda: tmp_path)

    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()

    data = {
        "dimensions": ["Dim A", "Dim B"],
        "profiles": {
            "Fantasy": [1.0, 0.8],
            "Dráma": [0.7, 1.0],
        },
        "tiers": {
            "S": 9.0,
            "A": 8.0,
            "B": 7.0,
        },
    }

    (cfg_dir / "profiles.json").write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8",
    )

    dims, profiles, tiers, err = load_profiles_config()

    assert err is None
    assert dims == ["Dim A", "Dim B"]
    assert profiles == {
        "Fantasy": [1.0, 0.8],
        "Dráma": [0.7, 1.0],
    }
    assert tiers == {
        "S": 9.0,
        "A": 8.0,
        "B": 7.0,
    }


def test_load_profiles_config_invalid_json_falls_back_to_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr(profiles_config_module, "app_dir", lambda: tmp_path)

    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "profiles.json").write_text("{ invalid json }", encoding="utf-8")

    dims, profiles, tiers, err = load_profiles_config()

    assert dims == DEFAULT_DIMENSIONS
    assert profiles == {}
    assert tiers == DEFAULT_TIERS
    assert err is not None


def test_load_profiles_config_missing_sections_fall_back_to_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr(profiles_config_module, "app_dir", lambda: tmp_path)

    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()

    data = {
        "profiles": {
            "Fantasy": [1.0, 0.8],
        }
    }

    (cfg_dir / "profiles.json").write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8",
    )

    dims, profiles, tiers, err = load_profiles_config()

    assert err is None
    assert dims == DEFAULT_DIMENSIONS
    assert profiles == {"Fantasy": [1.0, 0.8]}
    assert tiers == DEFAULT_TIERS