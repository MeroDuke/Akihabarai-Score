# License and distribution compliance audit

## Status

This document records the bottom-up compliance audit for the Akihabarai Score
`0.24.0` stabilization cycle. The audit starts from the files that were
actually distributed in release `0.23.0`, not only from the dependencies
declared by the source project.

The audit is intentionally evidence-driven. Every finding is classified as:

- **Confirmed**: verified in a released artifact, package metadata, source
  import, or authoritative upstream documentation.
- **Candidate**: likely unused or replaceable, but removal still requires a
  dedicated packaged-app build and regression test.
- **Unresolved**: provenance, exact license obligations, or runtime necessity
  still needs to be established.

This document is not legal advice. Final license selection and release
compliance should be reviewed against the complete license texts and, where
appropriate, by qualified legal counsel or the relevant vendor.

## Audit baseline

The audited release is `v0.23.0`, commit
`140fabfe6437cae9e1a1a852c618b0109636ee76`, published on 2026-07-31.

Release artifacts:

| Platform | Artifact | SHA-256 |
| --- | --- | --- |
| Windows | `AkihabaraiScore-windows.zip` | `a54a00b2280929ebae19c294205f4a1e85bc79f5d44fc6248cc29d9054917ca7` |
| Linux | `AkihabaraiScore-linux-x86_64.tar.gz` | `f27f39e5a016d038d75450e03dd3b367accf09c477080778557cb7abf9574a10` |

Both artifacts were downloaded from the public GitHub release and inspected
with PyInstaller's archive viewer.

## Distributed project-owned files

Both artifacts contain:

- the PyInstaller one-file executable;
- `assets/icon.ico`;
- `config/app.json`;
- `config/profiles.json`;
- `config/ui.json`;
- `config/locales/hu.json`;
- `config/locales/en.json`.

The application code, configuration, profile definitions, and localization
catalogs are project-owned unless a later provenance review finds copied or
contributed material with separate terms.

### Asset provenance

`assets/icon.ico` is tracked as the current Akihabarai Konyvespolc channel
logo. Ownership or an appropriate redistribution grant must be explicitly
recorded before `1.0.0`.

## External runtime service

### AniList

AniList code and an AniList database are not bundled. The application accesses
the AniList GraphQL API and cover-image URLs at runtime for:

- title search;
- title metadata;
- AniList IDs;
- cover image retrieval.

The service relationship is governed by AniList's API Terms of Use rather than
a bundled software license. The current desktop integration is user-driven and
does not bulk synchronize or maintain an application-readable cache.
Diagnostic logs may contain AniList-derived runtime values for up to 14 days,
as documented in `docs/anilist_data_lifecycle.md`.

The future hosted platform, database ingestion, aggregation, and monetization
plans require a new AniList terms review before implementation.

## Exact Python dependency resolution in `0.23.0`

The Windows and Linux tag builds resolved the same Python packages:

| Package | Version | Relationship | Declared license |
| --- | ---: | --- | --- |
| PyQt6 | 6.11.0 | direct | GPL-3.0-only or separately purchased commercial license |
| PyQt6-Qt6 | 6.11.1 | PyQt6 dependency | LGPL-3.0 / GPL option, subject to Qt component terms |
| PyQt6-sip | 13.11.1 | PyQt6 dependency | BSD-2-Clause |
| requests | 2.34.2 | direct | Apache-2.0 |
| certifi | 2026.7.22 | Requests dependency | MPL-2.0 |
| charset-normalizer | 3.4.9 | Requests dependency | MIT |
| idna | 3.18 | Requests dependency | BSD-3-Clause |
| urllib3 | 2.7.0 | Requests dependency | MIT |

The versions above are confirmed by the successful `v0.23.0` CI installation
logs and by metadata from the exact wheel releases.

The project currently declares only lower bounds, so rebuilding the same
source revision at a later date can resolve a different dependency set. A
release lock or constraints mechanism is required for reproducibility.

Release CI now installs the runtime dependency graph from
`requirements-release.txt` and the test/build toolchain from
`requirements-build.txt`. It uses an explicit Python patch version and
validates installed runtime versions before packaging. The validation also
emits a CycloneDX 1.6 Python SBOM as a CI artifact. Native and Qt component
SBOM coverage is still separate open work.

