"""Minimal application launcher that survives failures before Qt is available."""

from __future__ import annotations

import datetime as _dt
import faulthandler
import importlib.metadata
import platform
import sys
import traceback
from collections.abc import Callable
from pathlib import Path


UNKNOWN_VERSION = "unknown"


def application_version() -> str:
    try:
        return importlib.metadata.version("akihabarai-score")
    except Exception:
        return UNKNOWN_VERSION


def diagnostic_metadata(*, phase: str, timestamp: _dt.datetime) -> dict[str, str]:
    return {
        "timestamp": timestamp.isoformat(),
        "application_version": application_version(),
        "phase": phase,
        "platform": platform.platform(),
        "architecture": platform.machine() or UNKNOWN_VERSION,
        "python": sys.version.replace("\n", " "),
        "frozen": str(bool(getattr(sys, "frozen", False))).lower(),
        "executable": str(Path(sys.executable).resolve()),
        "working_directory": str(Path.cwd().resolve()),
    }


def format_metadata(metadata: dict[str, str]) -> str:
    return "".join(f"{key}: {value}\n" for key, value in metadata.items())


class FatalFaultLog:
    """Own the file descriptor required by ``faulthandler`` until shutdown."""

    def __init__(self, path: Path, stream, baseline_size: int):
        self.path = path
        self.stream = stream
        self.baseline_size = baseline_size

    def close(self, *, remove_if_clean: bool) -> None:
        try:
            if faulthandler.is_enabled():
                faulthandler.disable()
            self.stream.flush()
            current_size = self.stream.tell()
            self.stream.close()
            if remove_if_clean and current_size <= self.baseline_size:
                self.path.unlink(missing_ok=True)
        except Exception:
            try:
                self.stream.close()
            except Exception:
                pass


def enable_fatal_fault_log(
    *,
    log_directory: Path | None = None,
    now_func: Callable[[], _dt.datetime] = _dt.datetime.now,
) -> FatalFaultLog | None:
    """Enable best-effort fatal Python/native fault diagnostics very early."""
    try:
        if faulthandler.is_enabled():
            return None
        timestamp = now_func()
        target_directory = log_directory or application_directory() / "logs"
        target_directory.mkdir(parents=True, exist_ok=True)
        target = target_directory / timestamp.strftime("fatal-%Y-%m-%d_%H-%M-%S.log")
        stream = target.open("w", encoding="utf-8")
        stream.write("Akihabarai Score fatal fault diagnostics\n")
        stream.write(format_metadata(diagnostic_metadata(phase="launcher", timestamp=timestamp)))
        stream.write("failure_kind: native_fatal_fault\n")
        stream.write("\n")
        stream.flush()
        baseline_size = stream.tell()
        faulthandler.enable(file=stream, all_threads=True)
        return FatalFaultLog(target, stream, baseline_size)
    except Exception:
        return None


def application_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def write_startup_crash_log(
    error: BaseException,
    *,
    log_directory: Path | None = None,
    now_func: Callable[[], _dt.datetime] = _dt.datetime.now,
    phase: str = "run_application",
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
            + format_metadata(diagnostic_metadata(phase=phase, timestamp=timestamp))
            + "failure_kind: python_exception\n\n"
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
    fatal_log = enable_fatal_fault_log(log_directory=crash_log_directory)
    clean_shutdown = False
    phase = "import_application"
    try:
        if load_main is None:
            from app.main import main
        else:
            main = load_main()
        phase = "run_application"
        main()
        clean_shutdown = True
    except SystemExit:
        clean_shutdown = True
        raise
    except BaseException as error:
        write_startup_crash_log(
            error,
            log_directory=crash_log_directory,
            phase=phase,
        )
        clean_shutdown = True
        raise SystemExit(1) from error
    finally:
        if fatal_log is not None:
            fatal_log.close(remove_if_clean=clean_shutdown)


if __name__ == "__main__":
    run_application()
