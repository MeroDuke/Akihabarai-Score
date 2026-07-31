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
        *additional,
    ]


def test_build_audit_accepts_required_qt_runtime_without_pdf():
    entries = qt_entries()

    assert MODULE.validate(entries) == []
    assert MODULE.build_inventory(entries)["entry_count"] == 6


def test_build_audit_rejects_pdf_library_and_plugin():
    entries = qt_entries(
        {"destination": "PyQt6/Qt6/bin/Qt6Pdf.dll", "source": "pdf", "kind": "BINARY"},
        {
            "destination": "PyQt6/Qt6/plugins/imageformats/qpdf.dll",
            "source": "qpdf",
            "kind": "BINARY",
        },
    )

    errors = MODULE.validate(entries)
    assert any("qt6pdf" in error for error in errors)
    assert any("qpdf" in error for error in errors)


def test_build_audit_rejects_unsupported_image_plugins():
    entries = qt_entries(
        {"destination": "PyQt6/Qt6/plugins/imageformats/qsvg.dll", "source": "svg", "kind": "BINARY"}
    )

    assert any("qsvg" in error for error in MODULE.validate(entries))


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
