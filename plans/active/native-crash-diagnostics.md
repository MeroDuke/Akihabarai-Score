# Natív crash-diagnosztikai alap

- Plan ID: `PLAN-001`
- Status: `proposed`
- Target release: `TBD`
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
- Az 1.0.0 release scope-jának automatikus bővítése.

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

## Előzetes elfogadási feltételek

- [ ] A target release tulajdonosi jóváhagyást kapott.
- [ ] A Python és natív crash diagnosztikai kimenete egyértelműen elkülönül.
- [ ] A kimenet azonosítja az alkalmazás és a build verzióját.
- [ ] Windows és Linux mesterséges natív crash regressziós teszt rendelkezésre áll.
- [ ] A CI sikertelen, ha a csomagolt alkalmazás váratlanul összeomlik.
- [ ] A keletkezett diagnosztikai artifact megmarad a sikertelen CI futásban.
- [ ] Dokumentált, hogy mely következtetések bizonyítottak és melyek csak
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

- Melyik release legyen a célverzió?
- Az első iteráció csak `faulthandler` legyen, vagy tartalmazzon natív dumpot is?
- Hol és mennyi ideig őrizzük meg a release-szimbólumokat?
- A felhasználói gépen készült dump manuálisan kerüljön-e hibajelentéshez?
- Milyen adatvédelmi figyelmeztetés szükséges egy dump megosztásához?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-09-28 | Külön terv készül a natív crash-diagnosztikáról. | Előbb diagnosztikai alap és bizonyíték kell; nem akarunk találgatás alapján túlméretezett crash rendszert építeni. |
| 2026-09-28 | A célverzió egyelőre `TBD`. | A terv dokumentálása nem bővítheti automatikusan az 1.0.0 scope-ját. |

## Megvalósítási napló

A megvalósítás még nem kezdődött el.
