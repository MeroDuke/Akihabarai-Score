# -*- mode: python ; coding: utf-8 -*-
"""Cross-platform PyInstaller recipe with audited runtime exclusions."""

from pathlib import PurePosixPath
import sys


def normalized_destination(entry):
    return str(PurePosixPath(entry[0].replace("\\", "/"))).casefold()


def is_excluded_binary(entry):
    destination = normalized_destination(entry)
    excluded_markers = (
        "/plugins/imageformats/qpdf",
        "/plugins/imageformats/libqpdf",
        "/qt6pdf.dll",
        "/libqt6pdf.so",
        "/qt6pdf.framework/",
        "/plugins/imageformats/qicns",
        "/plugins/imageformats/libqicns",
        "/plugins/imageformats/qsvg",
        "/plugins/imageformats/libqsvg",
        "/plugins/imageformats/qtga",
        "/plugins/imageformats/libqtga",
        "/plugins/imageformats/qtiff",
        "/plugins/imageformats/libqtiff",
        "/plugins/imageformats/qwbmp",
        "/plugins/imageformats/libqwbmp",
        "/qt6svg.dll",
        "/libqt6svg.so",
        "/qt6svg.framework/",
    )
    return any(marker in destination for marker in excluded_markers)


a = Analysis(
    ["app/main.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["PyQt6.QtPdf", "PyQt6.QtPdfWidgets", "PyQt6.QtSvg", "PyQt6.QtSvgWidgets"],
    noarchive=False,
    optimize=0,
)

# QtGui's dynamic image-plugin discovery collects formats outside the product's
# input/output contract. Filtering is deliberately applied after Analysis,
# where platform-specific binary names are known. JPEG, PNG, ICO, WebP, and GIF
# support remains available for covers, the application icon, and exports.
a.binaries = type(a.binaries)(entry for entry in a.binaries if not is_excluded_binary(entry))

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="AkihabaraiScore",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icon.ico" if sys.platform == "win32" else None,
)
