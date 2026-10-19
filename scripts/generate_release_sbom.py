"""Validate the release lock and emit a CycloneDX Python dependency SBOM."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
from pathlib import Path
import re
import sys


LOCK_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+)==([^;\s]+)")


def read_lock(path: Path) -> dict[str, tuple[str, str]]:
    packages: dict[str, tuple[str, str]] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = LOCK_PATTERN.match(line)
        if not match:
            raise ValueError(f"Unsupported unpinned requirement: {raw_line}")
        name, version = match.groups()
        key = name.casefold().replace("_", "-")
        if key in packages:
            raise ValueError(f"Duplicate locked package: {name}")
        packages[key] = (name, version)
    return packages


def validate_installed(packages: dict[str, tuple[str, str]]) -> list[str]:
    errors: list[str] = []
    for name, expected in packages.values():
        try:
            actual = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            errors.append(f"{name} is not installed (expected {expected})")
            continue
        if actual != expected:
            errors.append(f"{name} is {actual}, expected {expected}")
    return errors


def build_sbom(packages: dict[str, tuple[str, str]]) -> dict:
    components = []
    for name, version in sorted(packages.values(), key=lambda item: item[0].casefold()):
        normalized = name.lower().replace("_", "-")
        components.append(
            {
                "type": "library",
                "bom-ref": f"pkg:pypi/{normalized}@{version}",
                "name": name,
                "version": version,
                "purl": f"pkg:pypi/{normalized}@{version}",
            }
        )
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "version": 1,
        "metadata": {"component": {"type": "application", "name": "Akihabarai Score"}},
        "components": components,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", type=Path, default=Path("requirements-release.txt"))
    parser.add_argument("--output", type=Path, default=Path("release-sbom-python.cdx.json"))
    parser.add_argument("--validate-installed", action="store_true")
    args = parser.parse_args()

    packages = read_lock(args.lock)
    if args.validate_installed:
        errors = validate_installed(packages)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1

    args.output.write_text(
        json.dumps(build_sbom(packages), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
