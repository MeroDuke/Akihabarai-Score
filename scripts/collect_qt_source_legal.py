"""Extract Qt license and attribution material from verified source archives."""

from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
import shutil
import sys
import tarfile


LEGAL_NAMES = {"qt_attribution.json", "reuse.toml"}
LEGAL_PREFIXES = ("license", "licence", "copying", "copyright", "notice")
MAX_LEGAL_FILE_SIZE = 8 * 1024 * 1024


def is_legal_member(name: str) -> bool:
    path = PurePosixPath(name)
    lowered_parts = [part.casefold() for part in path.parts]
    basename = path.name.casefold()
    return (
        "licenses" in lowered_parts
        or basename in LEGAL_NAMES
        or basename.startswith(LEGAL_PREFIXES)
    )


def safe_relative_name(name: str) -> Path:
    archive_path = PurePosixPath(name)
    parts = archive_path.parts
    if archive_path.is_absolute():
        raise ValueError(f"Unsafe archive member path: {name}")
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise ValueError(f"Unsafe archive member path: {name}")
    # Source tarballs have one top-level directory; omit it from the legal tree.
    relative_parts = parts[1:] if len(parts) > 1 else parts
    return Path(*relative_parts)


def extract_legal_files(archive: Path, output: Path) -> int:
    component_output = output / archive.name.replace(".tar.xz", "")
    extracted = 0
    with tarfile.open(archive, mode="r:xz") as source:
        for member in source.getmembers():
            if not member.isfile() or not is_legal_member(member.name):
                continue
            if member.size > MAX_LEGAL_FILE_SIZE:
                raise ValueError(f"Legal file exceeds size limit: {member.name}")
            relative = safe_relative_name(member.name)
            destination = component_output / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            file_object = source.extractfile(member)
            if file_object is None:
                raise ValueError(f"Unable to read archive member: {member.name}")
            with file_object, destination.open("wb") as target:
                shutil.copyfileobj(file_object, target)
            extracted += 1
    return extracted


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archives", type=Path, default=Path("release-sources"))
    parser.add_argument("--output", type=Path, default=Path("build/release-legal/qt-source"))
    args = parser.parse_args()

    try:
        qt_archives = sorted(args.archives.glob("qt*-everywhere-src-*.tar.xz"))
        if not qt_archives:
            raise ValueError("No verified Qt source archives found")
        total = sum(extract_legal_files(archive, args.output) for archive in qt_archives)
        if total == 0:
            raise ValueError("No Qt legal or attribution files were extracted")
        print(f"Extracted {total} Qt legal and attribution files")
    except (OSError, tarfile.TarError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
