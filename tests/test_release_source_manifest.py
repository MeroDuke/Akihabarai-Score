import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
MANIFEST = ROOT / "compliance" / "source-archives.json"


def test_source_manifest_has_pinned_official_archives():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["schema_version"] == 1
    components = {archive["component"]: archive for archive in manifest["archives"]}
    assert set(components) == {"PyQt6", "Qt Base", "Qt Wayland"}

    for archive in components.values():
        assert archive["url"].startswith("https://")
        assert len(archive["sha256"]) == 64
        int(archive["sha256"], 16)

    assert "download.qt.io" in components["Qt Base"]["url"]
    assert "download.qt.io" in components["Qt Wayland"]["url"]
    assert "pythonhosted.org" in components["PyQt6"]["url"]


def test_release_workflows_package_source_manifest():
    for workflow_name in ("build-windows-exe.yml", "build-linux.yml"):
        workflow = (ROOT / ".github" / "workflows" / workflow_name).read_text(encoding="utf-8")
        assert "source-archives.json" in workflow
        assert "release_source_availability.md" in workflow
