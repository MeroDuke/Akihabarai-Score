# tests/test_runtime.py
from pathlib import Path

from PyQt6.QtGui import QIcon

import app.core.runtime as runtime_module
from app.core.runtime import app_dir, load_app_icon


def test_app_dir_returns_path():
    result = app_dir()

    assert isinstance(result, Path)
    assert result.exists()


def test_load_app_icon_returns_none_when_icon_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime_module, "app_dir", lambda: tmp_path)

    icon = load_app_icon()

    assert icon is None


def test_load_app_icon_returns_qicon_when_icon_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(runtime_module, "app_dir", lambda: tmp_path)

    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()

    # elég egy üres fájl a létezés ellenőrzéshez
    (assets_dir / "icon.ico").write_bytes(b"")

    icon = load_app_icon()

    assert isinstance(icon, QIcon)