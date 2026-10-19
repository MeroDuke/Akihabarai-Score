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

Tulajdonosi döntés alapján az `1.4.0` dokumentációs QoL-alapozás lesz, tehát
ennél a kiadásnál tudatosan eltérünk a váltott ritmustól. Ez nem számozza át a
már elfogadott kiadásokat; az `1.5.0` típusáról külön döntünk.

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

### Következő release tervezési kapuja

Egy minor release scope-ját csak akkor zárjuk le, ha a következő tervezett
minor release már rendelkezik legalább egy tulajdonos által elfogadott,
célverzióhoz rendelt plan- vagy backlog-elemmel. Ennek nem kell fejlesztés
alatt állnia, és nem jelent határidő- vagy megvalósítási kényszert; csak azt
biztosítja, hogy a projektnek a lezárás után is legyen ismert következő célja.

Az egyetlen kivétel az, ha az ellenőrzött backlog valóban üres. Ezt a helyzetet
a lezáráskor a roadmapen tudatos állapotként rögzítjük. A sürgős hotfixeket ez
a tervezési kapu nem akadályozhatja.

## Termékprioritás

Az Akihabarai Score elsődleges és önálló terméke a desktop alkalmazás. Minden
desktop hibajavítás, stabilitási, diagnosztikai, funkcionális és QoL-fejlesztés
magasabb prioritású a webes változatnál. A WebUI opcionális, kísérleti és
tanulási célú irány; nem alakíthatja át öncélúan a desktop architektúrát, és
elmaradása nem veszélyezteti a projekt sikerét.

A részletes irányt és a tudatosan elvetett lehetőségeket a
[desktop-first döntési rekord](docs/decisions/desktop_first_product_direction.md)
rögzíti.

## 1.0.0 — kiadva: 2026-10-19

### Kiadási ütem

