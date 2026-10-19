import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "validate_release_version.py"
SPEC = importlib.util.spec_from_file_location("validate_release_version", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def write_release_metadata(
    root: Path, version: str = "1.0.0", release_state: str = "Unreleased"
) -> None:
    (root / "app").mkdir()
    (root / "app" / "version.py").write_text(
        f'APP_VERSION = "{version}"\n', encoding="utf-8"
    )
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "example"\nversion = "{version}"\n',
        encoding="utf-8",
    )
    (root / "CHANGELOG.md").write_text(
        f"# Changelog\n\n## [{version}] - {release_state}\n", encoding="utf-8"
    )


def test_repository_release_metadata_is_consistent():
    assert MODULE.validate(ROOT) == []


def test_release_workflows_validate_version_before_packaging():
    for workflow_name in ("build-windows-exe.yml", "build-linux.yml"):
        workflow = (ROOT / ".github" / "workflows" / workflow_name).read_text(
            encoding="utf-8"
        )
        assert "python scripts/validate_release_version.py" in workflow
        assert workflow.index("validate_release_version.py") < workflow.index(
            "pyinstaller"
        )


def test_matching_release_tag_is_accepted(tmp_path):
    write_release_metadata(tmp_path, release_state="2026-12-01")
    assert MODULE.validate(tmp_path, "v1.0.0") == []


def test_mismatching_release_tag_fails(tmp_path):
    write_release_metadata(tmp_path, release_state="2026-12-01")
    assert MODULE.validate(tmp_path, "v1.0.1") == [
        "Release tag mismatch: received v1.0.1, expected v1.0.0"
    ]


def test_release_tag_rejects_unreleased_changelog(tmp_path):
    write_release_metadata(tmp_path)
    assert MODULE.validate(tmp_path, "v1.0.0") == [
        "CHANGELOG.md has no dated release header for 1.0.0"
    ]


def test_package_and_changelog_mismatches_are_reported(tmp_path):
    write_release_metadata(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "example"\nversion = "0.23.0"\n', encoding="utf-8"
    )
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    assert MODULE.validate(tmp_path) == [
        "Version mismatch: app/version.py is 1.0.0, pyproject.toml is 0.23.0",
        "CHANGELOG.md has no release header for 1.0.0",
    ]
