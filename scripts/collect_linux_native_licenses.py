"""Map packaged Linux system libraries to dpkg packages and legal files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


SYSTEM_LIBRARY_ROOTS = (Path("/lib"), Path("/usr/lib"))


def is_system_library(path: Path) -> bool:
    return any(path == root or root in path.parents for root in SYSTEM_LIBRARY_ROOTS)


def query_owner(path: Path) -> str | None:
    candidates = [path]
    try:
        resolved = path.resolve(strict=True)
    except OSError:
        resolved = path
    if resolved not in candidates:
        candidates.append(resolved)

    for candidate in candidates:
        result = subprocess.run(
            ["dpkg-query", "-S", str(candidate)],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and ": " in result.stdout:
            return result.stdout.split(": ", 1)[0].strip()
    return None


def query_package(package: str) -> dict[str, str] | None:
    result = subprocess.run(
        [
            "dpkg-query",
            "-W",
            "-f=${binary:Package}\\t${Version}\\t${source:Package}\\t${source:Version}",
            package,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    fields = result.stdout.strip().split("\t")
    if len(fields) != 4:
        return None
    binary, version, source, source_version = fields
    source = source or binary.split(":", 1)[0]
    source_version = source_version or version
    return {
        "binary_package": binary,
        "version": version,
        "source_package": source,
        "source_version": source_version,
    }


def copyright_path(binary_package: str) -> Path:
    package_without_arch = binary_package.split(":", 1)[0]
    return Path("/usr/share/doc") / package_without_arch / "copyright"


def collect(inventory_path: Path, output: Path, legal_output: Path) -> list[str]:
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    system_entries = {
        Path(entry["source"])
        for entry in inventory["entries"]
        if entry["kind"] in {"BINARY", "EXTENSION"} and is_system_library(Path(entry["source"]))
    }

    errors: list[str] = []
    packages: dict[str, dict] = {}
    for library in sorted(system_entries, key=str):
        owner = query_owner(library)
        if owner is None:
            errors.append(f"No dpkg owner found for {library}")
            continue
        package = query_package(owner)
        if package is None:
            errors.append(f"Package metadata unavailable for {owner} ({library})")
            continue
        package_entry = packages.setdefault(
            package["binary_package"],
            {**package, "libraries": []},
        )
        package_entry["libraries"].append(str(library))

    for package in packages.values():
        source = copyright_path(package["binary_package"])
        if not source.is_file():
            errors.append(f"Copyright file unavailable for {package['binary_package']}: {source}")
            continue
        destination = legal_output / package["binary_package"].replace(":", "-")
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination / "copyright")

    output.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "platform": "linux",
                "generator": "scripts/collect_linux_native_licenses.py",
                "packages": sorted(packages.values(), key=lambda item: item["binary_package"]),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return errors


def main() -> int:
    if not sys.platform.startswith("linux"):
        print("Linux native license collection requires Linux", file=sys.stderr)
        return 2

    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, default=Path("release-native-inventory.json"))
    parser.add_argument("--output", type=Path, default=Path("release-linux-packages.json"))
    parser.add_argument(
        "--legal-output",
        type=Path,
        default=Path("build/release-legal/linux-packages"),
    )
    args = parser.parse_args()

    errors = collect(args.inventory, args.output, args.legal_output)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
