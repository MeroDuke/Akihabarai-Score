# Csomagolt alkalmazás startup crash-védelme

- Plan ID: `PLAN-000`
- Status: `completed`
- Target release: `1.0.0`
- Type: `reliability`
- Priority: `critical`
- Created: `2026-09-28`
- Last reviewed: `2026-09-28`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

A Windows PyInstaller build egy inkompatibilis Qt-függőség miatt induláskor
hibaablakot mutatott, de a régi CI smoke teszt ezt sikernek tekinthette, mert
csak azt ellenőrizte, hogy a process öt másodpercig életben maradt-e. A Linux
smoke teszt szintén csak process-élettartamot figyelt, valódi alkalmazás-ready
állapotot nem.

## Cél

- A korai Python- és importhibákból külön startup crash log készüljön.
- A folyamat hibás exit code-dal álljon le.
- A CI csak a valóban felépült főablakot fogadja el sikeres indulásnak.
- Windows és Linux ugyanazt az ellenőrzési szerződést használja.

## Megvalósítás

- Standard library-only `app/launcher.py` tölti be a valódi alkalmazást.
- Startup kivételnél `logs/crash-*.log` készül teljes Python tracebackkel.
- A normál `SystemExit` változatlanul továbbhalad.
- A főablak megjelenítése után `Main window ready` esemény kerül a normál logba.
- A közös `scripts/smoke_test_packaged_app.py` megkülönbözteti:
  - a ready állapotot;
  - a crash log létrejöttét;
  - a korai process-kilépést;
  - a startup timeoutot.
- A PyInstaller entrypoint a launcherre váltott.
- Windows és Linux CI ugyanazt a smoke runnert használja, és megőrzi a
  diagnosztikai artifactokat.

## Tesztelés és bizonyíték

- Unit tesztek fedik a sikeres indítást, crash logot és normál `SystemExit` utat.
- Workflow tesztek fedik a ready, crash-log és korai kilépés ágakat.
- Teljes helyi regresszió: `593 passed`.
- A helyi csomagolt Windows EXE elérte a `Main window ready` állapotot.
- Commit: `33e6c1d Harden packaged application startup checks`.
- [Windows CI — sikeres](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/36438702696)
- [Linux CI — sikeres](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/36438702692)

## Korlátok

- A launcher előtt bekövetkező bootloader/native hiba nem garantáltan tud
  Python crash logot írni, de hibás exit code-dal megbuktatja a CI-t.
- A jelenlegi crash log nem tartalmaz natív stacket vagy process dumpot.
- A faulting modulból önmagában nem lehet gyökérokot vagy felelősséget
  bizonyítani.

## Eredmény

Az 1.0.0 csomagolt alkalmazásának indulása már nem pusztán process-élettartam
alapján minősül sikeresnek. A megoldás elfogadási feltételei teljesültek.
