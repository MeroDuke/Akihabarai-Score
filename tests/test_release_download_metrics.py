import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
from urllib.error import HTTPError
import xml.etree.ElementTree as ET

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/release_download_metrics.py"
SPEC = importlib.util.spec_from_file_location("release_download_metrics", SCRIPT)
metrics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(metrics)


def release(count=12, asset_id=10, tag="v1.0.0"):
    return {"id": 1, "tag_name": tag, "draft": False, "prerelease": False,
            "assets": [{"id": asset_id, "name": "AkihabaraiScore-windows.zip", "download_count": count},
                       {"id": 20, "name": "AkihabaraiScore-linux-x86_64.tar.gz", "download_count": 3},
                       {"id": 30, "name": "qtbase-source.tar.xz", "download_count": 999}]}


def sample(count=12, asset_id=10, at="2026-11-01T05:17:00+00:00"):
    return metrics.snapshot([release(count, asset_id)], at)


def test_only_stable_application_archives_count():
    draft, preview = release(), release()
    draft["draft"], preview["prerelease"] = True, True
    result = metrics.snapshot([release(), draft, preview], "2026-11-01T07:17:00+02:00")
    assert result["observed_at"] == "2026-11-01T05:17:00+00:00"
    assert [a["downloads"] for a in result["assets"]] == [12, 3]


@pytest.mark.parametrize("count", [-1, "12", 1.2, True])
def test_invalid_counters_are_not_published(count):
    with pytest.raises(ValueError, match="Invalid download"):
        sample(count)


def test_duplicate_assets_fail():
    with pytest.raises(ValueError, match="Duplicate"):
        metrics.snapshot([release(), release()], "2026-11-01T00:00:00Z")


def test_pagination_and_auth_without_logging_token():
    urls = []
    def request(req, timeout):
        urls.append(req.full_url)
        assert req.get_header("Authorization") == "Bearer secret"
        assert timeout == 30
        data = [{"id": i} for i in range(100)] if len(urls) == 1 else [{"id": 100}]
        return io.BytesIO(json.dumps(data).encode())
    assert len(metrics.github_pages("repos/a/b/releases", "secret", request)) == 101
    assert urls[-1].endswith("per_page=100&page=2")


def test_fetches_asset_endpoint_separately():
    urls = []
    def request(req, timeout):
        urls.append(req.full_url)
        data = release()["assets"] if "/1/assets?" in req.full_url else [release()]
        return io.BytesIO(json.dumps(data).encode())
    assert len(metrics.fetch_releases("", request)[0]["assets"]) == 3
    assert len(urls) == 2


def test_asset_replacement_and_counter_decrease_remain_explicit():
    events = metrics.anomalies(sample(), sample(1, 11))
    assert any("Removed asset" in e for e in events)
    assert any("New asset" in e for e in events)
    assert "12 -> 1" in metrics.anomalies(sample(), sample(1))[0]


def test_failure_does_not_write_zero_or_touch_history(tmp_path):
    metrics.run(tmp_path, "2026-11-01T00:00:00Z", lambda: [release()])
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    def failed():
        raise HTTPError("https://api.github.com", 403, "Forbidden", {}, None)
    with pytest.raises(HTTPError):
        metrics.run(tmp_path, "2026-11-02T00:00:00Z", failed)
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before
    empty = tmp_path / "empty"
    with pytest.raises(HTTPError):
        metrics.run(empty, "2026-11-02T00:00:00Z", failed)
    assert not empty.exists()


def test_daily_repeat_is_idempotent_and_does_not_call_api(tmp_path):
    metrics.run(tmp_path, "2026-11-01T00:00:00Z", lambda: [release()])
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    def unexpected():
        raise AssertionError("same day should not query again")
    metrics.run(tmp_path, "2026-11-01T20:00:00Z", unexpected)
    assert {p.name: p.read_bytes() for p in tmp_path.iterdir()} == before
    with pytest.raises(ValueError, match="out-of-order"):
        metrics.run(tmp_path, "2026-10-31T20:00:00Z", unexpected)


def test_chart_escapes_labels_and_breaks_gaps_and_replaced_assets():
    history = {"2026-11-01": sample(), "2026-11-03": sample(20)}
    svg = metrics.chart(history)
    assert "stroke-width" not in svg  # No line across missing day.
    history["2026-11-02"] = sample(15)
    assert "stroke-width" in metrics.chart(history)
    history = {"2026-11-01": sample(), "2026-11-02": sample(20, 11)}
    # Linux unchanged can connect; replaced Windows cannot.
    assert metrics.chart(history).count('stroke-width="2"') == 1
    weird = metrics.snapshot([release(tag='<script>&"')], "2026-11-01T00:00:00Z")
    svg = metrics.chart({"2026-11-01": weird})
    ET.fromstring(svg)
    assert "<script>" not in svg


def test_complete_cli_workflow_from_fixture_to_history_graph_and_badges(tmp_path):
    fixture = tmp_path / "releases.json"
    output = tmp_path / "data"
    def cli(day, data):
        fixture.write_text(json.dumps(data), encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), "--output", str(output),
                               "--fixture", str(fixture), "--at", f"2026-11-{day}T05:17:00Z"],
                              capture_output=True, text=True)
    assert cli("01", [release()]).returncode == 0
    first = (output / "history.json").read_bytes()
    assert cli("01", [release(999)]).returncode == 0
    assert (output / "history.json").read_bytes() == first
    assert cli("03", [release(2, 11)]).returncode == 0
    history = json.loads((output / "history.json").read_text())["days"]
    assert len(history) == 2
    assert history["2026-11-01"]["assets"][0]["downloads"] == 12
    badge = json.loads((output / "windows.json").read_text())
    assert badge["message"] == "2"
    assert "2026-11-03" in badge["label"]
    assert json.loads((output / "linux.json").read_text())["message"] == "3"
    events = json.loads((output / "events.json").read_text())
    assert any("missing day" in e for e in events)
    assert any("Removed asset" in e for e in events)
    ET.parse(output / "downloads.svg")
    assert "v1.0.0 | Windows | 2" in (output / "README.md").read_text()
    before = {p.name: p.read_bytes() for p in output.iterdir()}
    assert cli("04", [release(-5)]).returncode != 0
    assert {p.name: p.read_bytes() for p in output.iterdir()} == before


def test_workflow_is_separate_from_releases_and_cannot_write_main():
    workflow = (ROOT / ".github/workflows/download-metrics.yml").read_text()
    assert 'cron: "17 5 * * *"' in workflow
    assert "workflow_dispatch:" in workflow
    assert "HEAD:refs/heads/metrics/downloads" in workflow
    assert "--force" not in workflow
    assert "github.ref == 'refs/heads/main'" in workflow
    assert "contents: read" in workflow
    assert "gh release" not in workflow
    assert "upload-artifact" not in workflow
    persist_step = workflow.split("name: Persist data only", 1)[1]
    assert "GH_TOKEN: ${{ github.token }}" in persist_step


def test_readme_download_badges_use_filtered_dated_endpoints():
    readme = (ROOT / "readme.md").read_text(encoding="utf-8")
    assert "metrics/downloads/windows.json" in readme
    assert "metrics/downloads/linux.json" in readme
    assert "github/downloads" not in readme
