import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
PROVENANCE_PATH = ROOT / "compliance" / "asset-provenance.json"


def test_distributed_icon_matches_its_provenance_record():
    provenance = json.loads(PROVENANCE_PATH.read_text(encoding="utf-8"))

    assert provenance["schema_version"] == 1
    assert len(provenance["assets"]) == 1
    record = provenance["assets"][0]
    asset = ROOT / record["path"]
    assert asset.is_file()
    assert hashlib.sha256(asset.read_bytes()).hexdigest() == record["sha256"]
    assert record["origin"]["type"] == "ai-generated-output"
    assert record["origin"]["known_specific_references"] == []
    assert record["rights_record"]["limitations"]


def test_release_workflows_package_asset_provenance():
    for workflow_name in ("build-windows-exe.yml", "build-linux.yml"):
        workflow = (ROOT / ".github" / "workflows" / workflow_name).read_text(encoding="utf-8")
        assert "asset-provenance.json" in workflow
        assert "project-assets.json" in workflow
