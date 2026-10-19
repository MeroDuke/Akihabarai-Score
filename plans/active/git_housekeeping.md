# Git ág- és tag-housekeeping

- Plan ID: `PLAN-016`
- Status: `proposed`
- Target release: `TBD`
- Type: `reliability`
- Priority: `medium`
- Created: `2026-10-19`
- Last reviewed: `2026-10-19`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

A tulajdonos jelzése szerint több mint húsz ág és tag gyűlt össze. Egy részük
lezárt fejlesztéshez vagy ideiglenes próbához tartozhat, de a szükségtelenségük
még nem ellenőrzött. A sok referencia nehezíti az áttekintést.

## Cél

Korai, később kiválasztandó release mellé illeszthető QoL-karbantartás:
ellenőrzött leltár és jóváhagyott takarítás, értékes történeti vagy kiadási
referenciák elvesztése nélkül. Nem önálló release; célverziója még nincs.

## Nem cél

- Mostani törlés vagy automatikus törlési felhatalmazás.
- Ágak vagy tagek törlése pusztán koruk vagy darabszámuk alapján.
- Publikált release-tagek rutinszerű eltávolítása vagy áthelyezése.
- Commit-history átírása, force-push, GitHub Release-ek vagy artifactok törlése.

## Jelenlegi állapot

A darabszám felhasználói jelzés, nem ebben a tervben végrehajtott audit.
A helyi ágak, távoli ágak, tagek, nyitott PR-ok és worktree-k kapcsolatait
a végrehajtás előtt kell felmérni. A történeti release-tag jellemzően
megőrzendő kiadási bizonyíték, nem eldobható fejlesztési ág.

## Tervezett megoldás

1. Leltár készítése helyi és távoli referenciákról commitazonosítókkal.
2. Külön besorolás: aktív, megőrzendő történeti/kiadási referencia, összeolvasztott
   és törölhető jelölt, illetve tisztázandó. Az egyedi, nem integrált commitokat,
   nyitott PR-okat, release-eket és worktree-ket külön ellenőrizzük.
3. A dokumentációs, CI-, source-availability és egyéb tartós hivatkozások
   felmérése a törlésre jelölt referenciákhoz.
4. Tételes javaslat és visszaállítási leltár; szükség szerint külön biztonsági
   mentés a törlés előtt. A távoli ág törlése is külön látható művelet.
5. Tulajdonosi jóváhagyás az explicit helyi/távoli törlési listára. Tag törlése
   külön indoklást igényel; a publikált kiadásokat alapértelmezetten megőrizzük.
6. Jóváhagyott takarítás után új leltár és a megőrzött hivatkozások ellenőrzése.

## Platform- és kompatibilitási szempontok

Nem változtat az alkalmazás működésén vagy csomagolásán. A GitHub workflow-k
branch/tag triggerjeit, a stabil maint és az aktív release-ágakat meg kell őrizni.
Más munkamenet worktree-jét és munkáját nem bontjuk meg.

## Tesztstratégia

- Elsőként csak olvasási audit és tételes dry-run lista.
- Minden jelöltnél integráltság vagy egyedi commitok, hivatkozások és mentés ellenőrzése.
- Takarítás után a jóváhagyott előtte/utána leltár összevetése.
- A stabil kiadás tagje, forráscommitja, aktív ágak és release-hivatkozások feloldhatók.
- Markdown-hivatkozás- és diffellenőrzés. Tisztán Git-karbantartásnál nem
  szükséges új alkalmazásfeature-t vagy Qt workflow-t létrehozni; ha CI-konfiguráció
  is változna, az külön jóváhagyott scope és releváns validáció tárgya.

## Elfogadási feltételek

- [ ] A feladat kísérő QoL-elemként elfogadott célrelease-t kapott.
- [ ] A helyi és távoli ág-/tag-leltár besorolással és indoklással elkészült.
- [ ] Az egyedi commitok, PR-ok, worktree-k és tartós hivatkozások ellenőrzése kész.
- [ ] A pontos törlési listát a tulajdonos jóváhagyta, visszaállítási adatok rendelkezésre állnak.
- [ ] Csak jóváhagyott referenciák változtak; a kiadási bizonyítékok és aktív munka megmaradt.
- [ ] Az utóellenőrzés, dokumentáció és roadmap frissítése kész.

## Kockázatok és visszaállítás

Téves törlés elveszíthet nem integrált munkát vagy megtörhet kiadási és
compliance-hivatkozásokat. A commitazonosítók puszta feljegyzése nem garantálja
az objektumok hosszú távú megmaradását, ezért szükség esetén visszaállítható
mentést is készítünk. Visszaállítás csak ellenőrzött mentésből és tételesen történik.

## Nyitott kérdések

- Melyik korai release mellé kerül a feladat?
- Mely ideiglenes referenciák bizonyulnak valóban feleslegesnek az auditban?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-10-19 | Git-housekeeping felvéve későbbi korai release kísérő QoL-elemeként, célverzió nélkül. | Az ágak és tagek áttekinthetősége javítandó; most csak tervezés, törlés nélkül. |

## Megvalósítási napló

Még nem indult el.
