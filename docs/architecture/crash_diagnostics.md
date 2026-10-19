# Crash diagnostics

Az alkalmazás által írt diagnosztikai fájlok helyben, az executable melletti
`logs/` könyvtárba kerülnek; fejlesztői futtatáskor ez a repository `logs/`
mappája. Linuxon az operációs rendszer által kezelt core dump helye ettől
eltérhet. A fájlokat az alkalmazás nem tölti fel automatikusan.

## Fájltípusok

- `crash-*.log`: kezelt Python startup exception teljes tracebackkel.
- `diagnostic-buffer-*.tmp`: az alkalmazás futása közben előre megnyitott,
  `armed` állapotú diagnosztikai buffer. A jelenléte önmagában nem jelent
  összeomlást. Tiszta leálláskor törlődik; natív fatal fault esetén a Python
  `faulthandler` által még rögzíthető thread stackekkel együtt megmarad.
- `native-crash-*.log`: a Windows supervisor összefoglalója, benne az exception
  code és a hozzá tartozó dump neve.
- `native-*.dmp`: Windows minidump. Memóriarészleteket tartalmazhat, ezért
  érzékeny diagnosztikai adatként kezelendő.
- `fatal-*.log`: korábbi buildek diagnosztikai bufferneve; a jelenlegi launcher
  helyette `diagnostic-buffer-*.tmp` fájlt hoz létre.
- Az EXE-be ágyazott `build-info.json` tartalmazza a csomagolt build commitját,
  Git refjét, CI run ID-ját és UTC buildidejét. Nem jelenik meg külön fájlként
  a portable gyökérben; az adatai bekerülnek a crash logok metaadatai közé.

Minden összetartozó diagnosztikai buffer, summary és dump ugyanazt a `crash_id`
értéket
használja.

## Indítás és megőrzés

A repository gyökeréből `py -3.11 -m app.launcher` (Windows), illetve
`python3 -m app.launcher` (Linux, a projekt függőségeivel telepített Python)
indítja a diagnosztikai launchert. A `python -m app.main` közvetlenül a Qt
belépési pontot futtatja, így kihagyja a launcher korai importhiba- és
faulthandler-védelmét. A csomagolt alkalmazás belépési pontja a launcher.

A normál logger a konfigurált megőrzési időnél régebbi `.log` fájlokat
induláskor, best-effort módon törli; a kiadott konfigurációban ez 14 nap.
Ez a takarítás nem terjed ki a megmaradt `.tmp` bufferekre, `.dmp` fájlokra
vagy az operációs rendszer által kezelt core dumpokra. A diagnosztikai
fájlírás best-effort: például nem írható programkönyvtár esetén nem garantált,
hogy összeomlási fájl készül.

## Windows

A csomagolt Windows alkalmazás első folyamata egy minimális supervisor. A GUI-t
külön gyermekfolyamatban indítja a Windows Debug API alatt. Második esélyes,
nem kezelt natív exception esetén a supervisor a Microsoft `DbgHelp`
`MiniDumpWriteDump` függvényével készít dumpot, mielőtt a gyermekfolyamat
megszűnik. Ez követi azt az ajánlást, hogy az instabil célfolyamat helyett külön
folyamat írja a dumpot:

- [MiniDumpWriteDump dokumentáció](https://learn.microsoft.com/windows/win32/api/minidumpapiset/nf-minidumpapiset-minidumpwritedump)
- [Minidump files](https://learn.microsoft.com/windows/win32/debug/minidump-files)

A dump alapvető process/thread és moduladatokat tartalmaz, de elemzéséhez az
azonos build binárisa és az elérhető szimbólumok szükségesek. A faulting modul
önmagában nem bizonyítja a gyökérok tulajdonosát.

## Linux

Linux alatt a core dumpot a kernel és gyakran a `systemd-coredump` kezeli. Az
alkalmazás nem írja át a felhasználó `RLIMIT_CORE`, `core_pattern` vagy systemd
beállításait. A megmaradt diagnosztikai buffer rögzíti az aktuális soft/hard
core limitet és a
`/proc/sys/kernel/core_pattern` értékét.

Az adott felhasználó legutóbbi alkalmazás-crashének vizsgálata tipikusan:

```bash
coredumpctl list AkihabaraiScore
coredumpctl info AkihabaraiScore
coredumpctl dump AkihabaraiScore --output=AkihabaraiScore.core
```

Ha nincs systemd-coredump, a core fájl helyét és nevét a `core_pattern`, a
folyamat limitjei és a munkakönyvtár határozza meg. Részletek:

- [Linux core(5)](https://man7.org/linux/man-pages/man5/core.5.html)
- [coredumpctl](https://www.freedesktop.org/software/systemd/man/latest/coredumpctl.html)

## Elsődleges triage

A diagnosztikai kategória csak valószínű érintett réteget jelölhet:

- `own-python-code`
- `pyqt-or-qt`
- `graphics-or-platform-plugin`
- `operating-system-or-native-runtime`
- `native-unknown`
- `insufficient-evidence`

Minden automatikus kategóriához a
`likely_layer_only_not_root_cause` korlátozás tartozik. Gyökérok csak a log,
dump/core, pontos build és reprodukció együttes elemzéséből állapítható meg.

## Hibajelentés és adatvédelem

Első körben a normál logot, a megmaradt diagnosztikai buffert, a `native-crash`
summaryt és a reprodukciót érdemes megosztani. `.dmp` vagy Linux core csak
tudatosan adható át:
folyamatmemóriát, útvonalakat és futásidejű adatokat is tartalmazhat. A CI
mesterséges crash tesztje ezért a logokat és a riportot őrzi meg, a dumpot nem
tölti fel.
