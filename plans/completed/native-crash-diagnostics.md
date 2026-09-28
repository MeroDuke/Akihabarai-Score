# Natív crash-diagnosztikai alap

- Plan ID: `PLAN-001`
- Status: `completed`
- Target release: `1.0.0`
- Type: `reliability`
- Priority: `high`
- Created: `2026-09-28`
- Last reviewed: `2026-09-28`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

Az 1.0.0 startup-védelme jól diagnosztizálja a Python- és importhibákat, és a
CI már megkülönbözteti a ténylegesen elkészült főablakot a pusztán életben
maradó hibafolyamattól. Ez azonban nem ad elegendő bizonyítékot minden natív
összeomláshoz, például Windows access violation, Linux `SIGSEGV`, Qt/PyQt vagy
platform-plugin hibák esetén.

A cél nem automatikus felelősségmegállapítás. Olyan diagnosztikai alap kell,
amely alapján nem sötétben tapogatózunk, és elkülöníthető, hogy a rendelkezésre
álló bizonyíték elsősorban saját Python-kódra, PyQt/Qt rétegre, rendszer- vagy
driverkomponensre, illetve ismeretlen eredetre mutat.

## Cél

- A Python exception, Python fatal fault és natív process crash elkülönítése.
- Az alkalmazásverzió, buildazonosító, platform, architektúra és indulási fázis
  rögzítése.
- A crash idején futó Python workflow lehetőség szerinti azonosítása.
- Windows és Linux alatt reprodukálható, mesterséges crash-próbák létrehozása.
- Olyan bizonyíték előállítása, amely alapján eldönthető a következő vizsgálati
  lépés és a valószínű érintett réteg.

## Nem cél

- A faulting modul automatikus hibáztatása.
- Automatikus crash-feltöltés vagy telemetria felhasználói hozzájárulás nélkül.
- Teljes Crashpad/Breakpad infrastruktúra bevezetése az első iterációban.
- Annak garantálása, hogy memóriarongálásnál a crash helye azonos az eredeti
  hibaforrással.
- Teljes natív minidump/core dump és szimbólum-infrastruktúra az első
  1.0.0-s diagnosztikai alapon túl.

## Jelenlegi állapot

Az 1.0.0 ág már tartalmazza:

- a standard libraryre épülő minimális launchert;
- startup Python exception esetén külön crash logot és hibás kilépési kódot;
- `Main window ready` indulási határt;
- Windows és Linux csomagolt-app smoke tesztet;
- korai kilépés, crash log és startup timeout megkülönböztetését.

A jelenlegi crash log időpontot, platformot, Python-verziót, frozen állapotot
és teljes Python tracebacket tartalmaz. Nem készít natív stacket vagy dumpot.

## Vizsgálandó megoldási lépcsők

### 1. Diagnosztikai metaadat és startup fázis

- alkalmazásverzió és build/commit azonosító;
- executable és munkakönyvtár;
- platform és architektúra;
- az utolsó sikeres startup fázis;
- egyedi crash azonosító.

### 2. Python fatal fault napló

A Python `faulthandler` nagyon korai, előre megnyitott naplófájllal történő
bekapcsolásának vizsgálata. Célja a Python thread stackek megőrzése natív fatal
fault környezetében is.

### 3. Platformnatív bizonyíték

- Windows: minidump, exception code, faulting module és betöltött modulok.
- Linux: core dump vagy dokumentált `coredumpctl`/GDB feldolgozás, signal és
  natív backtrace.
- Release-szimbólumok megőrzési és verzióazonosítási igényének felmérése.

### 4. Elsődleges triage

Bizonyítékalapú, óvatos kategóriák:

```text
own-python-code
pyqt-or-qt
operating-system
graphics-or-platform-plugin
native-unknown
insufficient-evidence
```

A kategória valószínű érintett réteget jelent, nem bizonyított gyökérokot.

## Tesztstratégia

- Kontrollált Python exception a launcher tesztfolyamatában.
- Kontrollált startup importhiba.
- Külön gyermekfolyamatban előállított Windows access violation.
- Külön gyermekfolyamatban előállított Linux `SIGSEGV`.
- A tesztfolyamat nem omlaszthatja össze a pytest vagy CI vezérlőfolyamatát.
- Ellenőrizni kell a log/dump létrejöttét, a hibás exit code-ot és az artifact
  megőrzését.
