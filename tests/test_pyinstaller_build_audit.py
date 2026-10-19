import importlib.util
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPT_PATH = ROOT / "scripts" / "audit_pyinstaller_build.py"
SPEC = importlib.util.spec_from_file_location("audit_pyinstaller_build", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def qt_entries(*additional):
    return [
        {"destination": "PyQt6/Qt6/bin/Qt6Core.dll", "source": "core", "kind": "BINARY"},
        {"destination": "PyQt6/Qt6/bin/Qt6Gui.dll", "source": "gui", "kind": "BINARY"},
        {"destination": "PyQt6/Qt6/bin/Qt6Widgets.dll", "source": "widgets", "kind": "BINARY"},
        {"destination": "PyQt6/Qt6/plugins/imageformats/qico.dll", "source": "ico", "kind": "BINARY"},
        {"destination": "PyQt6/Qt6/plugins/imageformats/qjpeg.dll", "source": "jpeg", "kind": "BINARY"},
        {"destination": "PyQt6/Qt6/plugins/imageformats/qwebp.dll", "source": "webp", "kind": "BINARY"},
        {"destination": "PyQt6/Qt6/plugins/platforms/qwindows.dll", "source": "windows", "kind": "BINARY"},
        {"destination": "PyQt6/Qt6/plugins/platforms/qoffscreen.dll", "source": "offscreen", "kind": "BINARY"},
        {"destination": "PyQt6/Qt6/translations/qt_en.qm", "source": "en", "kind": "DATA"},
        {"destination": "PyQt6/Qt6/translations/qtbase_hu.qm", "source": "hu", "kind": "DATA"},
        *additional,
    ]


def test_build_audit_accepts_required_qt_runtime_without_pdf():
    entries = qt_entries()

    assert MODULE.validate(entries, "win32") == []
    assert MODULE.build_inventory(entries)["entry_count"] == 10


def test_build_audit_rejects_pdf_library_and_plugin():
    entries = qt_entries(
        {"destination": "PyQt6/Qt6/bin/Qt6Pdf.dll", "source": "pdf", "kind": "BINARY"},
        {
            "destination": "PyQt6/Qt6/plugins/imageformats/qpdf.dll",
            "source": "qpdf",
            "kind": "BINARY",
        },
    )

    errors = MODULE.validate(entries, "win32")
    assert any("qt6pdf" in error for error in errors)
    assert any("qpdf" in error for error in errors)


def test_build_audit_rejects_unsupported_image_plugins():
    entries = qt_entries(
        {"destination": "PyQt6/Qt6/plugins/imageformats/qsvg.dll", "source": "svg", "kind": "BINARY"}
    )

    assert any("qsvg" in error for error in MODULE.validate(entries, "win32"))


def test_build_audit_rejects_unexpected_translation_and_platform_plugin():
    entries = qt_entries(
        {"destination": "PyQt6/Qt6/translations/qt_de.qm", "source": "de", "kind": "DATA"},
        {"destination": "PyQt6/Qt6/plugins/platforms/qminimal.dll", "source": "minimal", "kind": "BINARY"},
    )

    errors = MODULE.validate(entries, "win32")
    assert any("qt_de.qm" in error for error in errors)
    assert any("qminimal" in error for error in errors)


def test_windows_audit_rejects_bundled_system_runtime_files():
    entries = qt_entries(
        {
            "destination": "api-ms-win-crt-runtime-l1-1-0.dll",
            "source": "C:/hostedtoolcache/windows/Java/bin/api-ms-win-crt-runtime-l1-1-0.dll",
            "kind": "BINARY",
        },
        {
            "destination": "ucrtbase.dll",
            "source": "C:/hostedtoolcache/windows/Java/bin/ucrtbase.dll",
            "kind": "BINARY",
        },
    )

    errors = MODULE.validate(entries, "win32")
    assert any("system runtime" in error and "ucrtbase.dll" in error for error in errors)


def test_windows_audit_allows_only_known_python_and_pyqt_local_runtimes():
    valid = qt_entries(
        {
            "destination": "VCRUNTIME140.dll",
            "source": "C:/hostedtoolcache/windows/Python/3.11.9/x64/VCRUNTIME140.dll",
            "kind": "BINARY",
        },
        {
            "destination": "PyQt6/Qt6/bin/MSVCP140.dll",
            "source": "C:/hostedtoolcache/windows/Python/3.11.9/x64/Lib/site-packages/PyQt6/Qt6/bin/MSVCP140.dll",
            "kind": "BINARY",
        },
    )
    assert MODULE.validate(valid, "win32") == []

    unexpected_name = qt_entries(
        {
            "destination": "concrt140.dll",
            "source": "C:/hostedtoolcache/windows/Python/3.11.9/x64/concrt140.dll",
            "kind": "BINARY",
        }
    )
    assert any("Unexpected Windows local runtime files" in error for error in MODULE.validate(unexpected_name, "win32"))

    unexpected_origin = qt_entries(
        {
            "destination": "VCRUNTIME140.dll",
            "source": "C:/hostedtoolcache/windows/Java/bin/VCRUNTIME140.dll",
            "kind": "BINARY",
        }
    )
    assert any("runtime origins" in error for error in MODULE.validate(unexpected_origin, "win32"))


def test_linux_audit_requires_desktop_and_test_platforms():
    entries = [
        entry for entry in qt_entries()
        if "/platforms/" not in entry["destination"]
    ] + [
        {"destination": "PyQt6/Qt6/plugins/platforms/libqxcb.so", "source": "xcb", "kind": "BINARY"},
        {"destination": "PyQt6/Qt6/plugins/platforms/libqwayland.so", "source": "wayland", "kind": "BINARY"},
        {"destination": "PyQt6/Qt6/plugins/platforms/libqoffscreen.so", "source": "offscreen", "kind": "BINARY"},
    ]

    assert MODULE.validate(entries, "linux") == []


def test_linux_audit_rejects_bundled_operating_system_library():
    entries = [
        entry for entry in qt_entries()
        if "/platforms/" not in entry["destination"]
    ] + [
        {"destination": "PyQt6/Qt6/plugins/platforms/libqxcb.so", "source": "/opt/qt/libqxcb.so", "kind": "BINARY"},
        {"destination": "PyQt6/Qt6/plugins/platforms/libqwayland.so", "source": "/opt/qt/libqwayland.so", "kind": "BINARY"},
        {"destination": "PyQt6/Qt6/plugins/platforms/libqoffscreen.so", "source": "/opt/qt/libqoffscreen.so", "kind": "BINARY"},
        {"destination": "libssl.so.3", "source": "/usr/lib/x86_64-linux-gnu/libssl.so.3", "kind": "BINARY"},
    ]

    assert any("libssl.so.3" in error for error in MODULE.validate(entries, "linux"))


def test_build_audit_reads_pyinstaller_toc(tmp_path):
    toc = tmp_path / "Analysis-00.toc"
    toc.write_text(
        repr(
            (
                ["app/main.py"],
                [
                    ("PyQt6/Qt6/bin/Qt6Core.dll", "source", "BINARY"),
                    ("app.module", "source", "PYMODULE"),
                ],
            )
        ),
        encoding="utf-8",
    )

    assert MODULE.packaged_entries(MODULE.read_toc(toc)) == [
        {
            "destination": "PyQt6/Qt6/bin/Qt6Core.dll",
            "source": "source",
            "kind": "BINARY",
        }
    ]


def test_release_workflows_audit_and_package_native_inventory():
    for workflow_name in ("build-windows-exe.yml", "build-linux.yml"):
        workflow = (ROOT / ".github" / "workflows" / workflow_name).read_text(encoding="utf-8")
        assert "scripts/audit_pyinstaller_build.py" in workflow
        assert "release-native-inventory.json" in workflow
