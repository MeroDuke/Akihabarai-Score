# GPLv3 runtime compliance és tiszta portable csomag

- Plan ID: `PLAN-009`
- Status: `completed`
- Target release: `1.0.0`
- Type: `compliance`
- Priority: `high`
- Created: `2026-09-29`
- Last reviewed: `2026-09-29`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

A jelenlegi `onefile` desktop build mellett a Qt runtime licencútja még
feltételesként szerepel, miközben az alkalmazás, a PyQt6 binding és a teljes
kombináció GPLv3-kompatibilis irányt követ. A portable csomag emellett olyan
belső audit-, inventory-, provenance- és projektpolicy-fájlokat is átad a
felhasználónak, amelyekre a program futásához és a jogok megismeréséhez nincs
szüksége.

## Cél

- A `onefile` csomagolás megtartása mellett auditálható GPLv3 runtime-út.
- A pontos alkalmazás-, PyQt- és Qt-források azonosítható és ellenőrzött
  elérhetősége.
- Tiszta portable gyökér, egyetlen `legal/` fával a ténylegesen átadandó jogi
  anyagok számára.
- A belső megfelelőségi bizonyítékok megőrzése a repóban vagy CI-artifactként,
  nem a felhasználói programkönyvtárban.

## Nem cél

- `onedir` csomagolás vagy külön Qt runtime-könyvtár bevezetése.
- Kereskedelmi PyQt/Qt licenc beszerzése.
- UI-framework vagy binding cseréje.
- Brand- vagy creator-policy licencfeltétellé alakítása.

## Jelenlegi állapot

Az alkalmazás és a PyQt6 binding GPL-3.0-only. A lockolt PyQt6-Qt6 wheel
LGPLv3 licencszöveget tartalmaz; az LGPLv3 a GPLv3-ra épülő további engedély,
és GPLv3 alkalmazással GPLv3-kompatibilis kombinációt enged. A tag workflow-k
a pontos PyQt6, Qt Base és Qt Wayland forrásokat hash alapján ellenőrzik és a
release mellett elérhetővé teszik.

A csomag jelenleg külön `docs/` és `licenses/` fákat, valamint több gyökérszintű
compliance-fájlt tartalmaz. Az EXE-be ágyazott `build-info.json` mellett egy
második külső példány is bekerül.

## Tervezett megoldás

- Qt/PyQt runtime- és forráséletciklus auditdokumentum készül.
- A géppel olvasható compliance-státuszok a megvalósult állapotot tükrözik.
- A portable csomag kötelező jogi fájljai `legal/` alá kerülnek.
- Dependency licencek és tagelt Qt-attribúciók `legal/third-party/` alatt
  maradnak a bináris mellett.
- Belső SBOM, inventory, provenance, brand- és creator-dokumentum nem kerül a
  portable mappába; a workflow továbbra is előállítja vagy őrzi őket.
- A külső `build-info.json` megszűnik; az immutable build identity az EXE-be
  ágyazott példányból olvasható.

## Platform- és kompatibilitási szempontok

Windows és Linux azonos logikai layoutot kap. A Linux runtime-előfeltételek
felhasználói dokumentuma megmarad a `docs/` alatt. A csomagolt alkalmazás
indulása, a crash metadata és a tagelt forráskiadás nem változhat.

## Tesztstratégia

- Low-level tesztek a GPLv3 audit, compliance-státusz és portable validátor
  szerződésére.
- Workflow-szintű csomagolási teszt a Windows és Linux assembly lépésekre.
- Portable validátor fixture-rel a tiszta layout elfogadására és a régi
  gyökérszintű belső fájlok elutasítására.
- Helyi teljes pytest futtatás headless Qt módban.
- A kész csomagolt Windows és Linux smoke tesztje a CI-ben.

## Elfogadási feltételek

- [x] A Qt/PyQt GPLv3 runtime-út dokumentált és forráshivatkozásokkal igazolt.
- [x] A `runtime-components.json` nem jelez lezárt licenckonfliktust nyitottnak.
- [x] A portable gyökér nem tartalmaz belső SBOM-, inventory-, provenance-,
      brand-, creator- vagy külső build-info fájlt.
- [x] A szükséges licencek és source-availability információ a `legal/` alatt
      elérhető.
- [x] A releváns helyi tesztek sikeresek.
- [x] A teljes workflow/regressziós teszt helyben sikeres.
- [x] A releváns CI/CD workflow-k sikeresek.
- [x] A dokumentáció és a roadmap frissült.

## Kockázatok és visszaállítás

A layoutváltás törheti a validátort, a release archive listáját vagy jogi fájl
hivatkozásokat. Ezeket tesztek és tag-only validáció védik. Visszaállításkor a
korábbi `docs/`/`licenses/` layout visszatehető anélkül, hogy az alkalmazáskód
vagy a `onefile` build változna.

## Nyitott kérdések

- A tagelt release oldalán mely belső compliance-riportok maradjanak külön
  letölthető assetek a CI-artifact megőrzésén túl?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-09-29 | GPLv3 runtime-út és `onefile` build. | Az alkalmazás GPLv3, a felhasználói egy-EXE élmény elsődleges. |
| 2026-09-29 | A portable csomagból kikerülnek a belső auditanyagok. | A compliance-bizonyíték nem azonos a felhasználónak átadandó runtime-mal. |

## Megvalósítási napló

- `2026-09-29`: a Qt/PyQt GPLv3 runtime-audit, a géppel olvasható
  compliance-státuszok és a Windows/Linux workflow-k portable layoutja
  elkészült a `feature/license-compliance` ágon.
- `2026-09-29`: 609 pytest sikeresen lefutott headless Qt módban; a Markdown
  relatívlink-ellenőrzés 0 hibát talált.
- `2026-09-29`: valódi helyi Windows `onefile` binárisból, lockolt függőségi
  licencekből, SBOM-ból és natív inventoryból összeállított tiszta portable
  fixture sikeresen átment a release-validátoron.
- `2026-09-29`: implementációs commit: `ea0dbf8`.
- `2026-09-29`: a
  [Windows CI](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/36556660347)
  és a
  [Linux CI](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/36556660282)
  minden build-, audit-, portable-validációs, startup- és natív crash lépése
  sikeres lett.