- A teljes csomagolt workflow-t helyben kell ellenőrizni a CI-be kerülés előtt.

## Elfogadási feltételek az 1.0.0-s alaphoz

- [x] A target release tulajdonosi jóváhagyást kapott.
- [x] A Python exception és a Python által észlelt natív fatal fault kimenete
  egyértelműen elkülönül.
- [x] A kimenet azonosítja az alkalmazásverziót, platformot, architektúrát,
  futtatási módot, executable-t, munkakönyvtárat és startup fázist.
- [x] Windows és Linux alatt futó, izolált mesterséges natív fatal-crash
  regressziós teszt rendelkezésre áll.
- [x] A CI sikertelen, ha a csomagolt alkalmazás váratlanul összeomlik.
- [x] A csomagolt alkalmazás startup naplói sikertelen CI futáskor artifactként
  feltöltésre kerülnek.
- [x] Dokumentált, hogy mely következtetések bizonyítottak és melyek csak
  elsődleges triage eredmények.

## Kockázatok

- A dumpok érzékeny futásidejű adatokat tartalmazhatnak; automatikus feltöltés
  nem vezethető be külön adatkezelési döntés nélkül.
- A crash handler maga is hibázhat, ezért minimálisnak és best-effort jellegűnek
  kell maradnia.
- A teljes natív stack szimbólumok nélkül kevéssé beszédes lehet.
- PyInstaller one-file kicsomagolási útvonalai nehezíthetik a modulazonosítást.
- A faulting modul nem feltétlenül a gyökérok tulajdonosa.

## Nyitott kérdések

- A natív dump szükséges-e egy 1.0.0 utáni második iterációban?
- Hol és mennyi ideig őrizzük meg a release-szimbólumokat?
- A felhasználói gépen készült dump manuálisan kerüljön-e hibajelentéshez?
- Milyen adatvédelmi figyelmeztetés szükséges egy dump megosztásához?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-09-28 | Külön terv készül a natív crash-diagnosztikáról. | Előbb diagnosztikai alap és bizonyíték kell; nem akarunk találgatás alapján túlméretezett crash rendszert építeni. |
| 2026-09-28 | A célverzió egyelőre `TBD`. | A terv dokumentálása nem bővítheti automatikusan az 1.0.0 scope-ját. |
| 2026-09-28 | Az első biztonságos diagnosztikai alap az 1.0.0 scope része lett. | A tulajdonos jóváhagyta a metaadat, `faulthandler` és izolált fatal-crash regresszió megvalósítását; natív dump nélkül. |
| 2026-09-28 | A build/commit azonosító, minidump/core dump és natív szimbólumozás nem része ennek az első alapnak. | Ezek külön infrastruktúrát és adatkezelési döntést igényelnek; az 1.0.0-ban a megbízható elsődleges bizonyíték a cél. |

## Megvalósítási napló

A biztonságos 1.0.0-s diagnosztikai szelet elkészült a `9502457` commitban.

- A launcher a lehető legkorábban bekapcsolja a Python `faulthandler` naplót.
- Kontrollált Python exception és natív fatal fault külön `failure_kind` értéket
  kap.
- Tiszta leálláskor az üres fatal-fault napló törlődik; valódi fatal folyamatleállás
  esetén megmarad.
- Az izolált regressziós teszt gyermekfolyamatban idéz elő valódi fatal faultot,
  ezért nem veszélyezteti a pytest vezérlőfolyamatát.
- Helyi eredmény: `595 passed`.
- A Windows csomagolt alkalmazás buildje, auditja és smoke tesztje zöld:
  [CI + Windows Release #36444349911](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/36444349911).
- A Linux csomagolt alkalmazás buildje, auditja és smoke tesztje zöld:
  [CI + Linux Build #36444350235](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/36444350235).

### Bizonyíték határa

A napló bizonyítja a folyamat platformját, környezetét, indulási fázisát és a
Python által még rögzíthető thread stackeket. Ebből gyakran behatárolható az
érintett Python/Qt workflow, de faulting natív modul vagy gyökérok nem
állapítható meg biztosan. Ehhez egy későbbi minidump/core dump és
release-szimbólum infrastruktúra szükséges.
