# 1.0.0 kiadási validáció

- Dátum: 2026-10-19
- Release: [Akihabarai Score 1.0.0](https://github.com/MeroDuke/Akihabarai-Score/releases/tag/v1.0.0)
- Annotált tag: `v1.0.0`
- Kiadott commit: `21cd3a173caf8cfc377ceffe666c2f0f8952cc98`
- Előkészítés és kézi átvétel: [PLAN-014](../../plans/completed/release_1_0_0_preparation.md)

## Előfeltételek

A tulajdonos a dokumentációs review-t és a Windows/Linux preview csomagok
kézi átvételét elfogadta, majd külön jóváhagyta a main-integrációt, a dátumozást,
a taget és a GitHub Release-t. A merge utáni teljes helyi regresszió 624
sikeres tesztet adott. Az 1.1.0 elfogadott tracing terve teljesíti a következő
minor release tervezési kapuját.

A dátumozott commit main-CI-je:

- [Windows](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/39218105219) — sikeres.
- [Linux](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/39218107338) — sikeres.

## Tagelt kiadás

- [Windows release-CI](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/39218439945) — sikeres.
- [Linux release-CI](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/39218439946) — sikeres.

Mindkét workflow lefuttatta a teszteket, csomagolást, natív auditot,
forrásarchívum-letöltést és hash-ellenőrzést, Qt jogi anyaggyűjtést,
tag-szintű portable-validációt, startup smoke-ot és natív crash próbát.
A GitHub Release nyilvános, nem draft és nem prerelease. A kiadási leírás a
Windows/Linux indítási tudnivalókat és az ismert Linux feliratvágást is jelzi.

## Publikálás utáni ellenőrzés

Mind az öt release-asset letöltése sikeres. A két bináris csomagot
kicsomagolva a `validate_portable_release.py --tag-build` helyben is elfogadta
a megfelelő platform CI compliance-evidence artifactjával együtt.
Mindkettő tartalmazza a Qt attribution indexet és a szükséges `legal/` anyagokat.
A három upstream forrás SHA-256 értéke megegyezik a tagelt manifesttel.

| Asset | SHA-256 |
| --- | --- |
| `AkihabaraiScore-windows.zip` | `23da6d4576e146b7aee08d62176ee9802f48adcac482a7da6313b4e120d8206a` |
| `AkihabaraiScore-linux-x86_64.tar.gz` | `b483ba5096c19c01f3cee41b70736dc52c987e98a30e496fff88bb17e1377e4d` |
| `pyqt6-6.11.0.tar.gz` | `45dd60aa69976de1918b5ced6b4e7b6a25abd2a919ecef5fd5826ecc76718889` |
| `qtbase-everywhere-src-6.11.1.tar.xz` | `d9594a31228aa23ad6b531719a29b45f0f3989fe6c136d45767ea179f233c1ac` |
| `qtwayland-everywhere-src-6.11.1.tar.xz` | `95788aa502f75441d4edf65932b235f76523084e13dbbb7b9ee2d207b32bd9b3` |

A publikált Windows EXE-ből helyben, `QT_QPA_PLATFORM=offscreen` mellett
indított smoke próba elérte a `Main window ready` határt. A publikált Linux
binárist helyben nem futtattuk Windows alatt; a tagelt Linux CI startup- és
crash-próbája sikeres, a tulajdonosi kézi átvétel pedig a korábbi, azonos
alkalmazáskódú preview csomagra vonatkozik.

Ez a kiadás utáni rekord nem módosítja a `v1.0.0` tag célcommitját.
