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
    assert "release\\legal\\SOURCE_AVAILABILITY.md" in windows
    assert "release\\legal\\third-party" in windows
    assert "release/legal/SOURCE_AVAILABILITY.md" in linux
    assert "release/legal/third-party" in linux
    assert "release\\licenses" not in windows
    assert "release/licenses" not in linux
    assert "release\\build-info.json" not in windows
    assert "release/build-info.json" not in linux
    assert "tar -czf AkihabaraiScore-linux-x86_64.tar.gz -C release --" in linux
    assert (
        "AkihabaraiScore assets config docs legal"
    ) in linux
    assert "tar -czf AkihabaraiScore-linux-x86_64.tar.gz -C release ." not in linux
    assert "Validate Linux archive root layout" in linux
    assert "grep -q '^\\./'" in linux
    assert "Unexpected ./ root entry in Linux archive" in linux


def test_validator_reports_missing_release_files(tmp_path):
    errors = MODULE.validate(tmp_path, "windows")

    assert any("AkihabaraiScore.exe" in error for error in errors)


def test_validator_accepts_clean_layout_and_rejects_internal_file_leaks(tmp_path):
    release = tmp_path / "release"
    evidence = tmp_path / "evidence"
    for relative in MODULE.COMMON_FILES:
        path = release / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("placeholder", encoding="utf-8")
    (release / "AkihabaraiScore.exe").write_bytes(b"exe")
    (release / "legal" / "LICENSE").write_text(
        "GNU GENERAL PUBLIC LICENSE", encoding="utf-8"
    )
    third_party = release / "legal" / "third-party"
    third_party.mkdir(parents=True, exist_ok=True)
    for name in ("python-license.txt", "qt-license.txt", "requests-license.txt"):
        (third_party / name).write_text("license", encoding="utf-8")

    evidence.mkdir()
    (evidence / "release-sbom-python.cdx.json").write_text(
        '{"bomFormat":"CycloneDX","components":[{"name":"PyQt6"}]}',
        encoding="utf-8",
    )
    (evidence / "release-native-inventory.json").write_text(
        '{"schema_version":1,"entries":[{"destination":"python.dll","source":"wheel"}]}',
        encoding="utf-8",
    )
    compliance = evidence / "compliance"
    compliance.mkdir()
    (compliance / "source-archives.json").write_text(
        '{"schema_version":1,"archives":[{"component":"PyQt6"}]}',
        encoding="utf-8",
    )
    icon = release / "assets" / "icon.ico"
    import hashlib
    digest = hashlib.sha256(icon.read_bytes()).hexdigest()
    (compliance / "asset-provenance.json").write_text(
        '{"assets":[{"path":"assets/icon.ico","sha256":"' + digest + '"}]}',
        encoding="utf-8",
    )
    (compliance / "windows-runtime-provenance.json").write_text(
        '{"files":[]}', encoding="utf-8"
    )

    assert MODULE.validate(release, "windows", evidence_root=evidence) == []

    (release / "release-sbom-python.cdx.json").write_text("{}", encoding="utf-8")
    errors = MODULE.validate(release, "windows", evidence_root=evidence)
    assert any("leaked" in error for error in errors)
