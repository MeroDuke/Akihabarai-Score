# Natív crash-diagnosztika – platformbizonyíték

- Plan ID: `PLAN-004`
- Status: `completed`
- Target release: `1.0.0`
- Type: `reliability`
- Priority: `high`
- Created: `2026-09-28`
- Last reviewed: `2026-09-28`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

Az első diagnosztikai alap megőrzi a Python thread stackeket fatal fault esetén,
de nem rögzíti a konkrét buildet, Windows alatt nem készít natív dumpot, Linux
alatt pedig nem mutatja meg, hogy a kernel vagy a systemd milyen core dump
mechanizmust alkalmazott.

## Cél

- A release build egyértelmű azonosítása commit és CI-adatokkal.
- Windows alatt best-effort minidump készítése natív, nem kezelt kivételnél.
- Linux alatt a core dump feltételeinek rögzítése és reprodukálható begyűjtési
  workflow dokumentálása.
- Bizonyítékalapú elsődleges triage, automatikus gyökérok-állítás nélkül.

## Nem cél

- Dumpok automatikus feltöltése.
- Felhasználói rendszerbeállítások vagy registry tartós átírása.
- A faulting modul automatikus hibáztatása.
- Qt-, Python- vagy operációsrendszer-szimbólumok újradisztribúciója.

## Jelenlegi állapot

A [`PLAN-001`](../completed/native-crash-diagnostics.md) alapján a launcher már
elkülöníti a Python exception és fatal fault kimenetet, valamint Windows és
Linux CI-ben izolált valódi fatal-fault regresszió fut.

## Tervezett megoldás

- Generált és a PyInstaller csomagba ágyazott `build-info.json`.
- Külön, standard-library/`ctypes` alapú natív diagnosztikai komponens.
- Windows `MiniDumpWriteDump` alapú best-effort dump, minimális dump-típussal.
- Linux `RLIMIT_CORE` és `/proc/sys/kernel/core_pattern` állapot naplózása;
  a program nem írja át ezeket.
- Determinisztikusan tesztelhető triage és adatvédelmi útmutató.

## Platform- és kompatibilitási szempontok

Windows alatt a csomagolt alkalmazás külön supervisor folyamatból figyeli a
GUI-folyamatot, és második esélyes natív exception esetén onnan készít dumpot.
Linux alatt a core fájl tulajdonosa a kernel/systemd; az alkalmazás csak a
konfigurációt rögzíti és nem kér emelt jogosultságot.

## Tesztstratégia

- Buildmetaadat generálás és betöltés unit tesztekkel.
- Natív diagnosztikai metaadat és triage low-level tesztekkel.
- Izolált gyermekfolyamatos fatal-fault workflow regresszió.
- Windows CI-n valódi `.dmp` létrejöttének ellenőrzése.
- Linux CI-n core-konfiguráció és signal-kimenet ellenőrzése.
- Teljes csomagolt Windows és Linux smoke teszt.

## Elfogadási feltételek

- [x] A csomagolt build logja commit- és CI-azonosítót tartalmaz.
- [x] Windows natív fault esetén best-effort `.dmp` és fatal log készül.
- [x] Linux fatal log rögzíti a core limitet és a core handlert/patternt.
- [x] A triage kategória bizonyítékot és korlátot is közöl.
- [x] A dump adatvédelmi és manuális elemzési workflow dokumentált.
- [x] A releváns helyi tesztek sikeresek.
- [x] A teljes workflow/regressziós teszt helyben sikeres.
- [x] A releváns CI/CD workflow-k sikeresek.
- [x] A dokumentáció és a roadmap frissült.

## Kockázatok és visszaállítás

A Windows supervisor dumpírása is best-effort; ezért nem helyettesíti a fatal
logot, és hibája nem fedheti el az eredeti crash-t. A dump memóriatartalma
érzékeny lehet, ezért kizárólag helyben marad. A funkció külön komponensből
letiltható az alkalmazás működésének módosítása nélkül.

## Nyitott kérdések

- Hol őrizzük meg hosszú távon a saját release binárisokat és build inventoryt?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-09-28 | A második lépcső célverziója `1.0.0`. | A tulajdonos a korábban elhalasztott teljes natív diagnosztikai scope folytatását jóváhagyta. |
| 2026-09-28 | Nincs automatikus dumpfeltöltés vagy rendszerkonfiguráció-módosítás. | Adatvédelmi és platformbiztonsági határ. |
| 2026-09-28 | Windows alatt külön debug supervisor készíti a minidumpot. | Az in-process Python exception filter valódi crash-próbán nem készített dumpot; a külön folyamat megbízhatóbb és megfelel a Microsoft ajánlásának. |

## Megvalósítási napló

Branch: `feature/1.0.0/native-crash-diagnostics`.

Implementáció: `f26758b`, CI-kompatibilitási javítás: `6baf79e`.

Sikeres ellenőrzések:

- helyi headless regresszió: 607 teszt;
- Linux CI: [run 36474522205](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/36474522205);
- Windows CI: [run 36474522210](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/36474522210).
