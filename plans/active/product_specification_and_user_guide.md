# Belső termékspecifikáció és felhasználói útmutató

- Plan ID: `PLAN-006`
- Status: `proposed`
- Target release: `TBD`
- Type: `documentation`
- Priority: `high`
- Created: `2026-09-29`
- Last reviewed: `2026-09-29`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

A működést jelenleg a kód, a tesztek, szétszórt műszaki dokumentumok és
korábbi döntések együtt írják le. Nincs feature-enkénti normatív specifikáció,
és nincs teljes, feladatközpontú User Guide.

## Cél

Két egymásra épülő dokumentációs réteg:

1. a kód, tesztek és döntési előzmények visszaalakítása felülvizsgált belső
   termékspecifikációvá;
2. a specifikációból és a működő alkalmazásból felhasználói útmutató készítése.

Az eredmény később alkalmazáson belüli onboarding és AI-támogatott GitHub
issue-triage alapja lehet, de ezek nem részei ennek a tervnek.

## Nem cél

- A kód kritikátlan specifikációvá nyilvánítása.
- Forráskód-refaktor vagy funkciófejlesztés.
- WebUI-dokumentáció.
- Automatikus issue-kezelés, kódmódosítás vagy release.
- A teljes kézikönyv beépítése az alkalmazás UI-jába.

## Jelenlegi állapot

A `docs/` több aktuális műszaki dokumentumot tartalmaz. A README felhasználói
belépési pont, de nem kézikönyv. A tesztek sok szabályt bizonyítanak, de a
mögöttes termékszándék nem mindenhol olvasható ki belőlük.

## Tervezett megoldás

### Belső specifikáció

Feature-enként dokumentálandó a cél, felhasználói érték, workflow,
állapotátmenet, invariáns, `works as designed` eset, hiba, helyreállás, edge
case, nem támogatott viselkedés, lokalizációs és lifecycle-szabály, valamint a
kapcsolódó automata és kézi bizonyíték.

A rekonstruált szándék csak tulajdonosi review után válik normatívvá, így egy
történeti bug nem rögzül automatikusan elvárt működésként.

Javasolt sorrend: scoring; profile mix; scored és Freehand mód; Tier Board;
kártyaszerkesztés; AniList és Offline mód; cover lifecycle; lokalizáció;
clipboard és képexport; beállítások; logging, tracing és crash-diagnosztika;
csomagolási és platformhatárok.

### User Guide

Feladatközpontúan bemutatja az első értékelést, profilokat, dimenziókat,
eredményt, Online/Offline címbevitelt, Tier Boardot, módokat,
kártyaszerkesztést, exportot, nyelvet, gyakori kérdéseket és hibajelentést.

## Platform- és kompatibilitási szempontok

A User Guide elsődlegesen a támogatott Windows desktop működést írja le, és
jelöli a validált Linux-különbségeket. A leírás a csomagolt alkalmazás
tényleges felirataival és viselkedésével egyezik.

## Tesztstratégia

- A specifikáció állításainak összekötése kóddal és tesztbizonyítékkal.
- Minden User Guide workflow kézi végrehajtása a dokumentált lépések szerint.
- Helyi Markdown-linkek automatizált ellenőrzése.
- Képernyőképek aktualitásának felülvizsgálata.

## Elfogadási feltételek

- [ ] Jóváhagyott specifikációs sablon készült.
- [ ] A fő desktop feature-ök felülvizsgált specifikációt kaptak.
- [ ] Elkülönül a megfigyelt implementáció és az elfogadott termékszándék.
- [ ] Elkészült a feladatközpontú User Guide.
- [ ] A User Guide fő workflow-it manuálisan ellenőriztük.
- [ ] Minden helyi Markdown-hivatkozás feloldható.
- [ ] A dokumentáció és a roadmap frissült.

## Kockázatok és visszaállítás

Kockázat a történeti implementáció téves normatívvá emelése és az elavulás.
Ellenszere a tulajdonosi review, tesztbizonyíték, kis feldolgozási szeletek és
az a szabály, hogy viselkedésváltozáskor a specifikáció és User Guide is frissül.

## Nyitott kérdések

- Melyik release-be vagy folyamatos ciklusba kerüljön a program?
- Magyar legyen-e az elsődleges nyelv, és kell-e később angol változat?
- Milyen képernyőképeket érdemes verziózott dokumentációban fenntartani?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-09-29 | Két dokumentációs réteg készül. | A belső szándék és a felhasználói útmutatás eltérő közönséget szolgál. |
| 2026-09-29 | A specifikáció csak review után normatív. | A kód önmagában nem bizonyítja a szándékot. |

## Megvalósítási napló

