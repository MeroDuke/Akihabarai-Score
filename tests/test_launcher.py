import datetime as dt

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
    assert "timestamp: 2026-09-28T12:34:56" in path.read_text(encoding="utf-8")