The confirmed baseline is also stored in the machine-readable
`compliance/runtime-components.json` inventory. Its schema and mandatory
entries are covered by an automated test. This file is an audit input, not yet
the final release SBOM.

## Confirmed embedded Python runtime

The Windows executable contains Python 3.11 DLLs, the standard library
archive, native extension modules, and the application modules.

The Linux executable contains `libpython3.11.so.1.0`, standard library modules,
and native extension modules.

Redistribution therefore requires the Python Software Foundation license and
the applicable Python license stack. Referring to Python only by name in
`THIRD_PARTY_NOTICES.md` is not sufficient for an offline binary package.

## Confirmed application imports

Production source imports only these PyQt module families:

- `PyQt6.QtCore`;
- `PyQt6.QtGui`;
- `PyQt6.QtWidgets`;
- `PyQt6.sip`.

No production source import was found for:

- Qt PDF;
- Qt DBus;
- Qt OpenGL;
- Qt SVG APIs;
- Qt Network APIs;
- Qt Wayland APIs.

Absence of a direct import is not by itself proof that a Qt plugin is unused.
Qt image, platform, style, and icon plugins can be loaded dynamically.

Production source uses Requests for:

- AniList GraphQL POST requests;
- cover-image GET requests;
- timeout and network exception handling.

Requests is therefore a confirmed functional dependency in the current
implementation.

## Confirmed Qt payload

### Windows

The executable contains at least:

- Qt Core, GUI, Widgets, Network, PDF, and SVG libraries;
- Windows, minimal, and offscreen platform plugins;
- GIF, ICNS, ICO, JPEG, PDF, SVG, TGA, TIFF, WBMP, and WebP image plugins;
- Qt translation catalogs;
- software OpenGL support;
- Microsoft Visual C++ runtime libraries.

### Linux

The executable contains at least:

- Qt Core, GUI, Widgets, Network, PDF, SVG, DBus, OpenGL, Wayland Client,
  XCB QPA, and EGLFS integration libraries;
- XCB, Wayland, EGLFS, Linux framebuffer, VNC, minimal, and offscreen platform
  plugins;
- GTK and desktop portal platform themes;
- GIF, ICNS, ICO, JPEG, PDF, SVG, TGA, TIFF, WBMP, and WebP image plugins;
- Qt translation catalogs.

Qt PDF is shipped even though no application PDF API use was found. It also
brings PDFium, Chromium-derived code, ICU, FreeType, image codecs, and other
third-party components into the compliance scope. Qt PDF is therefore the
first high-value exclusion candidate, subject to packaged-app regression
testing.

`AkihabaraiScore.spec` now excludes the unused Qt PDF Python modules, PDF image
plugin, and Qt PDF shared library while retaining every other previously
collected Qt plugin. The exclusion remains conditional until Windows and Linux
packaged startup and functional regression checks pass in CI.

The source, assets, and supported workflows require JPEG AniList covers, the
ICO application icon, and PNG exports. WebP and GIF decoding are retained as
low-cost compatibility formats. ICNS, SVG, TGA, TIFF, and WBMP have no product
use and are excluded on both platforms; removing the SVG plugin also removes
the otherwise unused Qt SVG native module. The final-package audit requires
ICO, JPEG, and WebP plugins and rejects every excluded format.

CI inventories then showed 206 packaged entries on Windows and 316 on Linux.
More than one hundred entries were Qt translation catalogs outside the
application's Hungarian/English language contract. Release builds now keep
only `qt` and `qtbase` Hungarian/English catalogs. Windows retains its native
and offscreen platforms; Linux retains XCB, Wayland, and offscreen platforms.
Embedded/server backends (EGLFS, Linux framebuffer, VNC, Vulkan KHR display,
and minimal variants), generic raw-input plugins, and the unused SVG icon
engine are excluded. Desktop themes, input contexts, and XCB/Wayland graphics
integrations remain pending deeper functional testing.

