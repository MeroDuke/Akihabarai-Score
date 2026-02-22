import os
import datetime as dt
import importlib

import pytest

import app.logger as logger


class FixedDateTime(dt.datetime):
    """Deterministic datetime for tests."""
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 2, 22, 12, 34, 56, tzinfo=tz)


def _reset_logger_state(monkeypatch):
    # Reset singleton-like state so each test is isolated
    monkeypatch.setattr(logger, "_STATE", None, raising=False)


def _patch_app_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(logger, "app_dir", lambda: str(tmp_path))


def _patch_datetime(monkeypatch):
    # logger module imports datetime as _dt
    monkeypatch.setattr(logger._dt, "datetime", FixedDateTime)


def test_load_app_config_missing_returns_defaults(tmp_path, monkeypatch):
    _reset_logger_state(monkeypatch)
    _patch_app_dir(monkeypatch, tmp_path)

    cfg = logger.load_app_config()
    assert cfg == logger.DEFAULT_APP_CFG


def test_load_app_config_merges_user_config(tmp_path, monkeypatch):
    _reset_logger_state(monkeypatch)
    _patch_app_dir(monkeypatch, tmp_path)

    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "app.json").write_text(
        """{
          "logging": {
            "enabled": true,
            "level": "DEBUG",
            "filename_mode": "session",
            "retention_days": 3
          }
        }""",
        encoding="utf-8",
    )

    cfg = logger.load_app_config()
    assert cfg["logging"]["enabled"] is True
    assert cfg["logging"]["level"] == "DEBUG"
    assert cfg["logging"]["filename_mode"] == "session"
    assert cfg["logging"]["retention_days"] == 3


def test_init_logger_session_file_writes_and_level_filtering(tmp_path, monkeypatch):
    _reset_logger_state(monkeypatch)
    _patch_app_dir(monkeypatch, tmp_path)
    _patch_datetime(monkeypatch)

    cfg = {
        "logging": {
            "enabled": True,
            "level": "INFO",          # DEBUG should be filtered out
            "filename_mode": "session",
            "retention_days": 14,
        }
    }

    logger.init_logger(cfg)

    # DEBUG should not be written at INFO level
    logger.log_debug("ui", "debug-nope")
    logger.log_info("ui", "info-yes")

    expected_log = tmp_path / "logs" / "2026-02-22_12-34-56.log"
    assert expected_log.is_file()

    content = expected_log.read_text(encoding="utf-8")
    assert "debug-nope" not in content
    assert "[INFO]" in content
    assert "[ui]" in content
    assert "info-yes" in content


def test_filename_mode_daily_uses_date_file(tmp_path, monkeypatch):
    _reset_logger_state(monkeypatch)
    _patch_app_dir(monkeypatch, tmp_path)
    _patch_datetime(monkeypatch)

    cfg = {
        "logging": {
            "enabled": True,
            "level": "DEBUG",
            "filename_mode": "daily",
            "retention_days": 14,
        }
    }

    logger.init_logger(cfg)
    logger.log_info("ui", "daily-file")

    expected_log = tmp_path / "logs" / "2026-02-22.log"
    assert expected_log.is_file()
    assert "daily-file" in expected_log.read_text(encoding="utf-8")


def test_retention_deletes_old_logs_by_mtime(tmp_path, monkeypatch):
    _reset_logger_state(monkeypatch)
    _patch_app_dir(monkeypatch, tmp_path)
    _patch_datetime(monkeypatch)

    logs_dir = tmp_path / "logs"
    logs_dir.mkdir()

    old_log = logs_dir / "old.log"
    old_log.write_text("old", encoding="utf-8")

    # Make it "older than 1 day"
    old_mtime = (FixedDateTime.now().timestamp() - (2 * 86400))
    os.utime(old_log, (old_mtime, old_mtime))

    cfg = {
        "logging": {
            "enabled": True,
            "level": "INFO",
            "filename_mode": "session",
            "retention_days": 1,
        }
    }

    logger.init_logger(cfg)

    assert not old_log.exists()