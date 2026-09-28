import ast
from pathlib import Path


ROOT = Path(__file__).parents[1]
SPEC_PATH = ROOT / "AkihabaraiScore.spec"


def test_pyinstaller_spec_is_valid_python_and_excludes_pdf_only():
    source = SPEC_PATH.read_text(encoding="utf-8")
    ast.parse(source)

    assert '"PyQt6.QtPdf"' in source
    assert '"PyQt6.QtPdfWidgets"' in source
    assert "qpdf" in source.casefold()
    assert '"PyQt6.QtSvg"' in source
    assert "qsvg" in source.casefold()
    assert "qt6network" not in source.casefold()
    assert '"icu.dll", "icuin.dll", "icuuc.dll"' in source
    assert 'basename.startswith("icudt")' in source
    assert "a.binaries =" in source
    assert "a.datas =" in source
    assert "a.exclude_system_libraries()" in source
    assert '["app/launcher.py"]' in source
    assert 'Path("build-metadata/build-info.json")' in source
    assert "datas=build_info_datas" in source


def test_linux_runtime_contract_is_explicit_and_ci_driven():
    packages = (
        ROOT / "packaging" / "linux" / "ubuntu-24.04-runtime-packages.txt"
    ).read_text(encoding="utf-8").splitlines()
    workflow = (ROOT / ".github" / "workflows" / "build-linux.yml").read_text(encoding="utf-8")

    assert "libgtk-3-0t64" in packages
    assert "libxkbcommon-x11-0" in packages
    assert "libwayland-client0" in packages
    assert "ubuntu-24.04-runtime-packages.txt" in workflow


def test_release_workflows_build_from_the_audited_spec():
    for workflow_name in ("build-windows-exe.yml", "build-linux.yml"):
        workflow = (ROOT / ".github" / "workflows" / workflow_name).read_text(encoding="utf-8")
        assert "pyinstaller --clean --noconfirm AkihabaraiScore.spec" in workflow
        assert "scripts/generate_build_info.py" in workflow
        assert "scripts/smoke_test_packaged_app.py" in workflow
        assert "scripts/test_packaged_native_crash.py" in workflow
