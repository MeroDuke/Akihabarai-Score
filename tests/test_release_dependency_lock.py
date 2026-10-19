import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
SCRIPT_PATH = ROOT / "scripts" / "generate_release_sbom.py"
SPEC = importlib.util.spec_from_file_location("generate_release_sbom", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_runtime_lock_matches_component_inventory():
    locked = MODULE.read_lock(ROOT / "requirements-release.txt")
    inventory = json.loads(
        (ROOT / "compliance" / "runtime-components.json").read_text(encoding="utf-8")
    )

    expected = {
        package["name"].casefold().replace("_", "-"): package["version"]
        for package in inventory["python_packages"]
    }
    actual = {key: version for key, (_, version) in locked.items()}
    assert actual == expected


def test_sbom_contains_every_locked_runtime_package():
    locked = MODULE.read_lock(ROOT / "requirements-release.txt")
    sbom = MODULE.build_sbom(locked)

    assert sbom["bomFormat"] == "CycloneDX"
    assert sbom["specVersion"] == "1.6"
    assert len(sbom["components"]) == len(locked)
    assert all(component["purl"].startswith("pkg:pypi/") for component in sbom["components"])


def test_lock_parser_rejects_unpinned_requirement(tmp_path):
    lock = tmp_path / "requirements.txt"
    lock.write_text("requests>=2\n", encoding="utf-8")

    try:
        MODULE.read_lock(lock)
    except ValueError as error:
        assert "Unpinned" in str(error) or "unpinned" in str(error)
    else:
        raise AssertionError("Unpinned requirement was accepted")
