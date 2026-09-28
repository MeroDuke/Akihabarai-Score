# Projekttervek

A `plans/` könyvtár a jövőbeli vagy már lezárt fejlesztési kezdeményezések
helye. Célja, hogy a problémák, döntések, release-célok és elfogadási
feltételek ne csak beszélgetésekben vagy emlékezetben maradjanak meg.

## Határ a dokumentumtípusok között

- A `docs/` azt írja le, hogyan működik jelenleg a termék és az architektúra.
- A `plans/` azt írja le, mit és miért akarunk megváltoztatni.
- A gyökérben lévő `ROADMAP.md` azt mutatja meg, melyik terv melyik release-hez
  tartozik, illetve mi vár még célverzióra.
- A teszt- és validációs bizonyíték nem automatikusan terv. Annak végleges
  helyéről a dokumentáció későbbi, hivatkozás-ellenőrzött rendezése dönt.

## Könyvtárak

- `active/`: javasolt, elfogadott, folyamatban lévő vagy blokkolt tervek.
- `deferred/`: tudatosan elhalasztott vagy célverzió nélküli parkoltatott tervek.
- `completed/`: megvalósított vagy lezárt tervek és az eredményük.
- `plan-template.md`: új terv kötelező kiindulási sablonja.

## Kötelező metaadatok

Minden terv elején szerepeljen:

- stabil plan ID;
- státusz;
- célverzió vagy `TBD`;
- típus és prioritás;
- létrehozás és utolsó felülvizsgálat dátuma;
- kapcsolódó roadmap-bejegyzés.

A támogatott státuszok:

```text
proposed
accepted
in-progress
blocked
deferred
completed
cancelled
```

Az `in-progress` státusz feltétele a tulajdonos által elfogadott célverzió. A
`TBD` célverziójú terv nem release-vállalás és nem indíthat automatikusan
fejlesztést.

## Életciklus

1. Az ötlet a sablon alapján `proposed` tervként kerül az `active/` mappába.
2. A roadmap röviden hivatkozik rá, de nem másolja át a részleteit.
3. A scope és a célverzió tulajdonosi elfogadása után `accepted` lesz.
4. A fejlesztés kezdetekor `in-progress` státuszt kap.
5. A fejlesztés előtt elkészülnek a szükséges unit/low-level és teljes
   felhasználói workflow/regressziós tesztek.
6. Az elfogadási feltételek és a helyi, majd CI-ellenőrzések teljesülése után a
   terv `completed/` alá kerül, és rögzíti a commitokat, teszteket és az
   esetleges tervtől való eltéréseket.
7. Elhalasztás vagy törlés esetén a döntés indoka megmarad a dokumentumban.

## Karbantartási szabály

Egy tervet ugyanabban a változtatásban kell frissíteni, amikor annak scope-ja,
célverziója, státusza vagy elfogadási feltétele megváltozik. A `ROADMAP.md`
összefoglalójának ezzel konzisztensnek kell maradnia.
