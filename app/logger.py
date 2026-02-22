from __future__ import annotations

import json
import os
import sys
import datetime as _dt
from dataclasses import dataclass
from typing import Any, Dict, Optional

# -------------------------
# Paths / config
# -------------------------

def app_dir() -> str:
    """
    Same logic as main.py:
    - dev: project root (parent of /app)
    - PyInstaller onefile: folder of the executable
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


DEFAULT_APP_CFG: Dict[str, Any] = {
    "logging": {
        "enabled": False,
        "level": "INFO",          # DEBUG | INFO | WARNING | ERROR
        "filename_mode": "session",  # session | daily
        "retention_days": 14
    }
}


def _deep_merge(dst: Dict[str, Any], src: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in (src or {}).items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst


def load_app_config() -> Dict[str, Any]:
    """
    Loads config/app.json (multipurpose). Falls back to defaults if missing/broken.
    """
    cfg_path = os.path.join(app_dir(), "config", "app.json")
    cfg = json.loads(json.dumps(DEFAULT_APP_CFG))  # cheap deep copy
    try:
        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            _deep_merge(cfg, user_cfg)
    except Exception:
        # If config is malformed, keep defaults (safe behavior)
        pass
    return cfg


# -------------------------
# Logger
# -------------------------

_LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}


@dataclass
class _LoggerState:
    enabled: bool
    level: int
    log_dir: str
    session_id: str
    filename_mode: str  # session | daily
    retention_days: int


_STATE: Optional[_LoggerState] = None


def init_logger(cfg: Optional[Dict[str, Any]] = None) -> None:
    """
    Initializes a simple file-only logger.
    - Session-based file name by default (per user request).
    - Safe to call multiple times; only first call wins.
    """
    global _STATE
    if _STATE is not None:
        return

    cfg = cfg or load_app_config()
    lcfg = (cfg.get("logging") or {})

    enabled = bool(lcfg.get("enabled", False))
    level_name = str(lcfg.get("level", "INFO")).strip().upper()
    level = _LEVELS.get(level_name, _LEVELS["INFO"])

    filename_mode = str(lcfg.get("filename_mode", "session")).strip().lower()
    if filename_mode not in ("session", "daily"):
        filename_mode = "session"

    try:
        retention_days = int(lcfg.get("retention_days", 14))
    except Exception:
        retention_days = 14
    retention_days = max(0, retention_days)

    log_dir = os.path.join(app_dir(), "logs")
    os.makedirs(log_dir, exist_ok=True)

    session_id = _dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    _STATE = _LoggerState(
        enabled=enabled,
        level=level,
        log_dir=log_dir,
        session_id=session_id,
        filename_mode=filename_mode,
        retention_days=retention_days
    )

    if enabled and retention_days > 0:
        _cleanup_old_logs(log_dir, retention_days)

    if enabled:
        log_info("logger", f"Logger initialized (mode={filename_mode}, level={level_name}, session={session_id})")


def _cleanup_old_logs(log_dir: str, retention_days: int) -> None:
    """
    Deletes old .log files by mtime. Best-effort, never raises.
    """
    try:
        cutoff = _dt.datetime.now().timestamp() - (retention_days * 86400)
        for name in os.listdir(log_dir):
            if not name.lower().endswith(".log"):
                continue
            path = os.path.join(log_dir, name)
            try:
                if os.path.getmtime(path) < cutoff:
                    os.remove(path)
            except Exception:
                continue
    except Exception:
        return


def _log_path() -> str:
    assert _STATE is not None
    if _STATE.filename_mode == "daily":
        base = _dt.datetime.now().strftime("%Y-%m-%d")
    else:
        base = _STATE.session_id
    return os.path.join(_STATE.log_dir, f"{base}.log")


def _write(level_name: str, component: str, message: str) -> None:
    if _STATE is None:
        init_logger()

    assert _STATE is not None
    if not _STATE.enabled:
        return

    lvl = _LEVELS.get(level_name, _LEVELS["INFO"])
    if lvl < _STATE.level:
        return

    ts = _dt.datetime.now().strftime("%H:%M:%S")
    path = _log_path()

    # Keep formatting similar to the Fordító style (timestamp + separator)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] [{level_name}] [{component}] {message}\n")
        f.write("-" * 80 + "\n")


def log_debug(component: str, message: str) -> None:
    _write("DEBUG", component, message)


def log_info(component: str, message: str) -> None:
    _write("INFO", component, message)


def log_warning(component: str, message: str) -> None:
    _write("WARNING", component, message)


def log_error(component: str, message: str) -> None:
    _write("ERROR", component, message)
