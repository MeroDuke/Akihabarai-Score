"""Verify that a packaged application reaches its visible startup boundary."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path


READY_MESSAGE = "Main window ready"


def log_contains(log_directory: Path, message: str) -> bool:
    for path in log_directory.glob("*.log"):
        try:
            if message in path.read_text(encoding="utf-8", errors="replace"):
                return True
        except OSError:
            continue
    return False


def crash_logs(log_directory: Path) -> list[str]:
    return sorted(path.name for path in log_directory.glob("crash-*.log"))


def stop_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def run_smoke_test(
    command: list[str],
    *,
    working_directory: Path,
    log_directory: Path,
    timeout_seconds: float,
    poll_seconds: float = 0.1,
) -> dict:
    command = list(command)
    executable = Path(command[0])
    if not executable.is_absolute():
        command[0] = str((working_directory / executable).resolve())

    log_directory.mkdir(parents=True, exist_ok=True)
    for path in log_directory.glob("*.log"):
        path.unlink()

    report = {
        "command": command,
        "working_directory": str(working_directory),
        "timeout_seconds": timeout_seconds,
        "process_started": False,
        "pid": None,
        "exit_code": None,
        "ready": False,
        "crash_logs": [],
        "result": "FAIL",
        "reason": "",
    }
    process = subprocess.Popen(command, cwd=working_directory, env=os.environ.copy())
    report["process_started"] = True
    report["pid"] = process.pid
    deadline = time.monotonic() + timeout_seconds

    try:
        while time.monotonic() < deadline:
            report["crash_logs"] = crash_logs(log_directory)
            if report["crash_logs"]:
                report["reason"] = "Startup crash log was created"
                report["exit_code"] = process.poll()
                return report

            if log_contains(log_directory, READY_MESSAGE):
                report["ready"] = True
                report["result"] = "PASS"
                report["reason"] = "Application reached the main-window startup boundary"
                return report

            exit_code = process.poll()
            if exit_code is not None:
                report["exit_code"] = exit_code
                report["reason"] = "Application exited before startup completed"
                return report
            time.sleep(poll_seconds)

        report["reason"] = "Application did not become ready before the timeout"
        report["exit_code"] = process.poll()
        return report
    finally:
        stop_process(process)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--log-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        parser.error("a command is required after --")
    return args


def main() -> int:
    args = parse_args()
    report = run_smoke_test(
        args.command,
        working_directory=args.cwd.resolve(),
        log_directory=args.log_dir.resolve(),
        timeout_seconds=args.timeout,
    )
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(report["reason"])
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
