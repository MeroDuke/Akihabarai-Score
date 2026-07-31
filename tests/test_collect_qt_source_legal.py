import importlib.util
import io
from pathlib import Path
import tarfile


ROOT = Path(__file__).parents[1]
SCRIPT_PATH = ROOT / "scripts" / "collect_qt_source_legal.py"
SPEC = importlib.util.spec_from_file_location("collect_qt_source_legal", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def add_file(archive, name, content):
    payload = content.encode("utf-8")
    member = tarfile.TarInfo(name)
    member.size = len(payload)
    archive.addfile(member, io.BytesIO(payload))


def test_qt_legal_extraction_keeps_notices_and_ignores_source(tmp_path):
    archive_path = tmp_path / "qtbase-everywhere-src-6.11.1.tar.xz"
    with tarfile.open(archive_path, "w:xz") as archive:
        add_file(archive, "qtbase/LICENSES/LGPL-3.0-only.txt", "license")
        add_file(archive, "qtbase/src/3rdparty/example/qt_attribution.json", "{}")
        add_file(archive, "qtbase/src/corelib/example.cpp", "source")

    output = tmp_path / "legal"
    count = MODULE.extract_legal_files(archive_path, output)

    assert count == 2
    component = output / "qtbase-everywhere-src-6.11.1"
    assert (component / "LICENSES" / "LGPL-3.0-only.txt").read_text() == "license"
    assert (component / "src" / "3rdparty" / "example" / "qt_attribution.json").is_file()
    assert not (component / "src" / "corelib" / "example.cpp").exists()


def test_unsafe_archive_members_are_rejected():
    for name in ("qtbase/../outside", "/absolute/outside"):
        try:
            MODULE.safe_relative_name(name)
        except ValueError as error:
            assert "Unsafe" in str(error)
        else:
            raise AssertionError(f"Unsafe archive path was accepted: {name}")


def test_tag_workflow_extracts_qt_legal_material_before_assembly():
    workflow = (ROOT / ".github" / "workflows" / "build-linux.yml").read_text(encoding="utf-8")

    prepare = workflow.index("prepare_source_archives.py --output release-sources")
    collect = workflow.index("collect_qt_source_legal.py")
    assemble = workflow.index("Assemble portable folder")
    assert prepare < collect < assemble
