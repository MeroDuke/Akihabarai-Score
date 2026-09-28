"""Minimal application launcher that survives failures before Qt is available."""

from __future__ import annotations

import datetime as _dt
import faulthandler
import importlib.metadata
import platform
import os
import sys
import traceback
import uuid
from collections.abc import Callable
from pathlib import Path

from app.build_metadata import load_build_info
from app.native_crash_diagnostics import (
    linux_core_metadata,
    should_use_windows_supervisor,
    supervise_windows_process,
    trigger_native_crash_for_test,
    windows_exception_label,
)


UNKNOWN_VERSION = "unknown"


def application_version() -> str:
    try:
        return importlib.metadata.version("akihabarai-score")
    except Exception:
        return UNKNOWN_VERSION


def diagnostic_metadata(
    *, phase: str, timestamp: _dt.datetime, crash_id: str | None = None
) -> dict[str, str]:
    metadata = {
        "timestamp": timestamp.isoformat(),
        "crash_id": crash_id or "not-applicable",
        "application_version": application_version(),
        "phase": phase,
        "platform": platform.platform(),
        "architecture": platform.machine() or UNKNOWN_VERSION,
        "python": sys.version.replace("\n", " "),
        "frozen": str(bool(getattr(sys, "frozen", False))).lower(),
        "executable": str(Path(sys.executable).resolve()),
        "working_directory": str(Path.cwd().resolve()),
        "process_id": str(os.getpid()),
    }
    metadata.update(load_build_info())
    metadata.update(linux_core_metadata())
    return metadata


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
    crash_id: str | None = None,
) -> FatalFaultLog | None:
    """Enable best-effort fatal Python/native fault diagnostics very early."""
    try:
        if faulthandler.is_enabled():
            return None
        timestamp = now_func()
        target_directory = log_directory or application_directory() / "logs"
        target_directory.mkdir(parents=True, exist_ok=True)
        identifier = crash_id or uuid.uuid4().hex
        target = target_directory / timestamp.strftime(
            f"fatal-%Y-%m-%d_%H-%M-%S-{identifier}.log"
        )
        stream = target.open("w", encoding="utf-8")
        stream.write("Akihabarai Score fatal fault diagnostics\n")
        stream.write(
            format_metadata(
                diagnostic_metadata(
                    phase="launcher", timestamp=timestamp, crash_id=identifier
                )
            )
        )
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
    crash_id: str | None = None,
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
            + format_metadata(
                diagnostic_metadata(
                    phase=phase, timestamp=timestamp, crash_id=crash_id
                )
            )
            + "failure_kind: python_exception\n\n"
            f"{formatted_traceback}",
            encoding="utf-8",
        )
        return target
    except Exception:
        return None


def write_native_crash_summary(
    *,
    exception_code: int,
    dump_path: Path | None,
    log_directory: Path,
    timestamp: _dt.datetime,
    crash_id: str,
) -> Path | None:
    """Record evidence collected by the external Windows supervisor."""
    try:
        log_directory.mkdir(parents=True, exist_ok=True)
        target = log_directory / timestamp.strftime(
            f"native-crash-%Y-%m-%d_%H-%M-%S-{crash_id}.log"
        )
        category = "native-unknown"
        target.write_text(
            "Akihabarai Score native crash summary\n"
            + format_metadata(
                diagnostic_metadata(
                    phase="supervised_application",
                    timestamp=timestamp,
                    crash_id=crash_id,
                )
            )
            + "failure_kind: native_process_exception\n"
            + f"windows_exception_code: 0x{exception_code:08X}\n"
            + f"windows_exception_label: {windows_exception_label(exception_code)}\n"
            + f"minidump: {dump_path if dump_path else 'not-created'}\n"
            + f"triage_category: {category}\n"
            + "triage_limitation: likely_layer_only_not_root_cause\n",
            encoding="utf-8",
        )
        return target
    except Exception:
        return None


def run_supervised_packaged_application(
    *, crash_log_directory: Path | None = None
) -> None:
    timestamp = _dt.datetime.now()
    crash_id = uuid.uuid4().hex
    target_directory = crash_log_directory or application_directory() / "logs"
    dump_path = target_directory / timestamp.strftime(
        f"native-%Y-%m-%d_%H-%M-%S-{crash_id}.dmp"
    )
    result = supervise_windows_process(
        [sys.executable, *sys.argv[1:]],
        dump_path=dump_path,
        environment={"AKIHABARAI_CRASH_ID": crash_id},
    )
    if result.exception_code is not None:
        write_native_crash_summary(
            exception_code=result.exception_code,
            dump_path=result.dump_path,
            log_directory=target_directory,
            timestamp=timestamp,
            crash_id=crash_id,
        )
    if result.returncode:
        raise SystemExit(result.returncode)


def run_application(
    *,
    load_main: Callable[[], Callable[[], None]] | None = None,
    crash_log_directory: Path | None = None,
) -> None:
    """Load and run the real entry point, logging startup failures before exit."""
    if should_use_windows_supervisor():
        try:
            run_supervised_packaged_application(crash_log_directory=crash_log_directory)
            return
        except Exception as error:
            # A diagnostic helper failure must not prevent the application
            # itself from starting. The degraded state remains CI-visible.
            write_startup_crash_log(
                error,
                log_directory=crash_log_directory,
                phase="crash_supervisor",
            )

    crash_id = os.environ.get("AKIHABARAI_CRASH_ID") or uuid.uuid4().hex
    timestamp = _dt.datetime.now()
    fatal_log = enable_fatal_fault_log(
        log_directory=crash_log_directory,
        now_func=lambda: timestamp,
        crash_id=crash_id,
    )
    trigger_native_crash_for_test()
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
            crash_id=crash_id,
        )
        clean_shutdown = True
        raise SystemExit(1) from error
    finally:
        if fatal_log is not None:
            fatal_log.close(remove_if_clean=clean_shutdown)


if __name__ == "__main__":
    run_application()
