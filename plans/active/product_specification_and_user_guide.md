# Belső termékspecifikáció és felhasználói útmutató

- Plan ID: `PLAN-006`
- Status: `accepted`
- Target release: `1.4.0`
- Type: `documentation`
- Priority: `high`
- Created: `2026-09-29`
- Last reviewed: `2026-10-19`
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

Az `1.4.0` dokumentációs QoL-csomag a kezdeti alapozást zárja le. Ezután a
specifikáció és User Guide karbantartása minden érintett funkciófejlesztés és
működésváltozás része, ugyanabban a változtatásban; nem örökké nyitott plan.

Az [onboarding](desktop_onboarding.md) továbbra is `1.2.0` célverziójú külön
fejlesztés: a hozzá szükséges dokumentációs részek korábban elkészülhetnek,
nem kell megvárnia a teljes kezdeti csomagot. AI-támogatott GitHub issue-triage
csak későbbi lehetőség, nem része ennek a tervnek.

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

### Lezárható alapozás és folyamatos karbantartás

Az alapozás az elfogadási feltételek teljesülésekor lezárható és a terv a
`completed/` alá kerül. A létrejött aktuális specifikáció és útmutató a
`docs/` megfelelő kategóriáiba tartozik. Ezt követően minden érintett
feature vagy javítás része az elvárt működés, felhasználói lépések és
tesztbizonyítékok frissítése. A karbantartási szabályt az alapozás lezárásakor
a repository fejlesztési követelményeiben is rögzíteni kell.

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
- [ ] A feature-ökkel közös specifikáció- és User Guide-karbantartás szabálya
  bekerült a repository fejlesztési követelményeibe.
- [ ] A dokumentáció és a roadmap frissült.

## Kockázatok és visszaállítás

Kockázat a történeti implementáció téves normatívvá emelése és az elavulás.
Ellenszere a tulajdonosi review, tesztbizonyíték, kis feldolgozási szeletek és
az a szabály, hogy viselkedésváltozáskor a specifikáció és User Guide is frissül.

## Nyitott kérdések

- Magyar legyen-e az elsődleges nyelv, és kell-e később angol változat?
- Milyen képernyőképeket érdemes verziózott dokumentációban fenntartani?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-09-29 | Két dokumentációs réteg készül. | A belső szándék és a felhasználói útmutatás eltérő közönséget szolgál. |
| 2026-09-29 | A specifikáció csak review után normatív. | A kód önmagában nem bizonyítja a szándékot. |
| 2026-10-19 | A kezdeti csomag elfogadva az `1.4.0` dokumentációs QoL-kiadásba. | Tulajdonosi döntés; tudatos eltérés a váltott release-ritmustól. Az onboarding marad `1.2.0`, releváns dokumentációja előrevehető. |
| 2026-10-19 | Az alapozás lezárható; utána a dokumentáció a feature-ökkel együtt frissül. | Nem külön, folyamatosan nyitva tartott fejlesztés, hanem az elavulást megelőző karbantartási követelmény. |

## Megvalósítási napló

