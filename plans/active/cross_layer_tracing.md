# Kereszt-réteges tracing és diagnosztika

- Plan ID: `PLAN-005`
- Status: `accepted`
- Target release: `1.1.0`
- Type: `reliability`
- Priority: `high`
- Created: `2026-09-29`
- Last reviewed: `2026-09-29`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

A jelenlegi naplózás több fontos komponenshatárt láthatóvá tesz, de egy
felhasználói művelet teljes útja még nem követhető egységes azonosítóval a Qt
UI, az application/workflow service-ek, a domain, az adapterek és az eredmény
megjelenítése között.

## Cél

Desktop-first diagnosztikai rendszer, amelyből megállapítható, mely réteg mit
küldött, melyik komponens fogadta, mi lett az eredmény, és hol szakadt meg a
folyamat. A fejlesztés WebUI nélkül is teljes értékű.

## Nem cél

- Külső telemetria vagy automatikus logfeltöltés.
- Publikus SDK vagy általános integrációs platform.
- WebUI-megvalósítás.
- Minden korábbi logbejegyzés egyszeri teljes átírása.

## Jelenlegi állapot

A komponens- és eseményelnevezési alap a
[`logging_boundaries.md`](../../docs/architecture/logging_boundaries.md)
dokumentumban létezik. A Tier Board ürítése már külön frontend-, core- és
domaineseményeket használ. A teljes cross-layer correlation és per-action
context még hiányzik.

## Tervezett megoldás

- Műveletenkénti stabil trace/correlation ID.
- Egységes context a Qt UI, application service, domain és adapter határokon.
- Stabil komponens- és eseményazonosítók.
- Indítás, fogadás, eredmény, hiba, megszakítás és kihagyás külön eseményei.
- Strukturált mezők az ember által olvasható log megtartásával.
- A régi `ui` események fokozatos migrációja `qt_ui` identitásra.
- Scoring, profile mix, módváltás, Tier Board, AniList, cover image, clipboard
  és export folyamatok fokozatos lefedése.
- A bizonyított hiba, az érintett réteg és a feltételezett hibaforrás
  megkülönböztetése.
- Későbbi JSON-log lehetőségének értékelése a retention és adatvédelmi
  szabályok megtartásával.

## Platform- és kompatibilitási szempontok

Windows és Linux azonos stabil eseményazonosítókat használ. A tracing nem
okozhat érzékelhető UI-lassulást, és loggerhiba nem akadályozhat felhasználói
műveletet vagy alkalmazásindítást.

## Tesztstratégia

- Unit tesztek a trace context és mezőpropagáció szabályaira.
- Low-level tesztek a stabil azonosítókra.
- Legalább egy teljes Qt workflow ugyanazzal a trace ID-val a művelettől az
  eredményig.
- Hibás és megszakított workflow ellenőrzése.
- Loggerhiba melletti működés ellenőrzése.
- Qt-tesztek helyben `QT_QPA_PLATFORM=offscreen` módban, CI előtt zölden.

## Elfogadási feltételek

- [ ] Legalább egy teljes desktop workflow végigkövethető egy trace ID-val.
- [ ] A logból megállapítható a kommunikáló rétegek sorrendje és eredménye.
- [ ] Stabil, dokumentált komponens- és eseményazonosítók készültek.
- [ ] Az érzékeny és túl nagy diagnosztikai mezők kezelése tesztelt.
- [ ] Loggerhiba nem akadályozza a felhasználói workflow-t.
- [ ] A releváns helyi tesztek sikeresek.
- [ ] A teljes workflow/regressziós teszt helyben sikeres.
- [ ] A releváns CI/CD workflow-k sikeresek.
- [ ] A dokumentáció és a roadmap frissült.

## Kockázatok és visszaállítás

A túl részletes napló zajt, teljesítményromlást vagy adatvédelmi kockázatot
okozhat. A bevezetés workflow-szeletenként történik. A tracing leválasztható
marad az üzleti működésről, hogy funkcióvesztés nélkül visszaállítható legyen.

## Nyitott kérdések

- Mely workflow-k kerüljenek az első kötelező példafolyamat mellé?
- Kell-e már az `1.1.0`-ban JSON-kimenet?
- Hogyan jelenjen meg a trace ID a megosztható diagnosztikai csomagban?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-09-29 | A terv az `1.1.0` elsődleges fejlesztése. | A desktop diagnosztizálhatósága minden későbbi munkát támogat. |
| 2026-09-29 | A megvalósítás desktop-first. | A WebUI opcionális. |

## Megvalósítási napló

