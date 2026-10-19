"""Validate release version metadata and, on tag builds, the Git tag."""

from __future__ import annotations

import argparse
import os
import re
import sys
import tomllib
from pathlib import Path


VERSION_ASSIGNMENT = re.compile(r'^APP_VERSION\s*=\s*"([^"]+)"$', re.MULTILINE)


def read_application_version(root: Path) -> str:
    text = (root / "app" / "version.py").read_text(encoding="utf-8")
    match = VERSION_ASSIGNMENT.search(text)
    if match is None:
        raise ValueError("APP_VERSION is missing from app/version.py")
    return match.group(1)


def read_package_version(root: Path) -> str:
    with (root / "pyproject.toml").open("rb") as handle:
        return str(tomllib.load(handle)["project"]["version"])


def validate(root: Path, tag: str | None = None) -> list[str]:
    errors: list[str] = []

    try:
        application_version = read_application_version(root)
    except (OSError, ValueError) as error:
        return [str(error)]

    try:
        package_version = read_package_version(root)
    except (OSError, KeyError, tomllib.TOMLDecodeError) as error:
        return [f"Unable to read pyproject.toml version: {error}"]

    if package_version != application_version:
        errors.append(
            "Version mismatch: app/version.py is "
            f"{application_version}, pyproject.toml is {package_version}"
        )

    try:
        changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"Unable to read CHANGELOG.md: {error}")
    else:
        if tag is not None:
            release_state = r"\d{4}-\d{2}-\d{2}"
        else:
            release_state = r"(?:Unreleased|\d{4}-\d{2}-\d{2})"
        header = re.compile(
            rf"^## \[{re.escape(application_version)}\] - {release_state}$",
            re.MULTILINE,
        )
        if header.search(changelog) is None:
            if tag is None:
                errors.append(
                    f"CHANGELOG.md has no release header for {application_version}"
                )
            else:
                errors.append(
                    "CHANGELOG.md has no dated release header for "
                    f"{application_version}"
                )

    if tag is not None:
        expected_tag = f"v{application_version}"
        if tag != expected_tag:
            errors.append(
                f"Release tag mismatch: received {tag}, expected {expected_tag}"
            )

    return errors


def tag_from_environment() -> str | None:
    if os.environ.get("GITHUB_REF_TYPE") == "tag":
        return os.environ.get("GITHUB_REF_NAME") or ""
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--tag", help="Release tag to compare with the version")
    args = parser.parse_args()

    tag = args.tag if args.tag is not None else tag_from_environment()
    errors = validate(args.root, tag)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    version = read_application_version(args.root)
    suffix = f" and tag {tag}" if tag is not None else ""
    print(f"Validated release version {version}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
