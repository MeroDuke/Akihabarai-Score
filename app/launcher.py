"""Minimal application launcher that survives failures before Qt is available."""

from __future__ import annotations

import datetime as _dt
import platform
import sys
import traceback
from collections.abc import Callable
from pathlib import Path


def application_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def write_startup_crash_log(
    error: BaseException,
    *,
    log_directory: Path | None = None,
    now_func: Callable[[], _dt.datetime] = _dt.datetime.now,
) -> Path | None:
    """Write a best-effort crash report without importing any application module."""
    try:
        timestamp = now_func()
        target_directory = log_directory or application_directory() / "logs"
        target_directory.mkdir(parents=True, exist_ok=True)
        target = target_directory / timestamp.strftime("crash-%Y-%m-%d_%H-%M-%S.log")
        formatted_traceback = "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )
        target.write_text(
            "Akihabarai Score startup crash\n"
            f"timestamp: {timestamp.isoformat()}\n"
            f"platform: {platform.platform()}\n"
            f"python: {sys.version}\n"
            f"frozen: {bool(getattr(sys, 'frozen', False))}\n\n"
            f"{formatted_traceback}",
            encoding="utf-8",
        )
        return target
    except Exception:
        return None


def run_application(
    *,
    load_main: Callable[[], Callable[[], None]] | None = None,
    crash_log_directory: Path | None = None,
) -> None:
    """Load and run the real entry point, logging startup failures before exit."""
    try:
        if load_main is None:
            from app.main import main
        else:
            main = load_main()
        main()
    except SystemExit:
        raise
    except BaseException as error:
        write_startup_crash_log(error, log_directory=crash_log_directory)
        raise SystemExit(1) from error


if __name__ == "__main__":
    run_application()
