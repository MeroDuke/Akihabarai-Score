"""Generate the immutable build identity embedded in packaged applications."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
from pathlib import Path


def git_value(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def build_info(now: dt.datetime | None = None) -> dict[str, object]:
    timestamp = now or dt.datetime.now(dt.timezone.utc)
    return {
        "schema_version": 1,
        "commit": os.environ.get("GITHUB_SHA") or git_value("rev-parse", "HEAD"),
        "ref": os.environ.get("GITHUB_REF_NAME")
        or git_value("branch", "--show-current")
        or "unknown",
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "timestamp": timestamp.isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("build-metadata/build-info.json"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build_info(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
