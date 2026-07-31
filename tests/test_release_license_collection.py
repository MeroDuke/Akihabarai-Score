import importlib.util
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPT_PATH = ROOT / "scripts" / "collect_release_licenses.py"


def test_license_collector_is_valid_and_covers_runtime_and_packages():
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    compile(source, str(SCRIPT_PATH), "exec")

    assert "importlib.metadata.distribution" in source
    assert "python-packages" in source
    assert "python-runtime" in source
    assert "LICENSE_PREFIXES" in source


def test_release_workflows_package_legal_material():
    for workflow_name in ("build-windows-exe.yml", "build-linux.yml"):
        workflow = (ROOT / ".github" / "workflows" / workflow_name).read_text(encoding="utf-8")
        assert "scripts/collect_release_licenses.py" in workflow
        assert "THIRD_PARTY_NOTICES.md" in workflow
        assert "release-sbom-python.cdx.json" in workflow
