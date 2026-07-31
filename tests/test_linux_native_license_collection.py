import importlib.util
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPT_PATH = ROOT / "scripts" / "collect_linux_native_licenses.py"
SPEC = importlib.util.spec_from_file_location("collect_linux_native_licenses", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_system_library_detection_is_limited_to_linux_library_roots():
    assert MODULE.is_system_library(Path("/lib/x86_64-linux-gnu/libz.so.1"))
    assert MODULE.is_system_library(Path("/usr/lib/x86_64-linux-gnu/libgtk-3.so.0"))
    assert not MODULE.is_system_library(Path("/opt/python/lib/libpython3.11.so"))
    assert not MODULE.is_system_library(Path("PyQt6/Qt6/lib/libQt6Core.so.6"))


def test_copyright_path_strips_multiarch_suffix():
    assert MODULE.copyright_path("libgtk-3-0:amd64") == Path(
        "/usr/share/doc/libgtk-3-0/copyright"
    )


def test_owner_parser_handles_normal_and_diverted_dpkg_paths():
    assert MODULE.parse_owner_output("libgtk-3-0:amd64: /usr/lib/libgtk-3.so.0\n") == "libgtk-3-0:amd64"
    assert (
        MODULE.parse_owner_output(
            "diversion by libreadline8t64 from: /lib/x86_64-linux-gnu/libreadline.so.8\n"
        )
        == "libreadline8t64"
    )


def test_release_linux_workflow_collects_and_packages_native_licenses():
    workflow = (ROOT / ".github" / "workflows" / "build-linux.yml").read_text(encoding="utf-8")

    assert "scripts/collect_linux_native_licenses.py" in workflow
    assert "release-linux-packages.json" in workflow
    assert "linux-native-compliance" in workflow
