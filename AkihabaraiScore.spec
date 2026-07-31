# -*- mode: python ; coding: utf-8 -*-
"""Cross-platform PyInstaller recipe with audited runtime exclusions."""

from pathlib import PurePosixPath
import sys


def normalized_destination(entry):
    return str(PurePosixPath(entry[0].replace("\\", "/"))).casefold()


def is_excluded_binary(entry):
    destination = normalized_destination(entry)
    pdf_markers = (
        "/plugins/imageformats/qpdf",
        "/plugins/imageformats/libqpdf",
        "/qt6pdf.dll",
        "/libqt6pdf.so",
        "/qt6pdf.framework/",
    )
    return any(marker in destination for marker in pdf_markers)


a = Analysis(
    ["app/main.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["PyQt6.QtPdf", "PyQt6.QtPdfWidgets"],
    noarchive=False,
    optimize=0,
)

# QtGui's dynamic image-plugin discovery collects qpdf and its large PDFium
# dependency chain despite the application having no PDF feature. Filtering is
# deliberately applied after Analysis, where platform-specific binary names
# are known. Every other Qt plugin remains untouched at this stage.
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
