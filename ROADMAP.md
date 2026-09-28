# Akihabarai Score roadmap

Ez a fájl a projekt tervezett irányainak rövid, release-szintű áttekintése.
A részletes célokat, döntéseket, kockázatokat és elfogadási feltételeket a
kapcsolódó `plans/` dokumentumok tartalmazzák.

A roadmapbe kerülés önmagában nem engedélyezi a fejlesztést, a release-t, a
tag létrehozását vagy a `main` ágba történő merge-et.

## Release-ritmus az 1.0.0 után

A tervezett minor kiadások két típusa felváltva követi egymást:

1. **Quality of Life (QoL) release:** a meglévő funkciók használhatóságát,
   kényelmét, érthetőségét és stabilitását javítja. Tartalmazhat hibajavításokat,
   de alapvetően nem új képesség bevezetése a célja.
2. **Funkcióbővítő release:** legalább egy korábban nem létező felhasználói
   képességet vezet be, a hozzá tartozó tesztekkel és dokumentációval együtt.
   Emellett hibajavításokat is tartalmazhat.

Az `1.0.0` után az első tervezett minor kiadás az `1.1.0` QoL release, ezt az
`1.2.0` funkcióbővítő release követi. A ritmus ezután is felváltva folytatódik,
amíg egy tudatos roadmap-döntés meg nem változtatja.

A sürgős hotfixek nem részei ennek a váltásnak. Mindig az érintett kiadás
patch-verzióját növelik (`x.y.1`, `x.y.2`, …), függetlenül attól, hogy az adott
minor verzió QoL vagy funkcióbővítő release volt. A hotfix nem tolja el a
következő minor kiadás tervezett típusát.

Ez egy hobbi projekt: a kiadásokat nem mesterséges határidő vagy minimális
csomagméret vezérli. Egy minor release akkor készül el, amikor a hozzá elfogadott
scope megfelelő minőségben elkészült. A váltott ritmust akkor is megtartjuk, ha
egy QoL vagy funkcióbővítő kiadásba csak kevés fejlesztés kerül; emiatt nem
ugrunk át release-típust. Az elfogadott planeket a típusuk, függőségeik és
ésszerű sorrendjük alapján rendeljük majd a megfelelő minor kiadáshoz.

## 1.0.0 — cél: 2027. március vége

### Elkészült

- [Natív crash-diagnosztikai alap](plans/completed/native-crash-diagnostics.md)
- [Csomagolt alkalmazás startup crash-védelme és hiteles smoke tesztje](plans/completed/packaged-startup-crash-protection.md)
- [UI-független alkalmazásmag refaktor](plans/completed/ui_independent_core_refactor.md)
- [Refaktor stabilizációs kapu](plans/completed/refactor_stabilization.md)
- [Natív crash-diagnosztika – platformbizonyíték](plans/completed/native-crash-diagnostics-phase-2.md)

### Release előtt

- A closed beta alatt megerősített kritikus regressziók javítása.
- Az 1.0.0 verzió-, changelog- és felhasználói dokumentációjának véglegesítése.
- Teljes Windows- és Linux-integrációs/regressziós ellenőrzés.
- Zöld CI/CD és külön tulajdonosi jóváhagyás a `main` merge, majd a release előtt.

## Távolabbi irányok

- Webes frontend — külön részletes terv és célverzió még nincs elfogadva.

## Státuszjelölések

- **Javaslat:** vizsgálható irány, még nem vállalt release-scope.
- **Elfogadva:** a cél és a célverzió jóváhagyott, a megvalósítás még nem indult el.
- **Folyamatban:** aktív fejlesztés és tesztelés zajlik.
- **Blokkolva:** ismert akadály miatt nem haladhat.
- **Elhalasztva:** megőrzött terv, de nincs aktív célverziója.
- **Elkészült:** az elfogadási feltételek teljesültek és az eredmény dokumentált.
- **Törölve:** tudatosan elvetett terv, a döntés indoklása megmarad.
