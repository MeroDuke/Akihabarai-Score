# Linux CI runner migráció

- Plan ID: `PLAN-010`
- Status: `proposed`
- Target release: `TBD`
- Type: `reliability`
- Priority: `low`
- Created: `2026-09-29`
- Last reviewed: `2026-09-29`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

A GitHub Actions jelezte, hogy az `ubuntu-latest` címke 2026. október 19-től
Ubuntu 26-ra migrál. A lebegő runner-címke emiatt a projekt változtatása nélkül
is lecserélheti a Linux build operációs rendszerét, csomagkészletét és natív
runtime-környezetét.

Upstream követés:
<https://github.com/actions/runner-images/issues/14748>

Ez nem része az `1.0.0` scope-jának. A jelenlegi Linux build működik, ezért a
feladat alacsony prioritású, 1.0.0 utáni karbantartás.

## Cél

- A Linux CI ne észrevétlenül, egy lebegő címke átállása miatt migráljon.
- A támogatott runner-verzió és Linux runtime-baseline tudatos döntés legyen.
- Ubuntu 26 használata csak teljes build-, smoke-, crash- és portable
  validáció után váljon alapértelmezetté.

## Nem cél

- Az `1.0.0` kiadás blokkolása.
- Ubuntu 26 támogatásának előzetes kijelentése bizonyító CI-futás nélkül.
- Az alkalmazás Linux-disztribúciós támogatási körének automatikus bővítése.

## Jelenlegi állapot

A Linux workflow `ubuntu-latest` runnert használ, és külön rögzíti az Ubuntu
24.04 runtime-csomaglistát. A csomagolt alkalmazás buildje, natív inventoryja,
startup smoke tesztje, mesterséges natív crash tesztje és portable TAR
validációja CI-ben fut.

## Tervezett megoldás

1. Az aktuális workflow-t ideiglenesen explicit támogatott Ubuntu runnerre
   rögzítjük.
2. Külön migrációs próbában lefuttatjuk a teljes workflow-t Ubuntu 26-on.
3. Felülvizsgáljuk az APT runtime-csomaglistát és a Linux dokumentációt.
4. Csak zöld bizonyíték után állítjuk át a támogatott baseline-t.

## Platform- és kompatibilitási szempontok

A változtatás csak a Linux CI- és csomagolási környezetet érinti. A Windows
build és a desktop alkalmazás funkcionális viselkedése nem változhat.

## Tesztstratégia

- Workflow-szerződés teszt az explicit runnerre és csomaglistára.
- Teljes pytest futtatás headless Qt módban.
- Linux PyInstaller build és natív inventory.
- Csomagolt startup smoke és mesterséges natív crash workflow.
- Portable layout és TAR gyökérstruktúra validáció.

## Elfogadási feltételek

- [ ] A támogatott Linux runner nincs nem szándékosan lebegő címkéhez kötve.
- [ ] Az Ubuntu 26 runtime-csomaglista dokumentált és ellenőrzött.
- [ ] A Linux csomagolt startup és natív crash regresszió sikeres.
- [ ] A releváns helyi tesztek sikeresek.
- [ ] A releváns CI/CD workflow-k sikeresek.
- [ ] A dokumentáció és a roadmap frissült.

## Kockázatok és visszaállítás

Qt platformplugin-, rendszerkönyvtár- vagy csomagnév-változás törheti a buildet
vagy az indulást. Sikertelen migráció esetén a workflow az utolsó bizonyított,
explicit Ubuntu runneren marad.

## Nyitott kérdések

- Melyik explicit GitHub-hosted Ubuntu runner lesz még elérhető a végrehajtás
  időpontjában?
- Ubuntu 26 legyen-e új támogatott baseline, vagy csak CI-kompatibilitási cél?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-09-29 | A migráció 1.0.0 utáni, alacsony prioritású tétel. | A jelenlegi build működik; a runner-váltás nem indokol release-scope bővítést. |

## Megvalósítási napló
Még nem indult el.