- **2026-10-19:** a dokumentációs review, Windows/Linux kézi átvétel és
  sikeres main-, majd tag-CI után a tulajdonos jóváhagyta az 1.0.0 kiadását.
  A korábbi december végi cél helyett a stabil állapot alapján korábban
  lezártuk a kiadást.
  [GitHub Release](https://github.com/MeroDuke/Akihabarai-Score/releases/tag/v1.0.0)
  · [Kiadási validáció](docs/validation/release_1_0_publication.md).
- **2027. első negyedév:** fejlesztési pihenő és valós használati időszak. Az
  1.0.0 készülő videók produkciós baseline-ja; csak indokolt hotfix szakíthatja
  meg a pihenőt, az alább elfogadott környezetfrissítés kivételével.

### Elkészült

- [Natív crash-diagnosztikai alap](plans/completed/native-crash-diagnostics.md)
- [Csomagolt alkalmazás startup crash-védelme és hiteles smoke tesztje](plans/completed/packaged-startup-crash-protection.md)
- [UI-független alkalmazásmag refaktor](plans/completed/ui_independent_core_refactor.md)
- [Refaktor stabilizációs kapu](plans/completed/refactor_stabilization.md)
- [Natív crash-diagnosztika – platformbizonyíték](plans/completed/native-crash-diagnostics-phase-2.md)
- [GPLv3 runtime compliance és tiszta portable csomag](plans/completed/gpl_runtime_and_release_layout.md)
- [1.0.0 release-előkészítés](plans/completed/release_1_0_0_preparation.md) —
  verzió, changelog, dokumentációs review és Windows/Linux kézi átvétel kész.
  Az ideiglenes tesztcsomag-megőrzés visszaállt release-only működésre.

### Lezárt release-ellenőrzések

- [Determinisztikus mixed-DPI ablakindítás](plans/completed/mixed_dpi_startup_geometry.md) —
  az elsődleges képernyőhöz rögzített, használható geometriára korlátozott
  startup és monitor-DPI diagnosztika.
- [Linux CI runner baseline-rögzítés](plans/completed/linux_ci_runner_migration.md) —
  az 1.0.0 build explicit Ubuntu 24.04 baseline-ra rögzítése az
  `ubuntu-latest` automatikus átállása előtt; a 26.04 migráció a szinkronizált
  Python-frissítéshez kapcsolódik.
- A closed beta alatt megerősített kritikus regressziók javítva.
- A changelog kiadási dátuma: 2026-10-19.
- Teljes Windows- és Linux-integrációs/regressziós ellenőrzés sikeres.
- A `main` merge és a release külön tulajdonosi jóváhagyással elkészült;
  a main- és tag-CI zöld, a publikált csomagok letöltése és validációja sikeres.

## 1.1.0 — Quality of Life

A környezetfrissítés javasolt célablaka 2026 december–2027 január; ez nem
merev kiadási határidő. A támogatási és kompatibilitási ellenőrzés miatt ez a
karbantartás megelőzi a korábban késő tavaszra tervezett fejlesztéseket.

### Elfogadva

- [Szinkronizált Python runtime-frissítés](plans/active/synchronized_python_runtime_upgrade.md) —
  Score, webprojekt és fejlesztői PC összehangolt frissítése; Ubuntu 26.04 CI,
  fejlesztői eszközök bekötése és a régi helyi Pythonok ellenőrzött eltávolítása.
  A webprojekt saját repositoryban és saját kiadásban változik.

- [Release-letöltések, grafikon és README-jelvények](plans/active/release_download_metrics.md) —
  GitHub-oldali, alkalmazástelemetria nélküli napi idősor és grafikon;
  tömör README badge-rendszer, külön Windows/Linux alkalmazásletöltés-számlálóval.

Az `1.1.0` további scope-ja nincs előre kitöltve. Új elem csak külön
tulajdonosi elfogadással kerülhet a release-be.

## 1.2.0 — funkcióbővítő release

### Elfogadva

- [Desktop onboarding](plans/active/desktop_onboarding.md) — az első használatot
  segítő alkalmazáson belüli bevezetés. A usability backlogból csak ez az elem
  került a release-be; a részletes UX-et fejlesztés előtt pontosítjuk.

## 1.3.0 — Quality of Life

### Elfogadva

- [Kereszt-réteges tracing és diagnosztika](plans/active/cross_layer_tracing.md) —
  az 1.1.0-ból áthelyezett desktop-first nyomvonal a Qt UI, application
  workflow-k, domain és adapterek kommunikációjához. Külön dátum még nincs.

## 1.4.0 — dokumentációs Quality of Life

### Elfogadva

- [Belső termékspecifikáció és felhasználói útmutató](plans/active/product_specification_and_user_guide.md) —
  a kezdeti, lezárható specifikációs és User Guide-csomag elkészítése. Ezután
  a dokumentáció az érintett feature-ökkel együtt frissül, nem külön örökös
  fejlesztési kezdeményezésként. Az 1.2.0 onboardingjához szükséges részek
  korábban is elkészülhetnek; az onboarding célverziója nem változik.

## Javasolt desktop kezdeményezések — célverzió nélkül

- [Desktop usability és felfedezhetőségi backlog](plans/active/desktop_usability_backlog.md) —
  későbbi QoL release-ekhez külön kiválasztható, nem automatikusan vállalt
  súgó-, felfedezhetőségi és Linux UI-jelöltek; az onboarding külön 1.2.0 terv.
  Külön release-ekben választhatók ki: onboarding → súgók → fennmaradó
  felfedezhetőségi problémák → Linux vizuális rendbetétel. A Linux indulási és
  alapműködési ellenőrzése közben is megmarad; további célverzió még nincs.

## 1.0.0 utáni technikai karbantartás — célverzió nélkül

- [Git ág- és tag-housekeeping](plans/active/git_housekeeping.md) — egy korai,
  később kiválasztandó release kísérő QoL-eleme: leltár, besorolás és külön
  jóváhagyott takarítás. A kiadási tagek nem automatikus törlési jelöltek;
  most nincs törlés vagy konkrét célverzió.
- [Windows digitális aláírás megvalósíthatósági vizsgálata](plans/active/windows_code_signing_feasibility.md) —
  Authenticode, SmartScreen, költség és biztonságos CI-kulcskezelés vizsgálata;
  későbbi release kísérő eleme, külön feature- vagy QoL-tartalom mellett.
  Akkor újravizsgáljuk, akár más saját projekttel közös kiadói megoldásként;
  a halasztás vagy elvetés is elfogadható eredmény. Nem önálló release és nem
  vásárlási vagy bevezetési ígéret; célverziót később választunk.

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
