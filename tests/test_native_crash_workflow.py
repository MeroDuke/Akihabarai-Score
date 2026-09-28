import importlib.util
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).parents[1]
SCRIPT_PATH = ROOT / "scripts" / "test_packaged_native_crash.py"
SPEC = importlib.util.spec_from_file_location("test_packaged_native_crash", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_windows_packaged_crash_workflow_requires_log_summary_and_dump(
    monkeypatch, tmp_path
):
    logs = tmp_path / "logs"

    def fake_run(*args, **kwargs):
        logs.mkdir(parents=True, exist_ok=True)
        (logs / "fatal-test.log").write_text("fatal", encoding="utf-8")
        (logs / "native-crash-test.log").write_text("summary", encoding="utf-8")
        (logs / "native-test.dmp").write_bytes(b"MDMP")
        return SimpleNamespace(returncode=0xC0000005)

    monkeypatch.setattr(MODULE.subprocess, "run", fake_run)

    report = MODULE.run_crash_workflow(
        ["AkihabaraiScore.exe"],
        working_directory=tmp_path,
        log_directory=logs,
        platform_name="windows",
    )

    assert report["result"] == "PASS"
    assert report["minidumps"] == ["native-test.dmp"]


def test_linux_packaged_crash_workflow_does_not_require_local_core_file(
    monkeypatch, tmp_path
):
    logs = tmp_path / "logs"

    def fake_run(*args, **kwargs):
        logs.mkdir(parents=True, exist_ok=True)
        (logs / "fatal-test.log").write_text("fatal", encoding="utf-8")
        return SimpleNamespace(returncode=-11)

    monkeypatch.setattr(MODULE.subprocess, "run", fake_run)

    report = MODULE.run_crash_workflow(
        ["AkihabaraiScore"],
        working_directory=tmp_path,
        log_directory=logs,
        platform_name="linux",
    )

    assert report["result"] == "PASS"
    assert report["minidumps"] == []


def test_packaged_crash_workflow_fails_if_process_does_not_crash(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(
        MODULE.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=0)
    )

    report = MODULE.run_crash_workflow(
        ["AkihabaraiScore"],
        working_directory=tmp_path,
        log_directory=tmp_path / "logs",
        platform_name="linux",
    )

    assert report["result"] == "FAIL"
    assert "native crash test exited successfully" in report["errors"]
    assert "fatal fault log was not created" in report["errors"]
