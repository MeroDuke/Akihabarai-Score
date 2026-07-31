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


def test_release_workflows_build_from_the_audited_spec():
    for workflow_name in ("build-windows-exe.yml", "build-linux.yml"):
        workflow = (ROOT / ".github" / "workflows" / workflow_name).read_text(encoding="utf-8")
        assert "pyinstaller --clean --noconfirm AkihabaraiScore.spec" in workflow
