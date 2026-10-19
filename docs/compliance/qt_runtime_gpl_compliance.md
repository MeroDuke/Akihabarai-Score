# Qt/PyQt runtime GPLv3 compliance

## Scope and selected route

Akihabarai Score distributes its desktop application as a PyInstaller
`onefile` executable under `GPL-3.0-only`. The locked UI runtime is:

| Component | Version | Distributed license evidence |
|---|---:|---|
| Akihabarai Score | 1.0.0 release line | `GPL-3.0-only` |
| PyQt6 | 6.11.0 | `GPL-3.0-only` package metadata and license |
| PyQt6-Qt6 | 6.11.1 | LGPLv3 package license |
| PyQt6-sip | 13.11.1 | BSD-2-Clause |

The release lock therefore combines PyQt6 6.11.0 with PyQt6-Qt6 6.11.1 and
PyQt6-sip 13.11.1.

LGPLv3 consists of GPLv3 plus additional permissions. The GNU license
compatibility guidance permits LGPLv3 code to be combined with and conveyed as
part of a GPLv3 work. Akihabarai Score therefore distributes the combined
application under GPLv3 and does not rely on a proprietary application or an
LGPL-only application exception.

Primary references:

- <https://www.gnu.org/licenses/license-compatibility.html>
- <https://www.gnu.org/licenses/gpl-faq.html>
- <https://www.gnu.org/licenses/lgpl-3.0.html>
- <https://www.riverbankcomputing.com/software/pyqt/>
- <https://www.qt.io/development/open-source-lgpl-obligations>

This is an engineering compliance record, not independent legal advice.

## Onefile packaging boundary

PyInstaller embeds CPython, PyQt6, Qt and the required plugins in the executable
and extracts them to a temporary runtime directory when the process starts.
The packaging form does not change the GPLv3 rights granted to recipients.

The release does not impose DRM, signature enforcement, activation, account
linkage or another technical restriction on modified builds. A recipient may
obtain, modify, rebuild and run the application and its covered runtime from
the corresponding sources. The project keeps `AkihabaraiScore.spec`, release
dependency locks, build workflows and packaging scripts in the tagged source.

## Corresponding-source chain

`compliance/source-archives.json` pins the exact source archives and SHA-256
digests for PyQt6 6.11.0, Qt Base 6.11.1 and Qt Wayland 6.11.1. Tag workflows:

1. download every pinned archive;
2. verify its digest;
3. extract license, copyright, NOTICE, REUSE and Qt attribution material;
4. place the applicable legal material in the portable package; and
5. publish the verified source archives beside the binary GitHub Release.

The tagged repository revision is the corresponding Akihabarai Score source.
Its `requirements-release.txt`, `requirements-build.txt`, PyInstaller spec,
workflows and scripts describe the preferred form and build process used for
the executable.

## Third-party material

Conveying the combined work under GPLv3 does not erase copyright or notice
requirements for separately licensed material. The portable package retains:

- the complete GPLv3 application license;
- `THIRD_PARTY_NOTICES.md`;
- collected Python runtime and dependency license/NOTICE files;
- Qt and embedded third-party attribution material on tagged releases; and
- a source-availability explanation identifying the exact release sources.

Internal SBOM, native inventory, asset provenance and platform provenance are
build evidence. CI continues to generate or validate them, but they are not
part of the end-user program directory.

## Verification boundary

CI must fail if:

- the application license is no longer `GPL-3.0-only`;
- release dependency versions diverge from the compliance inventory;
- the source archive manifest is missing or invalid;
- a required license or notice is missing from the portable package;
- tag-only Qt attribution material is absent;
- excluded Qt modules or unsupported native payloads return; or
- the packaged executable does not reach the main-window-ready smoke boundary.

Any Qt/PyQt version, binding, packaging model or application-license change
requires a new review of this document, the source manifest and the generated
artifact inventories.
