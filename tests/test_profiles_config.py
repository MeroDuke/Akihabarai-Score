import json
from pathlib import Path

import app.config.profiles_config as profiles_config_module
from app.config.profiles_config import load_profiles_config


REPO_ROOT = Path(__file__).resolve().parents[1]
TEXT_FILE_SUFFIXES = {".json", ".md", ".py"}
SKIPPED_TEXT_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    "build",
    "dist",
    "htmlcov",
}


def _iter_repo_text_files():
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_FILE_SUFFIXES:
            continue
        if any(part in SKIPPED_TEXT_DIRS for part in path.relative_to(REPO_ROOT).parts):
            continue
        yield path


def test_load_profiles_config_missing_file_returns_error(tmp_path, monkeypatch):
    monkeypatch.setattr(profiles_config_module, "app_dir", lambda: tmp_path)

    dims, profiles, tiers, err = load_profiles_config()

    assert dims is None
    assert profiles is None
    assert tiers is None
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
        "tier_thresholds": {
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


def test_episode_rhythm_label_uses_correct_hungarian_spelling():
    wrong_episode_rhythm_label = "epizód" + "rítmus"
    correct_episode_rhythm_label = "epizódritmus"

    profiles_text = (REPO_ROOT / "config" / "profiles.json").read_text(
        encoding="utf-8"
    )
    readme_text = (REPO_ROOT / "readme.md").read_text(encoding="utf-8")

    assert correct_episode_rhythm_label in profiles_text
    assert correct_episode_rhythm_label in readme_text

    matches = []
    for path in _iter_repo_text_files():
        text = path.read_text(encoding="utf-8")
        if wrong_episode_rhythm_label in text:
            matches.append(str(path.relative_to(REPO_ROOT)))

    assert matches == []


def test_load_profiles_config_invalid_json_returns_error(tmp_path, monkeypatch):
    monkeypatch.setattr(profiles_config_module, "app_dir", lambda: tmp_path)

    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()

    (cfg_dir / "profiles.json").write_text("{ invalid json }", encoding="utf-8")

    dims, profiles, tiers, err = load_profiles_config()

    assert dims is None
    assert profiles is None
    assert tiers is None
    assert err is not None


def test_load_profiles_config_missing_sections_returns_error(tmp_path, monkeypatch):
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

    assert dims is None
    assert profiles is None
    assert tiers is None
    assert err is not None