Both platform builds now preserve the distinction between PyInstaller's input
analysis and its final package TOC. The analysis records that the generic Qt
hooks discovered the PDF chain; `PKG-00.toc` records that the explicit spec
excluded it from the executable. The build audits the final package TOC, fails
if Qt PDF or its image plugin is present, fails if Qt Core, GUI, or Widgets is
missing, and emits the complete packaged binary/data inventory as
`release-native-inventory.json`. The inventory is uploaded for audit and
included in release packages.

PyInstaller analysis confirms that these native Qt libraries are collected
through dynamically loaded Qt plugins and their binary dependencies, rather
than application imports. The PDF image plugin pulls in Qt PDF, the SVG image
plugin pulls in Qt SVG, and the broad Linux platform-plugin set expands into
multiple display-system and desktop-integration stacks. The safe reduction
point is therefore an explicit PyInstaller specification with an allow-listed
plugin set, followed by packaged functional tests. Removing imports from the
application core would not solve this packaging issue.

## Confirmed cryptographic and certificate payload

Both artifacts include OpenSSL 3 `libcrypto` and `libssl` binaries. OpenSSL 3
is Apache-2.0 licensed and requires the applicable license and notice handling.

Both artifacts include certifi's `cacert.pem`. Its MPL-2.0 obligations apply to
the distributed certifi material without automatically changing the license
of unrelated project files.

## Linux native-library payload

The Linux one-file executable also bundles a broad host-runtime set, including
families such as:

- GTK, GLib, GObject, GIO, ATK, and accessibility libraries;
- Cairo, Pango, Fontconfig, FreeType, HarfBuzz, Graphite, and Pixman;
- ICU, JPEG, PNG, Brotli, zlib, zstd, bzip2, and lzma;
- OpenSSL, libffi, readline, D-Bus, systemd, and SELinux;
- Kerberos and GSSAPI libraries;
- X11, XCB, XKB, Wayland, and related platform libraries.

These libraries have mixed licenses and some may be host libraries collected
by PyInstaller rather than dependencies that should be redistributed by the
application. Exact source package, version, copyright, license, and necessity
remain **unresolved** for this group.

The Linux build must produce a machine-readable native dependency inventory
and retain package provenance before `1.0.0`.

Linux CI now maps every packaged system library under `/lib` or `/usr/lib` to
its owning dpkg binary package, installed version, source package, and source
version. It copies each package's Debian/Ubuntu copyright file into the release
legal directory and emits `release-linux-packages.json`. An unmapped library,
missing package metadata, or missing copyright file fails the build instead of
silently producing an incomplete compliance package.

The first complete CI mapping covers 89 packaged system-library files owned by
82 binary packages. All 82 packages have a recorded installed version, source
package and source version, and all 82 Debian/Ubuntu copyright files were
collected. No unknown-origin Linux system library remains in that build.

The product owner selected a distribution-provided system-library model for
future Linux releases. PyInstaller now excludes binaries originating under
`/lib` and `/usr/lib`; CPython, PyQt6, and Qt wheel libraries remain bundled
from the pinned Python environment. Ubuntu 24.04 x86_64 is the validated
baseline, with its runtime packages defined in
`packaging/linux/ubuntu-24.04-runtime-packages.txt`. The final-package audit
fails if a system library is bundled again, and CI installs the declared list
before packaged startup testing. The previous 82-package legal mapping remains
historical evidence for the retired self-contained Linux layout.

## Build tooling

The `0.23.0` release used PyInstaller 6.21.0. PyInstaller's bootloader exception
allows generated executable bundles to use the application's chosen license,
provided the licenses of the bundled dependencies are respected. PyInstaller
does not itself force Akihabarai Score to use the GPL.

GitHub Actions, pytest, pytest-qt, pytest-html, and similar CI-only tools are
not end-user runtime dependencies unless later artifact inspection proves that
their code was bundled. They belong in build provenance, not in the primary
end-user third-party notice list.

The Linux artifact currently contains some setuptools and packaging runtime
material. The import path that caused these build-time packages to enter the
executable remains **unresolved**.

The `0.23.0` Linux archive also accidentally contains the log written by the
startup smoke test. Release packaging now removes smoke-test logs after they
have been uploaded as diagnostics and before the portable archive is created.

## Current release-package compliance gaps

The Windows and Linux portable packages do not contain:

