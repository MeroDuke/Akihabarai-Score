"""Collect license files from the exact installed release dependencies."""

from __future__ import annotations

import argparse
import importlib.metadata
from pathlib import Path
import shutil
import sys

from generate_release_sbom import read_lock


LICENSE_PREFIXES = ("license", "licence", "copying", "notice")


def license_files(distribution: importlib.metadata.Distribution):
    for package_file in distribution.files or ():
        name = Path(str(package_file)).name.casefold()
        if name.startswith(LICENSE_PREFIXES):
            source = Path(distribution.locate_file(package_file))
            if source.is_file():
                yield source


def find_python_license() -> Path | None:
    for base in (Path(sys.base_prefix), Path(sys.prefix)):
        for name in ("LICENSE.txt", "LICENSE", "LICENSE.md"):
            candidate = base / name
            if candidate.is_file():
                return candidate
    return None


def collect(lock: Path, output: Path) -> list[str]:
    errors: list[str] = []
    output.mkdir(parents=True, exist_ok=True)

    for name, expected_version in read_lock(lock).values():
        try:
            distribution = importlib.metadata.distribution(name)
        except importlib.metadata.PackageNotFoundError:
            errors.append(f"{name} is not installed")
            continue
        actual_version = distribution.version
        if actual_version != expected_version:
            errors.append(f"{name} is {actual_version}, expected {expected_version}")
            continue

        sources = list(dict.fromkeys(license_files(distribution)))
        if not sources:
            errors.append(f"{name} {actual_version} has no discoverable license file")
            continue

        destination = output / "python-packages" / f"{name}-{actual_version}"
        destination.mkdir(parents=True, exist_ok=True)
        for index, source in enumerate(sources, start=1):
            target_name = source.name if len(sources) == 1 else f"{index:02d}-{source.name}"
            shutil.copyfile(source, destination / target_name)

    python_license = find_python_license()
    if python_license is None:
        errors.append("CPython runtime license was not found under sys.prefix")
    else:
        destination = output / "python-runtime"
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(python_license, destination / python_license.name)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", type=Path, default=Path("requirements-release.txt"))
    parser.add_argument("--output", type=Path, default=Path("build/release-legal"))
    args = parser.parse_args()

    errors = collect(args.lock, args.output)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
