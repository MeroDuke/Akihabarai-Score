import re
from pathlib import Path

from app.version import APP_VERSION


def test_pyproject_version_matches_application_version():
    pyproject_text = (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(
        encoding="utf-8"
    )
    match = re.search(r'^version\s*=\s*"([^"]+)"$', pyproject_text, re.MULTILINE)

    assert match is not None
    assert match.group(1) == APP_VERSION
