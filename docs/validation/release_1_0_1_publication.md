# 1.0.1 publikálási rekord

Dátum: **2026-11-01**.
[Publikált stabil release](https://github.com/MeroDuke/Akihabarai-Score/releases/tag/v1.0.1).

A tulajdonos engedélyezte a main-merge-et és push-t, majd zöld main-CI után
a taget és a kiadást. A main-merge és az annotált `v1.0.1` tag forráscommitja:
`83bea0a61eaf95e4fc5afe1a10041500863bf228`. A későbbi dokumentációs lezárás
nem módosítja a taget vagy a kiadott alkalmazáskódot.

## Ellenőrzések

- Main utáni helyi offscreen regresszió: **657 passed**.
- Main-CI: [Windows](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41329228157),
  [Linux](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41329228185).
- Éles metrikák: [main-trigger](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41329228172)
  és [kézi ismétlés](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41329334528).
  Az azonos napi ismétlés idempotens; az első jövőbeli cron-eseményt nem állítjuk megtörténtnek.
- Tag-CI: [Windows](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41329513435),
  [Linux](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41329513414).
  Mindkettő sikeres, a csomagolt startup-, natív crash- és compliance-kapukkal.
- Windows tag-build három kötelező indulása: **3,032 / 2,625 / 2,937 s**,
  változatlan 15 s limittel, retry nélkül.
- Mindkét publikált alkalmazáscsomag visszatöltve és a
  `scripts/validate_portable_release.py` tag-build validátorral ellenőrizve,
  a megfelelő CI compliance-evidence alapján. Ez nem új helyi GUI-kézi átvétel;
  az indítási bizonyítékot a platform-CI adja.
- A három publikált PyQt/Qt forrásarchívum SHA-256 értéke egyezik a
  `compliance/source-archives.json` nyilvántartással.

## Publikált alkalmazáscsomagok SHA-256 értékei

| Csomag | SHA-256 |
| --- | --- |
| `AkihabaraiScore-windows.zip` | `6609d52ce76f5b8b99f8e7c9bec7612b50cf7fb041473e17172c32df932a2615` |
| `AkihabaraiScore-linux-x86_64.tar.gz` | `adc2f2cf46c848d4062fa4bcf3f288365b010362897135ac3aa2ed89cdfcd82d` |

A helyi validáció anyagai a figyelmen kívül hagyott
`build/published-v1.0.1/` alatt találhatók. Saját és automatizált ellenőrző
letöltések is növelhetik a GitHub számlálóját; ez nem felhasználószám.
