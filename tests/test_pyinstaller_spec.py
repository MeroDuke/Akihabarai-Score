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
    assert "a.binaries =" in source
    assert "a.datas =" in source
    assert "a.exclude_system_libraries()" in source


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
