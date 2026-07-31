import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
PROVENANCE_PATH = ROOT / "compliance" / "windows-runtime-provenance.json"
AUDIT_PATH = ROOT / "scripts" / "audit_pyinstaller_build.py"
SPEC = importlib.util.spec_from_file_location("audit_pyinstaller_build_runtime", AUDIT_PATH)
AUDIT = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(AUDIT)


def test_windows_runtime_provenance_matches_build_allowlist():
    provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))

    assert provenance["schema_version"] == 1
    recorded = {entry["destination"].casefold() for entry in provenance["files"]}
    assert recorded == AUDIT.ALLOWED_WINDOWS_LOCAL_RUNTIME_DESTINATIONS
    assert len(recorded) == 7
    assert provenance["redistribution_basis"]["official_references"]
    assert provenance["redistribution_basis"]["engineering_note"]


def test_windows_release_packages_runtime_provenance():
    workflow = (ROOT / ".github" / "workflows" / "build-windows-exe.yml").read_text(
        encoding="utf-8"
    )

    assert "windows-runtime-provenance.json" in workflow
    assert "microsoft-runtime.json" in workflow
