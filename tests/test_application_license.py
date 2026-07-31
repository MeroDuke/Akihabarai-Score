from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_application_uses_complete_gpl_v3_license():
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")

    assert "GNU GENERAL PUBLIC LICENSE" in license_text
    assert "Version 3, 29 June 2007" in license_text
    assert "END OF TERMS AND CONDITIONS" in license_text
    assert len(license_text.splitlines()) > 600


def test_project_metadata_declares_gpl_3_only():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert 'license = "GPL-3.0-only"' in pyproject


def test_retired_custom_restrictions_are_not_in_application_license():
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8").casefold()

    retired_phrases = (
        "personal, non-commercial use only",
        "modifying, transforming, reverse engineering",
        "strictly prohibited without prior written permission",
        "kizárólag személyes, nem kereskedelmi célra",
        "módosítása, átalakítása, visszafejtése",
    )
    assert not any(phrase in license_text for phrase in retired_phrases)


def test_release_workflows_package_application_license():
    for workflow_name in ("build-windows-exe.yml", "build-linux.yml"):
        workflow = (ROOT / ".github" / "workflows" / workflow_name).read_text(encoding="utf-8")
        assert "LICENSE" in workflow
