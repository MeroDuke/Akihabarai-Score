import json

from app import build_metadata


def test_load_build_info_reads_valid_embedded_identity(tmp_path):
    path = tmp_path / "build-info.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "commit": "abc123",
                "ref": "feature/test",
                "run_id": "42",
                "timestamp": "2026-09-28T12:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    assert build_metadata.load_build_info(path) == {
        "build_commit": "abc123",
        "build_ref": "feature/test",
        "build_run_id": "42",
        "build_timestamp": "2026-09-28T12:00:00+00:00",
    }


def test_load_build_info_rejects_unknown_schema(tmp_path):
    path = tmp_path / "build-info.json"
    path.write_text('{"schema_version": 999}', encoding="utf-8")

    assert set(build_metadata.load_build_info(path).values()) == {"unknown"}
