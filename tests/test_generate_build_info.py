import datetime as dt
import importlib.util
from pathlib import Path


_MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "generate_build_info.py"
_SPEC = importlib.util.spec_from_file_location("generate_build_info", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
generate_build_info = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(generate_build_info)


def test_build_info_prefers_ci_identity(monkeypatch):
    monkeypatch.setenv("GITHUB_SHA", "deadbeef")
    monkeypatch.setenv("GITHUB_REF_NAME", "feature/crash")
    monkeypatch.setenv("GITHUB_RUN_ID", "12345")

    payload = generate_build_info.build_info(
        dt.datetime(2026, 9, 28, 12, 30, tzinfo=dt.timezone.utc)
    )

    assert payload == {
        "schema_version": 1,
        "commit": "deadbeef",
        "ref": "feature/crash",
        "run_id": "12345",
        "timestamp": "2026-09-28T12:30:00+00:00",
    }
