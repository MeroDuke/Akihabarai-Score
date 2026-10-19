import json
from pathlib import Path


INVENTORY_PATH = Path(__file__).parents[1] / "compliance" / "runtime-components.json"


def test_runtime_component_inventory_is_machine_readable_and_complete():
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))

    assert inventory["schema_version"] == 1
    assert inventory["baseline"]["release"] == "0.23.0"
    assert len(inventory["baseline"]["commit"]) == 40

    for artifact in inventory["baseline"]["artifacts"].values():
        assert artifact["name"]
        assert len(artifact["sha256"]) == 64

    packages = inventory["python_packages"]
    names = [package["name"].casefold() for package in packages]
    assert len(names) == len(set(names))
    assert {"pyqt6", "requests", "certifi", "urllib3"}.issubset(names)

    allowed_statuses = {"confirmed", "candidate", "unresolved", "resolved"}
    for section in ("python_packages", "runtime_families", "external_services", "exclusion_candidates"):
        for component in inventory[section]:
            assert component["name"]
            assert component["status"] in allowed_statuses

    assert inventory["application_license_gate"]["current_status"] == "resolved"
    assert inventory["application_license_gate"]["selected_path"] == "GPL-3.0-only"
    exclusions = {
        component["name"]: component["status"]
        for component in inventory["exclusion_candidates"]
    }
    assert exclusions["Qt PDF module and PDF image plugin"] == "resolved"
    assert exclusions["Qt SVG module and SVG image plugin"] == "resolved"
    assert exclusions["Non-target Qt platform plugins"] == "resolved"
