import json

import app.config.ui_config as ui_config_module
from app.config.ui_config import DEFAULT_WINDOW_CONFIG, load_ui_config
from app.core.constants import DEFAULT_UI


def test_load_ui_config_missing_file_returns_default(tmp_path, monkeypatch):
    monkeypatch.setattr(ui_config_module, "app_dir", lambda: tmp_path)

    cfg, err = load_ui_config()

    assert err is not None
    assert cfg["window"] == DEFAULT_WINDOW_CONFIG


def test_load_ui_config_valid_json_merges_with_default(tmp_path, monkeypatch):
    monkeypatch.setattr(ui_config_module, "app_dir", lambda: tmp_path)

    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()

    custom_cfg = {
        "app_title": "Custom Title",
        "show_summary": False,
    }

    (cfg_dir / "ui.json").write_text(json.dumps(custom_cfg), encoding="utf-8")

    cfg, err = load_ui_config()

    assert err is None
    assert cfg["app_title"] == "Custom Title"
    assert cfg["show_summary"] is False
    assert cfg["window"] == DEFAULT_WINDOW_CONFIG


def test_load_ui_config_default_window_size_is_supported_baseline(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(ui_config_module, "app_dir", lambda: tmp_path)

    cfg, err = load_ui_config()

    assert err is not None
    assert cfg["window"] == DEFAULT_WINDOW_CONFIG


def test_load_ui_config_window_section_merges_with_default(tmp_path, monkeypatch):
    monkeypatch.setattr(ui_config_module, "app_dir", lambda: tmp_path)

    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()

    custom_cfg = {
        "window": {
            "default_width": 1920,
        }
    }

    (cfg_dir / "ui.json").write_text(json.dumps(custom_cfg), encoding="utf-8")

    cfg, err = load_ui_config()

    assert err is None
    assert cfg["window"]["default_width"] == 1920
    assert cfg["window"]["default_height"] == 720
    assert cfg["window"]["minimum_width"] == 1600
    assert cfg["window"]["minimum_height"] == 720


def test_load_ui_config_invalid_json_falls_back_to_default(tmp_path, monkeypatch):
    monkeypatch.setattr(ui_config_module, "app_dir", lambda: tmp_path)

    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()
    (cfg_dir / "ui.json").write_text("{ invalid json }", encoding="utf-8")

    cfg, err = load_ui_config()

    assert err is not None
    assert cfg["window"] == DEFAULT_WINDOW_CONFIG


def test_load_ui_config_returns_fresh_dict_each_time(tmp_path, monkeypatch):
    monkeypatch.setattr(ui_config_module, "app_dir", lambda: tmp_path)

    cfg1, _ = load_ui_config()
    cfg2, _ = load_ui_config()

    cfg1["app_title"] = "Modified title"
    cfg1["window"]["default_width"] = 9999

    assert cfg2["app_title"] == DEFAULT_UI["app_title"]
    assert cfg2["window"] == DEFAULT_WINDOW_CONFIG
