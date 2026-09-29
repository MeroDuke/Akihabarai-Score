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

## Termékprioritás

Az Akihabarai Score elsődleges és önálló terméke a desktop alkalmazás. Minden
desktop hibajavítás, stabilitási, diagnosztikai, funkcionális és QoL-fejlesztés
magasabb prioritású a webes változatnál. A WebUI opcionális, kísérleti és
tanulási célú irány; nem alakíthatja át öncélúan a desktop architektúrát, és
elmaradása nem veszélyezteti a projekt sikerét.

A részletes irányt és a tudatosan elvetett lehetőségeket a
[desktop-first döntési rekord](docs/decisions/desktop_first_product_direction.md)
rögzíti.

## 1.0.0 — cél: 2027. március vége

### Elkészült

- [Natív crash-diagnosztikai alap](plans/completed/native-crash-diagnostics.md)
- [Csomagolt alkalmazás startup crash-védelme és hiteles smoke tesztje](plans/completed/packaged-startup-crash-protection.md)
- [UI-független alkalmazásmag refaktor](plans/completed/ui_independent_core_refactor.md)
- [Refaktor stabilizációs kapu](plans/completed/refactor_stabilization.md)
- [Natív crash-diagnosztika – platformbizonyíték](plans/completed/native-crash-diagnostics-phase-2.md)
- [GPLv3 runtime compliance és tiszta portable csomag](plans/completed/gpl_runtime_and_release_layout.md)

### Release előtt

- A closed beta alatt megerősített kritikus regressziók javítása.
- Az 1.0.0 verzió-, changelog- és felhasználói dokumentációjának véglegesítése.
- Teljes Windows- és Linux-integrációs/regressziós ellenőrzés.
- Zöld CI/CD és külön tulajdonosi jóváhagyás a `main` merge, majd a release előtt.

## 1.1.0 — Quality of Life

### Elfogadva

- [Kereszt-réteges tracing és diagnosztika](plans/active/cross_layer_tracing.md) —
  desktop-first nyomvonal a Qt UI, application workflow-k, domain és adapterek
  kommunikációjához.

Az `1.1.0` további scope-ja nincs előre kitöltve. Új elem csak külön
tulajdonosi elfogadással kerülhet a release-be.

## 1.2.0 — funkcióbővítő release

A következő desktop funkció még nincs kiválasztva. A verziót nem töltjük ki
mesterségesen webes vagy nem igazolt ötlettel; a scope külön döntés után kerül
ide.

## Javasolt desktop kezdeményezések — célverzió nélkül

- [Belső termékspecifikáció és felhasználói útmutató](plans/active/product_specification_and_user_guide.md) —
  a kód, tesztek és döntések felülvizsgált specifikációvá, majd feladatközpontú
  User Guide-dá alakítása.
- [Desktop usability és felfedezhetőségi backlog](plans/active/desktop_usability_backlog.md) —
  későbbi QoL release-ekhez külön kiválasztható, nem automatikusan vállalt
  onboarding-, felfedezhetőségi és Linux UI-jelöltek.

## Távolabbi irányok

- [Opcionális webes Pontozó](plans/deferred/optional_web_score_direction.md) —
  iteratív, webnatív mellékirány a külön Könyvespolc webprojektben. A desktop
  minden fejlesztése megelőzi; célverzió és aktív Score release-scope nincs.
- OBS-integráció és Discord bot csak távoli, nem vállalt lehetőség. Előbbi
  esetén elsőként browser source vagy overlay vizsgálandó.
- Profilhoz kötött session- és pontozásmentés csak jóval később, autentikációs,
  adatbázis- és adatvédelmi döntés után kerülhet elő.
- AI-alapú GitHub issue-triage és hotfix-előkészítés csak a belső
  termékspecifikáció és User Guide elkészülte után vizsgálható kísérletként.

## Tudatosan nem követett irányok

- publikus vagy belső SDK-termék;
- CLI kliens;
- generatív AI-alapú Strengths funkció.

## Státuszjelölések

- **Javaslat:** vizsgálható irány, még nem vállalt release-scope.
- **Elfogadva:** a cél és a célverzió jóváhagyott, a megvalósítás még nem indult el.
- **Folyamatban:** aktív fejlesztés és tesztelés zajlik.
- **Blokkolva:** ismert akadály miatt nem haladhat.
- **Elhalasztva:** megőrzött terv, de nincs aktív célverziója.
- **Elkészült:** az elfogadási feltételek teljesültek és az eredmény dokumentált.
- **Törölve:** tudatosan elvetett terv, a döntés indoklása megmarad.
