# Determinisztikus mixed-DPI ablakindítás

- Plan ID: `PLAN-013`
- Status: `completed`
- Target release: `1.0.0`
- Type: `reliability`
- Priority: `high`
- Created: `2026-10-07`
- Last reviewed: `2026-10-07`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

Eltérő felbontású és Windows-skálázású monitorok mellett a főablak indulásakor
az egér másik monitorra mozgatása hibás képernyőválasztást és összetört Qt
layoutot eredményezhet. A jelenlegi bootstrap fix 1600×720-as méretet és
minimumot alkalmaz anélkül, hogy figyelembe venné a célképernyő Qt által
jelentett, logikai pixelekben mért használható területét.

## Cél

Az alkalmazás indulási képernyője és geometriája legyen determinisztikus,
férjen el a képernyő használható területén, és a napló tartalmazza a hiba
utólagos elemzéséhez szükséges monitor- és DPI-adatokat.

## Nem cél

- A teljes desktop UI reszponzív átalakítása 1600 logikai pixel alatti
  munkaterületre.
- Futás közben másik monitorra áthúzott ablak teljes layout-újratervezése.
- A Qt vagy az operációs rendszer high-DPI támogatásának kikapcsolása.

## Jelenlegi állapot

A `show_main_window()` a konfigurált alap- és minimumméretet közvetlenül
alkalmazza. Nem választ explicit képernyőt, nem korlátozza a méretet a
`QScreen.availableGeometry()` alapján, és nem naplózza a képernyők DPI-adatait.

## Tervezett megoldás

- A `QApplication` létrejötte után, a főablak előtt rögzítjük az elsődleges
  képernyőt indulási célként.
- Minden képernyő releváns geometriáját, logikai DPI-jét és pixelarányát
  naplózzuk.
- Az ablak alap- és minimumméretét a célképernyő használható geometriájához
  korlátozzuk, majd azon középre helyezzük.
- Ha képernyőadat nem érhető el, megőrizzük a korábbi indulási fallbacket.

## Platform- és kompatibilitási szempontok

A megoldás Qt publikus, platformfüggetlen képernyő API-ját használja. A jelentett
hiba Windows mixed-DPI környezetben jelentkezett, Linuxon pedig a meglévő
fallback és a Qt által közölt használható geometria marad az alap.

## Tesztstratégia

- Tiszta unit teszt a méret- és minimumméret-korlátozásra.
- Diagnosztikai teszt több, eltérő DPI-jű képernyő naplózására.
- Teljes bootstrap workflow/regressziós teszt, amely a felhasználói főablak
  létrehozásától a megjelenítésig ellenőrzi a rögzített képernyő használatát.
- Qt-tesztek helyben `QT_QPA_PLATFORM=offscreen` módban.
- Manuális Windows mixed-DPI ellenőrzés a closed beta környezetben.

## Elfogadási feltételek

- [x] Az egér helyzete nem változtatja meg az indulási képernyőt a bootstrap
  közben.
- [x] A kért ablak- és minimumméret nem nagyobb a célképernyő használható
  logikai méreténél.
- [x] A napló az összes képernyő geometriáját, DPI-jét, pixelarányát és az
  elsődleges képernyő jelölését tartalmazza.
- [x] Képernyőadat nélküli környezetben a korábbi indulási fallback működik.
- [x] A releváns helyi tesztek sikeresek.
- [x] A teljes workflow/regressziós teszt helyben sikeres.
- [x] A releváns CI/CD workflow-k sikeresek.
- [x] A dokumentáció és a roadmap frissült.

## Kockázatok és visszaállítás

Kisebb munkaterületen a teljes UI továbbra is zsúfolt lehet; ezt a változtatás
nem állítja be reszponzív támogatásként. Regresszió esetén az új bootstrap
geometriakezelés önállóan visszaállítható, a diagnosztikai napló megtartható.

## Nyitott kérdések

- Szükséges-e egy későbbi QoL release-ben valódi, 1600 logikai pixel alatti
  reszponzív vagy görgethető desktop layout?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-10-07 | Az elsődleges képernyő az indulási cél. | Determinisztikus, az egérmozgástól független startup szükséges. |
| 2026-10-07 | A célzott stabilizáció az 1.0.0 része. | Closed beta alatt talált, felhasználói UI-t összetörő regresszió. |

## Megvalósítási napló

Branch: `feature/license-compliance`.

- A bootstrap az elsődleges képernyőt a főablak létrehozása előtt rögzíti.
- A méretet, minimumméretet és pozíciót a célképernyő használható logikai
  geometriájából számítja.
- Helyi ellenőrzés: `QT_QPA_PLATFORM=offscreen python -m pytest -q` —
  617 sikeres teszt.
- Implementációs commit: `dd60b9d` (`fix: stabilize mixed-DPI window startup`).
- CI: [Linux build](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/37655348473)
  és [Windows build](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/37655348461)
  sikeres, beleértve a csomagolt startup smoke és natív crash ellenőrzéseket.
- A valódi, eltérő skálázású fizikai monitorokon történő reprodukció a
  felhasználói kézi ellenőrzés része marad.
