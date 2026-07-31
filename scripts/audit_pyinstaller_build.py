"""Audit a PyInstaller Analysis TOC and emit the packaged native inventory."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path, PurePosixPath
import sys


FORBIDDEN_MARKERS = (
    "qt6pdf",
    "qt6svg",
    "/imageformats/qpdf",
    "/imageformats/libqpdf",
    "/imageformats/qicns",
    "/imageformats/libqicns",
    "/imageformats/qsvg",
    "/imageformats/libqsvg",
    "/imageformats/qtga",
    "/imageformats/libqtga",
    "/imageformats/qtiff",
    "/imageformats/libqtiff",
    "/imageformats/qwbmp",
    "/imageformats/libqwbmp",
    "pyqt6.qtpdf",
    "pyqt6.qtsvg",
)
REQUIRED_QT_MARKERS = ("qt6core", "qt6gui", "qt6widgets")
REQUIRED_IMAGE_PLUGIN_MARKERS = ("/imageformats/qico", "/imageformats/qjpeg", "/imageformats/qwebp")


def normalized_path(value: str) -> str:
    return str(PurePosixPath(value.replace("\\", "/"))).casefold()


def read_toc(path: Path) -> list[tuple]:
    value = ast.literal_eval(path.read_text(encoding="utf-8"))
    if not isinstance(value, (list, tuple)):
        raise ValueError("PyInstaller TOC root must be a list or tuple")
    return list(value)


def packaged_entries(toc: list[tuple]) -> list[dict[str, str]]:
    entries = []

    def visit(value):
        if (
            isinstance(value, tuple)
            and len(value) >= 3
            and all(isinstance(part, str) for part in value[:3])
            and value[2] in {"BINARY", "DATA", "EXTENSION"}
        ):
            destination, source, kind = value[:3]
            entries.append(
                {
                    "destination": destination.replace("\\", "/"),
                    "source": source,
                    "kind": kind,
                }
            )
            return
        if isinstance(value, (list, tuple)):
            for child in value:
                visit(child)

    visit(toc)
    return sorted(entries, key=lambda entry: entry["destination"].casefold())


def validate(entries: list[dict[str, str]]) -> list[str]:
    destinations = [normalized_path(entry["destination"]) for entry in entries]
    errors = []
    for marker in FORBIDDEN_MARKERS:
        matches = [path for path in destinations if marker in path]
        if matches:
            errors.append(f"Forbidden packaged component {marker}: {matches}")
    for marker in REQUIRED_QT_MARKERS:
        if not any(marker in path for path in destinations):
            errors.append(f"Required packaged Qt component missing: {marker}")
    for marker in REQUIRED_IMAGE_PLUGIN_MARKERS:
        if not any(marker in path or f"/imageformats/lib{marker.rsplit('/', 1)[-1]}" in path for path in destinations):
            errors.append(f"Required packaged image plugin missing: {marker}")
    return errors


def build_inventory(entries: list[dict[str, str]]) -> dict:
    return {
        "schema_version": 1,
        "generator": "scripts/audit_pyinstaller_build.py",
        "platform": sys.platform,
        "entry_count": len(entries),
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--toc", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("release-native-inventory.json"))
    args = parser.parse_args()

    entries = packaged_entries(read_toc(args.toc))
    errors = validate(entries)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    args.output.write_text(
        json.dumps(build_inventory(entries), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
