"""Download and verify pinned corresponding-source archives for a release."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlparse
from urllib.request import urlopen


def read_manifest(path: Path) -> list[dict[str, str]]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        raise ValueError("Unsupported source archive manifest schema")
    archives = manifest.get("archives")
    if not isinstance(archives, list) or not archives:
        raise ValueError("Source archive manifest is empty")

    names = set()
    for archive in archives:
        for field in ("component", "version", "url", "sha256"):
            if not archive.get(field):
                raise ValueError(f"Source archive is missing {field}")
        parsed = urlparse(archive["url"])
        if parsed.scheme != "https" or not parsed.path.rsplit("/", 1)[-1]:
            raise ValueError(f"Source archive URL must be a named HTTPS resource: {archive['url']}")
        filename = parsed.path.rsplit("/", 1)[-1]
        if filename in names:
            raise ValueError(f"Duplicate source archive filename: {filename}")
        names.add(filename)
        digest = archive["sha256"]
        if len(digest) != 64:
            raise ValueError(f"Invalid SHA-256 for {archive['component']}")
        int(digest, 16)
    return archives


def download_archive(archive: dict[str, str], output: Path) -> Path:
    filename = urlparse(archive["url"]).path.rsplit("/", 1)[-1]
    destination = output / filename
    partial = output / f"{filename}.part"

    if destination.is_file():
        existing_digest = hashlib.sha256()
        with destination.open("rb") as existing:
            while chunk := existing.read(1024 * 1024):
                existing_digest.update(chunk)
        if existing_digest.hexdigest() == archive["sha256"]:
            return destination

    digest = hashlib.sha256()

    with urlopen(archive["url"], timeout=120) as response, partial.open("wb") as target:
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)
            target.write(chunk)

    actual = digest.hexdigest()
    if actual != archive["sha256"]:
        partial.unlink(missing_ok=True)
        raise ValueError(
            f"SHA-256 mismatch for {archive['component']}: {actual} != {archive['sha256']}"
        )
    partial.replace(destination)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("compliance/source-archives.json"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    try:
        archives = read_manifest(args.manifest)
        if args.validate_only:
            return 0
        if args.output is None:
            raise ValueError("--output is required unless --validate-only is used")
        args.output.mkdir(parents=True, exist_ok=True)
        for archive in archives:
            downloaded = download_archive(archive, args.output)
            print(f"Verified source archive: {downloaded}")
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
