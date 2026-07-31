import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPT_PATH = ROOT / "scripts" / "validate_portable_release.py"
SPEC = importlib.util.spec_from_file_location("validate_portable_release", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_release_workflows_validate_and_upload_portable_packages():
    windows = (ROOT / ".github" / "workflows" / "build-windows-exe.yml").read_text(
        encoding="utf-8"
    )
    linux = (ROOT / ".github" / "workflows" / "build-linux.yml").read_text(encoding="utf-8")

    for workflow, platform in ((windows, "windows"), (linux, "linux")):
        assert f"validate_portable_release.py --platform {platform}" in workflow
        assert "--tag-build" in workflow
        assert "portable-package-" not in workflow
    assert "AkihabaraiScore-windows.zip" in windows
    assert "AkihabaraiScore-linux-x86_64.tar.gz" in linux
    assert "prepare_source_archives.py --output release-sources" in windows
    assert "collect_qt_source_legal.py" in windows
    assert "release\\docs\\SOURCE_AVAILABILITY.md" in windows
    assert "release\\licenses\\release-sbom-python.cdx.json" in windows
    assert "release/docs/SOURCE_AVAILABILITY.md" in linux
    assert "release/licenses/release-sbom-python.cdx.json" in linux


def test_validator_reports_missing_release_files(tmp_path):
    errors = MODULE.validate(tmp_path, "windows")

    assert any("AkihabaraiScore.exe" in error for error in errors)
    assert any("microsoft-runtime.json" in error for error in errors)
