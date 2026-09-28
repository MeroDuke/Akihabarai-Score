import importlib.util
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPT_PATH = ROOT / "scripts" / "smoke_test_packaged_app.py"
SPEC = importlib.util.spec_from_file_location("smoke_test_packaged_app", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FakeProcess:
    def __init__(self, exit_code=None):
        self.pid = 123
        self.exit_code = exit_code
        self.terminated = False

    def poll(self):
        return self.exit_code

    def terminate(self):
        self.terminated = True
        self.exit_code = 0

    def wait(self, timeout=None):
        return self.exit_code

    def kill(self):
        self.exit_code = -9


def test_smoke_workflow_passes_only_after_main_window_ready(monkeypatch, tmp_path):
    process = FakeProcess()
    logs = tmp_path / "logs"
    launched = []

    def fake_sleep(_seconds):
        (logs / "session.log").write_text(
            "[INFO] [app] Main window ready\n", encoding="utf-8"
        )

    monkeypatch.setattr(
        MODULE.subprocess,
        "Popen",
        lambda command, **kwargs: launched.append(command) or process,
    )
    monkeypatch.setattr(MODULE.time, "sleep", fake_sleep)

    report = MODULE.run_smoke_test(
        ["AkihabaraiScore"],
        working_directory=tmp_path,
        log_directory=logs,
        timeout_seconds=1,
    )

    assert report["result"] == "PASS"
    assert report["ready"] is True
    assert process.terminated is True
    assert launched == [[str((tmp_path / "AkihabaraiScore").resolve())]]


def test_smoke_workflow_fails_when_startup_crash_log_appears(monkeypatch, tmp_path):
    process = FakeProcess()
    logs = tmp_path / "logs"

    def fake_sleep(_seconds):
        (logs / "crash-startup.log").write_text("boom", encoding="utf-8")

    monkeypatch.setattr(MODULE.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(MODULE.time, "sleep", fake_sleep)

    report = MODULE.run_smoke_test(
        ["AkihabaraiScore"],
        working_directory=tmp_path,
        log_directory=logs,
        timeout_seconds=1,
    )

    assert report["result"] == "FAIL"
    assert report["crash_logs"] == ["crash-startup.log"]
    assert process.terminated is True


def test_smoke_workflow_fails_on_early_exit(monkeypatch, tmp_path):
    process = FakeProcess(exit_code=1)
    monkeypatch.setattr(MODULE.subprocess, "Popen", lambda *args, **kwargs: process)

    report = MODULE.run_smoke_test(
        ["AkihabaraiScore"],
        working_directory=tmp_path,
        log_directory=tmp_path / "logs",
        timeout_seconds=1,
    )

    assert report["result"] == "FAIL"
    assert report["exit_code"] == 1
