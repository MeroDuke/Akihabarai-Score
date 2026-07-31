# Runtime license obligation map

## Purpose

This is the component-level obligation map derived from the `0.23.0` release
artifacts. It separates application-license compatibility from packaging and
notice duties. It is an engineering compliance record, not legal advice.

Status meanings:

- **compatible**: no known blocker for the intended permissive application
  licensing direction, provided the listed duties are met;
- **conditional**: usable only after the stated distribution condition is
  implemented and verified;
- **conflict**: incompatible with the current Akihabarai Score License 1.0;
- **unresolved**: exact provenance or obligations still need evidence.

## Application and Python stack

| Component | License | Status | Required release treatment |
| --- | --- | --- | --- |
| Akihabarai Score 0.23.0 | custom | conflict | Retire the no-modification, non-commercial and reverse-engineering restrictions before 1.0.0. |
| PyQt6 6.11.0 community edition | GPL-3.0-only | conflict | Use a GPL-compatible application license, buy an appropriate commercial PyQt license, or migrate bindings. Merely adding a notice does not resolve this. |
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
| Qt PDF/PDFium chain | mixed third-party licenses | candidate for removal | No application PDF feature exists. Exclude the plugin/module if packaged regression tests remain green. Until then, include its complete notice set. |

The current blanket reverse-engineering prohibition cannot coexist with the
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
| Linux system libraries collected into the executable | Linux | unresolved | Map every shipped library to its source package, version and license. Provide corresponding source/access where LGPL or GPL requires it. Prefer not bundling host libraries that are not needed. |
| Qt platform and image plugins | Windows/Linux | conditional | Keep only the formats and platform backends supported by the product; test every exclusion in a packaged application. Include notices for everything that remains. |

## Services and tools that are not bundled runtime libraries

| Item | Relationship | Release treatment |
| --- | --- | --- |
| AniList GraphQL API | external runtime service | Document service use and data lifecycle. Re-review the API terms before hosted aggregation, database ingestion, competing tracker functionality, or material monetization. |
| PyInstaller 6.21.0 | build tool plus embedded bootloader | Record build provenance. Its bootloader exception does not determine the application license; bundled dependency licenses still apply. |
| GitHub Actions and action implementations | hosted build tooling | Record workflow provenance, but do not list them as bundled application libraries unless artifact inspection proves otherwise. |
| pytest, pytest-qt and pytest-html | test tooling | Keep in build/test provenance, not the end-user runtime notice list. |

## Decision gates

The engineering work can continue without choosing the final application
license. A user decision is required only when choosing between these binding
strategies:

1. release Akihabarai Score under a GPLv3-compatible license and retain the
   community PyQt6 dependency;
2. keep a GPL-incompatible application license and purchase a suitable
   commercial PyQt license;
3. migrate from PyQt6 to another binding and evaluate that binding's license
   and migration cost.

No final `LICENSE` replacement is made before that decision.
