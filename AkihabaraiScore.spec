# -*- mode: python ; coding: utf-8 -*-
"""Cross-platform PyInstaller recipe with audited runtime exclusions."""

from pathlib import Path, PurePosixPath
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
    if any(marker in destination for marker in excluded_markers):
        return True

    if "/translations/" in destination:
        translation = destination.rsplit("/", 1)[-1]
        return translation not in {"qt_en.qm", "qt_hu.qm", "qtbase_en.qm", "qtbase_hu.qm"}

    common_unused_plugins = (
        "/plugins/generic/",
        "/plugins/iconengines/qsvgicon",
        "/plugins/iconengines/libqsvgicon",
    )
    if any(marker in destination for marker in common_unused_plugins):
        return True

    if sys.platform == "win32":
        basename = destination.rsplit("/", 1)[-1]
        windows_icu_runtime = (
            basename in {"icu.dll", "icuin.dll", "icuuc.dll"}
            or (basename.startswith("icudt") and basename.endswith(".dll"))
        )
        windows_system_runtime = basename == "ucrtbase.dll" or basename.startswith(
            ("api-ms-win-core-", "api-ms-win-crt-")
        )
        return (
            windows_icu_runtime
            or windows_system_runtime
            or "/plugins/platforms/qminimal" in destination
        )

    if sys.platform.startswith("linux"):
        linux_unused_plugins = (
            "/plugins/egldeviceintegrations/",
            "/plugins/platforms/libqeglfs",
            "/plugins/platforms/libqlinuxfb",
            "/plugins/platforms/libqminimal",
            "/plugins/platforms/libqminimalegl",
            "/plugins/platforms/libqvkkhrdisplay",
            "/plugins/platforms/libqvnc",
        )
        return any(marker in destination for marker in linux_unused_plugins)

    return False


build_info_path = Path("build-metadata/build-info.json")
build_info_datas = [(str(build_info_path), ".")] if build_info_path.is_file() else []


a = Analysis(
    ["app/launcher.py"],
    pathex=[],
    binaries=[],
    datas=build_info_datas,
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
# Only Hungarian and English Qt catalogs are retained. Platform plugins are
# limited to native Windows, X11/Wayland Linux, and offscreen test execution.
a.binaries = type(a.binaries)(entry for entry in a.binaries if not is_excluded_binary(entry))
a.datas = type(a.datas)(entry for entry in a.datas if not is_excluded_binary(entry))

# Windows 10 and later provide ICU, UCRT, and API-set forwarders as operating
# system components. Excluding ICU also prevents unrelated tools on the build
# PATH from contaminating the package with an incompatible third-party copy.
# Linux releases similarly rely on the supported distribution for libraries
# under /lib and /usr/lib. Python, PyQt, and Qt wheel libraries remain bundled.
if sys.platform.startswith("linux"):
    a.exclude_system_libraries()

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
