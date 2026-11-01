# Csomagolt indulás mérése és gyorsítása

- Plan ID: `PLAN-021`
- Status: `in-progress`
- Target release: `1.0.1`
- Type: `reliability`
- Priority: `high`
- Created: `2026-11-01`
- Last reviewed: `2026-11-01`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

A Windows startup smoke két külön futásban elérte a 15 másodperces határt
(`41306299670`, `41306972541`). A process futott, a napló az ablakgeometria
beállításánál ért véget, crash-log nélkül. Egy újrafuttatás sikeres volt, így
a jelenség nem minden indulásnál jelentkezik. A pontos gyökérok még ismeretlen.

## Cél

Az indulás szakaszainak mérhetővé tétele, az igazolt szűk keresztmetszet
csökkentése, sikeres Windows/Linux csomagolt startup, a crash-védelem megtartásával.

## Nem cél

Vakon emelt timeout, crash-supervisor kikapcsolása, új csomagformátum vagy
onefile → onedir átállás, illetve a readiness-jelzés előrehozása a megjelenítés elé.

## Jelenlegi állapot

Helyi Python/offscreen mérés: Qt-import 0,037 s; app-importtal együtt 0,401 s;
ablak felépítve 0,504 s; megjelenítve 0,510 s. Ez nem csomagolt/natív Windows
benchmark, és nem cáfolja a CI-hibát. A onefile bootloader és a Windows
crash-supervisor is része a valódi indítási útvonalnak.

## Tervezett megoldás

Először kumulatív startup-szakaszidők és a smoke timeout előtti, opt-in
faulthandler stack-pillanatkép. Ezután az igazolt ok célzott optimalizálása;
a csomagolási szerződés és a felhasználó által elfogadott UI nem változhat.

## Platform- és kompatibilitási szempontok

Windows elsődleges, Linux regresszió kötelező. A normál indulás nem kapcsol
be watchdogot. A CI watchdog nem állítja le a processt, csak stack-et ír a
meglévő diagnosztikai pufferbe; a smoke readiness-kapu változatlan.

## Tesztstratégia

Unit teszt időmérésre és watchdog élesítés/leállításra; izolált subprocess
lassú indulási workflow, hálózat nélkül; teljes helyi offscreen regresszió;
Windows/Linux csomagolt startup és natív crash-CI. Előtte/utána mérések alapján
értékeljük a gyorsítást, nem kizárólag egy zöld újrafuttatásból.

## Elfogadási feltételek

- [ ] Az igazolt szűk keresztmetszet és előtte/utána adatok rögzítve.
- [ ] A readiness továbbra is a megjelenítés után történik.
- [ ] A watchdog csak smoke/explicit diagnosztikában aktív, nem okoz crasht.
- [ ] Helyi low-level és teljes workflow/regresszió sikeres.
- [ ] Windows/Linux csomagolt és natív crash-CI sikeres.
- [ ] Dokumentáció és roadmap frissült.

## Kockázatok és visszaállítás

Mérés önmagában nem gyorsítás. Ne keverjük a runner-, hálózati és alkalmazás-
költséget. A módosítás külön fix-ágon, önálló commitokkal visszavonható.

## Nyitott kérdések

Melyik stack-frame és indulási szakasz okozza a CI-n látható hosszú várakozást?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-11-01 | A tulajdonos startup-gyorsítást kér az 1.0.1 lezárása előtt. | Visszatérő Windows startup-timeout; a release még nem kiadáskész. |

## Megvalósítási napló

Ág: `fix/1.0.1/startup-performance`, a `release/1.0.1` állapotából.
Első lépés: szakaszmérés és timeout előtti stack, a 15 s kapu megtartásával.

- Mérési commit: `ccea6ee`, **650 helyi teszt sikeres**, beleértve a lassú
  indulás izolált stack-rögzítését is. Mindkét csomagolt és natív crash-CI zöld:
  [Windows](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41307643861),
  [Linux](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41307643779).
- Windows csomagolt mérés: teljes smoke **6,656 s**; QApplication kumulatív
  **119,2 ms**, ablak felépítve **752,8 ms**, ablak megjelenítve **4598,6 ms**.
  A konstrukció utáni megjelenítési szakasz tehát kb. **3845,8 ms**.
- Linux csomagolt mérés: QApplication **1,7 ms**, konstrukcióval együtt
  **57,2 ms**, megjelenítéssel együtt **62,4 ms**. Eltérő OS/runner/backend,
  ezért ez nem kontrollált teljesítmény-összehasonlítás.
- Helyi offscreen Python A/B: normál alfolyamat **0,513 s**, Windows
  crash-supervisorral **0,629 s**. Nem a csomagolt, natív GUI-s útvonal;
  nem bizonyítja, hogy a supervisor ott sem befolyásoló tényező.
- A mostani Windows-futásban nem állt elő a timeout, stack-watchdog sem sült el.
  **Optimalizációs eredmény még nincs igazolva**, a terv és a fix-ág nyitott;
  a release-be nem integráltuk a mérési változtatást. Következő vizsgálati pont
  a natív Windows megjelenítés hosszú szakasza, lehetőleg lassú futás stackjével.
