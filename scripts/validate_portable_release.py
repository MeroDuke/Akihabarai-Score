"""Validate the assembled portable release before it is archived or published."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys


COMMON_FILES = (
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "SOURCE_AVAILABILITY.md",
    "release-sbom-python.cdx.json",
    "release-native-inventory.json",
    "source-archives.json",
    "assets/icon.ico",
    "config/app.json",
    "config/profiles.json",
    "config/ui.json",
    "config/locales/hu.json",
    "config/locales/en.json",
    "licenses/project-assets.json",
)


def normalized(value: str) -> str:
    return str(PurePosixPath(value.replace("\\", "/"))).casefold()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate(root: Path, platform: str, tag_build: bool = False) -> list[str]:
    errors = []
    executable = "AkihabaraiScore.exe" if platform == "windows" else "AkihabaraiScore"
    required = [*COMMON_FILES, executable]
    if platform == "windows":
        required.append("licenses/microsoft-runtime.json")
    else:
        required.extend(
            (
                "LINUX_RUNTIME.md",
                "ubuntu-24.04-runtime-packages.txt",
                "release-linux-packages.json",
            )
        )
    if tag_build:
        required.append("licenses/qt-source/qt-attributions.json")

    for relative in required:
        path = root / relative
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"Required release file missing or empty: {relative}")
    if errors:
        return errors

    if "GNU GENERAL PUBLIC LICENSE" not in (root / "LICENSE").read_text(
        encoding="utf-8", errors="replace"
    ):
        errors.append("Release LICENSE is not the complete GPL text")

    sbom = read_json(root / "release-sbom-python.cdx.json")
    if sbom.get("bomFormat") != "CycloneDX" or not sbom.get("components"):
        errors.append("Python CycloneDX SBOM has no components")

    inventory = read_json(root / "release-native-inventory.json")
    entries = inventory.get("entries", [])
    if inventory.get("schema_version") != 1 or not entries:
        errors.append("Native release inventory is empty or unsupported")

    sources = read_json(root / "source-archives.json")
    if sources.get("schema_version") != 1 or not sources.get("archives"):
        errors.append("Corresponding-source manifest is empty or unsupported")

    asset_record = read_json(root / "licenses/project-assets.json")["assets"][0]
    icon_digest = hashlib.sha256((root / "assets/icon.ico").read_bytes()).hexdigest()
    if asset_record.get("path") != "assets/icon.ico" or asset_record.get("sha256") != icon_digest:
        errors.append("Packaged icon does not match its provenance record")

    if platform == "windows":
        runtime = read_json(root / "licenses/microsoft-runtime.json")
        recorded = {normalized(item["destination"]) for item in runtime.get("files", [])}
        packaged = {
            normalized(entry["destination"])
            for entry in entries
            if normalized(entry["destination"]).rsplit("/", 1)[-1].startswith(
                ("msvcp", "vcruntime", "concrt")
            )
        }
        if packaged != recorded:
            errors.append(
                f"Packaged Microsoft runtime set differs from provenance: {packaged} != {recorded}"
            )
    else:
        bundled_system = [
            entry["source"]
            for entry in entries
            if normalized(entry["source"]).startswith(("/lib/", "/usr/lib/"))
        ]
        if bundled_system:
            errors.append(f"Linux system libraries are bundled: {bundled_system}")

    if tag_build:
        attributions = read_json(root / "licenses/qt-source/qt-attributions.json")
        if attributions.get("schema_version") != 1 or not attributions.get("entries"):
            errors.append("Qt attribution index is empty or unsupported")

    legal_files = [path for path in (root / "licenses").rglob("*") if path.is_file()]
    if len(legal_files) < 3:
        errors.append("Release legal directory does not contain dependency license material")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("release"))
    parser.add_argument("--platform", choices=("windows", "linux"), required=True)
    parser.add_argument("--tag-build", action="store_true")
    args = parser.parse_args()

    try:
        errors = validate(args.root, args.platform, args.tag_build)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        errors = [f"Unable to validate portable release: {error}"]
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Validated {args.platform} portable release at {args.root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
