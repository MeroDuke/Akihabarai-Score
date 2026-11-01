# 1.0.1 release-előkészítési validáció

Történeti előkészítési rekord. A main-integráció és publikálás azóta elkészült;
a végleges bizonyítékot a [publikálási rekord](release_1_0_1_publication.md)
tartalmazza. Az alábbi korábbi engedélyezési kapuk az előkészítés állapotát őrzik.

Dátum és kiválasztott kiadási dátum: **2026-11-01**. Ez előkészítési rekord,
nem publikálási bizonyíték. A dátumot csúszás esetén a tulajdonossal újra
egyeztetjük; dátumozott changelog önmagában nem jelent kiadást.

## Scope és integráció

- [PLAN-018: eredménypanel layout](../../plans/completed/result_table_layout_fix.md).
- [PLAN-017: GitHub-letöltések és jelvények](../../plans/completed/release_download_metrics.md).
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
- [x] Release-ág Windows- és Linux-CI, startup- és natív crash-próbákkal.
- [x] A metrika-workflow release-ágon offline tesztel, éles gyűjtés nélkül.

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
- A kombinált `8f0cac1` release-állapot mindkét platform-CI-je sikeres:
  [Windows](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41328115042),
  [Linux](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41328114909).
  Mindkét platformon sikeres a csomagolás, natív komponens-/jogi leltár,
  portable-validáció, csomagolt startup és mesterséges natív crash-próba.
  A tag-only publikálási/jogi kapuk helyesen kimaradtak: nem tagelt futás.
- Az integrált Windows EXE három kötelező indulása **2,828 / 2,422 / 3,250 s**,
  mind PASS, 15 s limittel és retry nélkül. A korábbi release-ág timeoutját
  már az integrált startup-javítást tartalmazó sikeres futás váltotta fel.
- A metrikakód/workflow a korábban sikeres
  [release-metrika CI](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41306972550)
  óta változatlan: `test` sikeres, `collect` kihagyott. A jelenlegi teljes
  platformtesztek a 15 offline metrikaesetet is tartalmazzák. A startup/docs
  diff nem érinti a metrikaworkflow path-szűrőjét, ezért abból új külön futás
  nem indult. Éles adatírást nem állítunk elvégzettnek.
- Read-only `git merge-tree --write-tree origin/main HEAD`: konfliktusmentes.
  Ez nem módosította a maint. A végleges bizonyítékot rögzítő következő commit
  csak dokumentációt változtat; a release runtime-kódja változatlan.

Az első három előkészítési lépés teljesült. A következő engedélyköteles lépés
a main-integráció, nem új feature-fejlesztés. A main utáni éles metrikapróba
és a későbbi publikálás továbbra is nyitott, külön ellenőrzési szakasz.
