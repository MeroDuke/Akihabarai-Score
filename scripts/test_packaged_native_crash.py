"""Exercise the packaged application's real native-crash diagnostic path."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


def run_crash_workflow(
    command: list[str],
    *,
    working_directory: Path,
    log_directory: Path,
    platform_name: str,
    timeout_seconds: float = 30,
) -> dict:
    executable = Path(command[0])
    if not executable.is_absolute():
        command[0] = str((working_directory / executable).resolve())
    log_directory.mkdir(parents=True, exist_ok=True)
    before = {path.name for path in log_directory.iterdir()}
    environment = os.environ.copy()
    environment["AKIHABARAI_DIAGNOSTIC_TEST_CRASH"] = "ci-native-crash-test"
    process = subprocess.run(
        command,
        cwd=working_directory,
        env=environment,
        timeout=timeout_seconds,
        check=False,
    )
    new_files = sorted(
        path.name for path in log_directory.iterdir() if path.name not in before
    )
    diagnostic_buffers = [
        name for name in new_files if name.startswith("diagnostic-buffer-")
    ]
    summaries = [name for name in new_files if name.startswith("native-crash-")]
    dumps = [name for name in new_files if name.endswith(".dmp")]
    errors: list[str] = []
    if process.returncode == 0:
        errors.append("native crash test exited successfully")
    if not diagnostic_buffers:
        errors.append("fatal fault diagnostic buffer was not preserved")
    if platform_name == "windows":
        if not summaries:
            errors.append("Windows native crash summary was not created")
        if not dumps:
            errors.append("Windows minidump was not created")
    report = {
        "platform": platform_name,
        "returncode": process.returncode,
        "new_files": new_files,
        "diagnostic_buffers": diagnostic_buffers,
        "native_summaries": summaries,
        "minidumps": dumps,
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--log-dir", type=Path, required=True)
    parser.add_argument("--platform", choices=("windows", "linux"), required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        parser.error("a command is required after --")
    report = run_crash_workflow(
        args.command,
        working_directory=args.cwd.resolve(),
        log_directory=args.log_dir.resolve(),
        platform_name=args.platform,
    )
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
