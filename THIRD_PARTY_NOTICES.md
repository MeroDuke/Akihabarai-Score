# Third-Party Notices

Akihabarai Score includes or uses the components and services listed below.
The portable release package includes the available full license and NOTICE
texts under `licenses/`, together with its generated Python dependency SBOM.
Exact upstream source archives for confirmed copyleft runtime components are
recorded in `source-archives.json` and explained in `SOURCE_AVAILABILITY.md`.

## Bundled application runtime

| Component | Purpose | License |
| --- | --- | --- |
| CPython | Application runtime and standard library | Python Software Foundation license stack |
| PyQt6 | Python bindings for the desktop UI | GPL-3.0-only for the community edition |
| Qt 6 | Native desktop UI framework used by PyQt6 | LGPL-3.0; bundled third-party components retain their own terms |
| PyQt6-sip | PyQt support runtime | BSD-2-Clause |
| Requests | HTTP client | Apache-2.0 |
| certifi | Certificate authority bundle | MPL-2.0 |
| charset-normalizer | HTTP response character-set handling | MIT |
| idna | Internationalized domain-name handling | BSD-3-Clause |
| urllib3 | HTTP transport used by Requests | MIT |
| OpenSSL | Cryptographic and TLS runtime used by bundled components | Apache-2.0 |

Each release contains a machine-readable native payload inventory. Linux
operating-system libraries are installed from the documented Ubuntu runtime
packages and are not copied into the portable payload. Windows 10+ UCRT and
API-set system files are likewise excluded. The Windows package retains only
the allow-listed Microsoft C++ runtime files supplied with the locked CPython
and PyQt6-Qt6 distributions while their redistribution basis is tracked in the
release compliance record.

Tagged Linux packages additionally contain the license, copyright, NOTICE,
REUSE, and attribution material extracted from the verified Qt Base and Qt
Wayland source archives. `licenses/qt-source/qt-attributions.json` indexes the
conservative upstream source-module attribution set and does not claim that
every optional record was compiled into the binary wheels.

## AniList

The application uses the external AniList GraphQL API and cover-image service
at runtime for user-driven anime title search, metadata lookup, and cover
retrieval. AniList software and databases are not bundled with Akihabarai
Score. Use of that service is governed by the AniList API Terms of Use:
https://docs.anilist.co/guide/terms-of-use

The application's AniList data lifecycle is documented in
`docs/anilist_data_lifecycle.md`.

## Build and test tooling

PyInstaller is used to produce the executable. Its bootloader exception allows
the generated application to use the application's selected license while all
bundled dependency licenses continue to apply.

GitHub Actions, pytest, pytest-qt, and pytest-html are build/test tools and are
not represented as bundled runtime libraries unless a platform artifact audit
identifies their code inside a release.
