# 1.0.1 release-előkészítési validáció

Dátum és kiválasztott kiadási dátum: **2026-11-01**. Ez előkészítési rekord,
nem publikálási bizonyíték. A dátumot csúszás esetén a tulajdonossal újra
egyeztetjük; dátumozott changelog önmagában nem jelent kiadást.

## Scope és integráció

- [PLAN-018: eredménypanel layout](../../plans/completed/result_table_layout_fix.md).
- [PLAN-017: GitHub-letöltések és jelvények](../../plans/active/release_download_metrics.md).
- [PLAN-021: Windows startup-gyorsítás](../../plans/completed/startup_performance.md).
- Integrációs ág: `release/1.0.1`. A startup-fix merge-je: `ee8c044`, a zöld
  `773ffc8` fix-ág alapján. A korábbi layout és metrika feature már az ág része.
- A tulajdonos a layoutot, a statisztikai oldal elhelyezését és a gyorsított
  ikonmegoldást elfogadta; az első három kiadás-előkészítési lépést jóváhagyta.
  Ez nem main-merge, tagelési vagy GitHub Release-engedély.

## Átvételi alap és korlátok

A layout kézzel végignyomogatott állapota elfogadott. Az ismételt végleges
csomag kézi átvételét a tulajdonos dokumentáltan elengedte; nem állítunk friss
fizikai DPI-/többmonitoros kézi próbát. HU/EN, ablakméret, három betűméret,
vágólapmásolás, ikonpaletta/DPR és módváltás automata regresszióval védett.

A startup-fix előzetes Windows csomagolt próbái 2,328 / 2,016 / 2,015 s,
változatlan 15 s limittel, retry nélkül. A readiness csak a `show()` után jön.
A onefile formátum és a natív crash-supervisor megmaradt; új függőség nem került be.

## Release-ág ellenőrzési kapui

- [x] A jóváhagyott scope minden implementációja integrálva.
- [x] A rajzolt ikonok tulajdonosi elfogadása rögzítve.
- [x] Alkalmazás- és csomagverzió: `1.0.1`, changelog: `2026-11-01`.
- [x] Teljes integrált helyi offscreen regresszió.
- [x] Verzió/tag konzisztencia-validáció (tag létrehozása nélkül).
- [x] Helyi Markdown-linkek és diff-ellenőrzés.
- [ ] Release-ág Windows- és Linux-CI, startup- és natív crash-próbákkal.
- [ ] A metrika-workflow release-ágon offline tesztel, éles gyűjtés nélkül.

A konkrét eredmények és futásazonosítók az alábbi naplóba kerülnek. Csak zöld
release-validáció után kérhető main-integrációs jóváhagyás.

## Külön jóváhagyásra váró további lépések

1. Main-merge és push a legfrissebb `origin/main` alapján, post-merge
   regresszióval és tiszta munkakönyvtárral.
2. Main-CI és az éles metrika-workflow ellenőrzése: jogosultság, adatágra írás,
   azonos napi idempotencia. A kézi bootstrap már létezik, ezért a dátumozott
   jelvények élnek, de ez önmagában nem bizonyítja az automata ütemezést.
3. Külön kiadási jóváhagyás után `v1.0.1` tag, GitHub Release és a publikált
   Windows/Linux csomagok, jogi/forrásanyagok és letöltési hivatkozások ellenőrzése.

Az 1.1.0 elfogadott környezetfrissítési terve megmaradt. A következő minor
release tervezési kapuja így is teljesül, bár ez a patch kiadásnál nem kötelező.

## Ellenőrzési napló

- Az `ee8c044` integrációs állapoton `QT_QPA_PLATFORM=offscreen; python -m pytest -q`:
  **657 passed in 39.75s**.
- `python scripts/validate_release_version.py --tag v1.0.1`: sikeres, tag nem készült.
- Helyi Markdown-célok és `git diff --check`: hibamentes. A lezárt layout-terv
  átköltözött a `plans/completed/` alá, hivatkozásai frissítve.
- A legfrissebb `origin/main` a release előzménye. Függőséglock és PyInstaller
  spec az 1.0.0 baseline-hoz képest változatlan; új runtime-függőség nincs.
- A release-ág kombinált platform-CI-jét a push indítja; eredménye alább rögzítendő.
