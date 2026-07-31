import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPT_PATH = ROOT / "scripts" / "prepare_source_archives.py"
SPEC = importlib.util.spec_from_file_location("prepare_source_archives", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def write_manifest(path, archives):
    path.write_text(json.dumps({"schema_version": 1, "archives": archives}), encoding="utf-8")


def test_checked_in_source_manifest_is_accepted():
    archives = MODULE.read_manifest(ROOT / "compliance" / "source-archives.json")

    assert {archive["component"] for archive in archives} == {"PyQt6", "Qt Base", "Qt Wayland"}


def test_manifest_rejects_insecure_or_unpinned_archive(tmp_path):
    manifest = tmp_path / "sources.json"
    write_manifest(
        manifest,
        [{"component": "Qt", "version": "1", "url": "http://example.test/qt.tar.xz", "sha256": "bad"}],
    )

    try:
        MODULE.read_manifest(manifest)
    except ValueError as error:
        assert "HTTPS" in str(error) or "SHA-256" in str(error)
    else:
        raise AssertionError("Invalid source archive manifest was accepted")


def test_download_verifies_hash_before_publishing_file(tmp_path, monkeypatch):
    payload = b"corresponding source"
    source = tmp_path / "upstream.tar.xz"
    source.write_bytes(payload)
    output = tmp_path / "out"
    output.mkdir()
    archive = {
        "component": "Example",
        "version": "1",
        "url": source.as_uri(),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }

    downloaded = MODULE.download_archive(archive, output)

    assert downloaded.read_bytes() == payload
    assert not list(output.glob("*.part"))


def test_tag_release_workflow_attaches_verified_sources():
    workflow = (ROOT / ".github" / "workflows" / "build-linux.yml").read_text(encoding="utf-8")

    assert "prepare_source_archives.py --validate-only" in workflow
    assert "prepare_source_archives.py --output release-sources" in workflow
    assert "release-sources/*" in workflow
