import datetime as dt
import subprocess
import sys
from pathlib import Path

import pytest

from app import launcher


def test_run_application_executes_loaded_main_without_crash_log(tmp_path):
    calls = []

    launcher.run_application(
        load_main=lambda: lambda: calls.append("main"),
        crash_log_directory=tmp_path,
    )

    assert calls == ["main"]
    assert list(tmp_path.iterdir()) == []


def test_run_application_writes_startup_crash_log_and_exits_nonzero(tmp_path):
    def failing_main():
        raise ImportError("QtCore DLL load failed")

    with pytest.raises(SystemExit) as exit_info:
        launcher.run_application(
            load_main=lambda: failing_main,
            crash_log_directory=tmp_path,
        )

    assert exit_info.value.code == 1
    crash_log = next(tmp_path.glob("crash-*.log"))
    contents = crash_log.read_text(encoding="utf-8")
    assert "Akihabarai Score startup crash" in contents
    assert "ImportError: QtCore DLL load failed" in contents


def test_run_application_preserves_normal_system_exit(tmp_path):
    def normal_exit():
        raise SystemExit(0)

    with pytest.raises(SystemExit) as exit_info:
        launcher.run_application(
            load_main=lambda: normal_exit,
            crash_log_directory=tmp_path,
        )

    assert exit_info.value.code == 0
    assert list(tmp_path.iterdir()) == []


def test_startup_crash_log_has_deterministic_name_and_diagnostics(tmp_path):
    error = RuntimeError("startup failed")

    path = launcher.write_startup_crash_log(
        error,
        log_directory=tmp_path,
        now_func=lambda: dt.datetime(2026, 9, 28, 12, 34, 56),
    )

    assert path == tmp_path / "crash-2026-09-28_12-34-56.log"
    contents = path.read_text(encoding="utf-8")
    assert "timestamp: 2026-09-28T12:34:56" in contents
    assert "application_version: " in contents
    assert "phase: run_application" in contents
    assert "architecture: " in contents
    assert "executable: " in contents
    assert "working_directory: " in contents
    assert "failure_kind: python_exception" in contents


def test_fatal_fault_log_is_removed_after_clean_shutdown(tmp_path):
    launcher.run_application(
        load_main=lambda: lambda: None,
        crash_log_directory=tmp_path,
    )

    assert list(tmp_path.glob("fatal-*.log")) == []


def test_native_fatal_fault_is_captured_in_isolated_child_process(tmp_path):
    root = Path(__file__).parents[1]
    script = (
        "from pathlib import Path; "
        "from app.launcher import enable_fatal_fault_log; "
        "import faulthandler, sys; "
        "guard = enable_fatal_fault_log(log_directory=Path(sys.argv[1])); "
        "assert guard is not None; "
        "faulthandler._sigsegv()"
    )

    result = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path)],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )

    assert result.returncode != 0
    fatal_log = next(tmp_path.glob("fatal-*.log"))
    contents = fatal_log.read_text(encoding="utf-8", errors="replace")
    assert "Akihabarai Score fatal fault diagnostics" in contents
    assert "application_version: " in contents
    assert "phase: launcher" in contents
    assert "failure_kind: native_fatal_fault" in contents
    assert "Fatal Python error" in contents