- the current Akihabarai Score `LICENSE` file;
- `THIRD_PARTY_NOTICES.md`;
- GPL-3.0 and LGPL-3.0 texts required by the current Qt/PyQt path;
- the Python license stack;
- Requests' Apache-2.0 license and NOTICE;
- the licenses of Requests' transitive dependencies;
- OpenSSL's license;
- Qt's module and third-party notices;
- native Windows/Linux runtime notices;
- a software bill of materials.

The current project license itself requires its text to accompany
redistributions, so the binary packages do not even meet the project's own
stated redistribution packaging rule.

Release assembly now includes the application license, the rewritten
third-party notice, the generated Python SBOM, and license/NOTICE files
collected from every locked Python runtime distribution plus the CPython
runtime license. Qt third-party, OpenSSL binary provenance, and platform-native
license coverage remain open and prevent this from being considered the final
compliance package.

The exact official PyQt6 6.11.0, Qt Base 6.11.1, and Qt Wayland 6.11.1 source
archive URLs and SHA-256 values are now pinned in
`compliance/source-archives.json` and included in portable releases. This is a
reproducible source-identity record, not yet a claim that linking to upstream
alone satisfies every GPL/LGPL corresponding-source delivery requirement.

After selecting GPL-3.0-only, tag builds now download those pinned source
archives, verify every SHA-256, and attach the verified archives alongside the
binary release. Normal branch CI validates the manifest without downloading
the large sources. This creates a same-release corresponding-source delivery
path for the bundled PyQt and Qt modules.

## Compatibility findings so far

### No application-license blocker identified

Subject to notice and source-availability requirements, no fundamental
application-license conflict has yet been identified for:

- Python;
- Requests;
- certifi;
- charset-normalizer;
- idna;
- urllib3;
- PyQt6-sip;
- OpenSSL 3;
- PyInstaller's generated bootloader bundle.

### Conditional compatibility

Qt under LGPL-3.0 can be used by an application under another license only if
all LGPL conditions are met. The release design must preserve the user's
rights to inspect, replace, modify, and re-link the LGPL-covered Qt libraries.
The existing blanket reverse-engineering prohibition conflicts with those
rights and cannot remain in that form.

The PyInstaller one-file format requires specific review because Qt libraries
are extracted and loaded at runtime instead of being shipped as plainly
replaceable files beside the executable.

### Confirmed conflict

The GPL-3.0-only PyQt6 community build is not compatible with the current
Akihabarai Score license, which prohibits modification and commercial use.
The conflict can be resolved only through a compatible application license,
an appropriate commercial PyQt license, or migration away from the GPL PyQt6
binding.

The goals and viable resolution routes are reviewed in
`docs/application_license_decision.md`. GPL-3.0-only was selected for the
application. The former custom license has been replaced by the complete GPLv3
text, project metadata uses the `GPL-3.0-only` SPDX identifier, and automated
tests prevent the retired non-commercial and no-modification restrictions from
returning.

## Component review rule

For every unidentified or unacceptable component:

1. establish its exact origin and license;
2. identify why the build collected it;
3. map it to the application function that needs it;
4. decide whether the function is part of the supported product;
5. if it is unnecessary, exclude the component and run full packaged-app
   regression checks;
6. if it is necessary, first search for an alternative already present in the
   accepted dependency set or Python standard library;
7. introduce a new dependency or remove a user-facing function only after a
   separate compatibility, maintenance, and product decision.

No component is removed merely because its purpose is not immediately known.

## Open work

- Record ownership or license provenance for `assets/icon.ico`.
- Generate exact Python dependency locks for release builds.
- Generate Python dependency SBOM and license material.
- Obtain and filter the Qt 6.11.1 SBOM for the modules actually shipped.
- Determine whether Qt PDF and its image plugin can be excluded.
- Determine which image plugins are required by AniList covers and exports.
- Trace why Qt Network and SVG are collected despite no direct application
  import.
- Trace setuptools and packaging material in the Linux executable.
- Map every bundled Linux shared library to its source package and license.
- Record Microsoft runtime redistribution provenance for the Windows build.
- Select the final application license only after the inventory is complete.
- Review each goal of the retired custom license against the selected license.
- Define a separate attribution and brand/trademark policy where permitted.
- Add release-package compliance tests and packaged functional smoke tests.
