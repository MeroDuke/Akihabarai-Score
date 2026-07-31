# Runtime license obligation map

## Purpose

This is the component-level obligation map derived from the `0.23.0` release
artifacts. It separates application-license compatibility from packaging and
notice duties. It is an engineering compliance record, not legal advice.

Status meanings:

- **compatible**: no known blocker for the selected GPL-3.0-only application
  license, provided the listed duties are met;
- **conditional**: usable only after the stated distribution condition is
  implemented and verified;
- **resolved**: an earlier incompatibility or packaging issue has been removed;
- **unresolved**: exact provenance or obligations still need evidence.

## Application and Python stack

| Component | License | Status | Required release treatment |
| --- | --- | --- | --- |
| Akihabarai Score | GPL-3.0-only | compatible | Ship the complete GPLv3 license and corresponding source with releases. |
| PyQt6 6.11.0 community edition | GPL-3.0-only | compatible | Ship the GPLv3 text, notices, and the verified corresponding-source archive with tagged releases. |
| PyQt6-sip 13.11.1 | BSD-2-Clause | compatible | Preserve copyright and license text. |
| CPython 3.11 runtime | PSF license stack | compatible | Ship the applicable Python license text with binary distributions. |
| Requests 2.34.2 | Apache-2.0 | compatible | Ship the Apache-2.0 license and Requests NOTICE. Mark material modifications if made. |
| certifi 2026.7.22 | MPL-2.0 | compatible | Ship the MPL-2.0 text and retain notices for distributed certifi material. Make modified MPL-covered files available in source form if they are changed. |
| charset-normalizer 3.4.9 | MIT | compatible | Preserve copyright and license text. |
| idna 3.18 | BSD-3-Clause | compatible | Preserve copyright, conditions, disclaimer, and avoid endorsement implications. |
| urllib3 2.7.0 | MIT | compatible | Preserve copyright and license text. |
| OpenSSL 3 | Apache-2.0 | compatible | Ship the Apache-2.0 text and applicable OpenSSL notices. |

## Qt framework

| Component | License path | Status | Required release treatment |
| --- | --- | --- | --- |
| Qt 6.11.1 runtime modules | LGPL-3.0 or applicable alternative | conditional | Ship LGPL text and notices, identify Qt use, provide corresponding Qt source offer/access, and preserve the user's ability to replace or relink the LGPL libraries. |
| Qt third-party code | component-specific | conditional | Derive notices and source duties from the exact shipped Qt module/plugin set and Qt SBOM. Do not claim that one Qt license covers every embedded third-party component. |
| Qt PDF/PDFium chain | mixed third-party licenses | resolved | Removed from the package because the application has no PDF feature; packaging tests prevent its return. |

The retired blanket reverse-engineering prohibition could not coexist with the
LGPL rights needed to debug modifications to or replace the Qt libraries. A
future trademark policy may still protect the official name and visual brand;
that is separate from copyright licensing.

The current PyInstaller `--onefile` layout extracts Qt libraries at runtime.
Before release it must be demonstrated that an end user can practically
replace/relink the LGPL-covered Qt components, or the Qt-based distribution
must use a layout that makes this possible.

## Platform runtimes

| Component family | Platform | Status | Required release treatment |
| --- | --- | --- | --- |
| Microsoft Visual C++ runtime/UCRT | Windows | unresolved | Record exact redistributed files and the Microsoft redistribution basis. Do not describe these files as open-source components. |
| Linux distribution libraries | Linux | resolved | They are installed from the documented Ubuntu 24.04 runtime package set and excluded from the portable payload; CI rejects accidental rebundling. |
| Qt platform and image plugins | Windows/Linux | conditional | Keep only the formats and platform backends supported by the product; test every exclusion in a packaged application. Include notices for everything that remains. |

Linux releases now rely on the supported distribution for `/lib` and
`/usr/lib` system libraries. They are runtime prerequisites rather than copied
release contents. The release audit enforces this boundary; only actually
bundled components belong in the portable package's third-party inventory.

## Services and tools that are not bundled runtime libraries

| Item | Relationship | Release treatment |
| --- | --- | --- |
| AniList GraphQL API | external runtime service | Document service use and data lifecycle. Re-review the API terms before hosted aggregation, database ingestion, competing tracker functionality, or material monetization. |
| PyInstaller 6.21.0 | build tool plus embedded bootloader | Record build provenance. Its bootloader exception does not determine the application license; bundled dependency licenses still apply. |
| GitHub Actions and action implementations | hosted build tooling | Record workflow provenance, but do not list them as bundled application libraries unless artifact inspection proves otherwise. |
| pytest, pytest-qt and pytest-html | test tooling | Keep in build/test provenance, not the end-user runtime notice list. |

## Selected application-license route

Akihabarai Score uses GPL-3.0-only and retains the GPL community edition of
PyQt6. The former custom license and its incompatible restrictions have been
retired. Brand protection and creator attribution expectations will be handled
separately after the technical release-compliance work is complete.
