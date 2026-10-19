# Linux CI runner baseline-rögzítés és 26.04 felmérés

- Plan ID: `PLAN-010`
- Status: `completed`
- Target release: `1.0.0`
- Type: `reliability`
- Priority: `high`
- Created: `2026-09-29`
- Last reviewed: `2026-10-07`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

A GitHub Actions jelezte, hogy az `ubuntu-latest` címke 2026. október 19-től
Ubuntu 26-ra migrál. A lebegő runner-címke emiatt a projekt változtatása nélkül
is lecserélheti a Linux build operációs rendszerét, csomagkészletét és natív
runtime-környezetét.

Upstream követés:
<https://github.com/actions/runner-images/issues/14748>

A migráció 2026. október 19-én indul, miközben az 1.0.0 stabilizációja még
folyamatban van. A lebegő címke meghagyása így már közvetlen release-kockázat;
a tulajdonos ezért a feladatot az `1.0.0` scope-jába emelte.

## Cél

- A Linux CI ne észrevétlenül, egy lebegő címke átállása miatt migráljon.
- A támogatott runner-verzió és Linux runtime-baseline tudatos döntés legyen.
- Ubuntu 26 használata csak teljes build-, smoke-, crash- és portable
  validáció után váljon alapértelmezetté.

## Nem cél

- Ubuntu 26 támogatásának előzetes kijelentése bizonyító CI-futás nélkül.
- Az alkalmazás Linux-disztribúciós támogatási körének automatikus bővítése.

## Jelenlegi állapot

A Linux workflow `ubuntu-latest` runnert használ, és külön rögzíti az Ubuntu
24.04 runtime-csomaglistát. A csomagolt alkalmazás buildje, natív inventoryja,
startup smoke tesztje, mesterséges natív crash tesztje és portable TAR
validációja CI-ben fut.

## Tervezett megoldás

1. Az 1.0.0 workflow-ját explicit `ubuntu-24.04` runnerre rögzítjük, hogy ne
   sodródjon át automatikusan az új image-re.
2. Külön migrációs próbában ellenőrizzük az `ubuntu-26.04` runnert.
3. Lefuttatjuk a teljes teszt-, build-, natív inventory-, startup smoke-,
   crash- és portable-validációs workflow-t.
4. A 26.04 baseline csak a Python-baseline kompatibilis frissítése és zöld
   bizonyíték után válthatja le a 24.04-et.

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

- [x] A támogatott Linux runner nincs nem szándékosan lebegő címkéhez kötve.
- [x] Az 1.0.0 Ubuntu 24.04 runtime-csomaglistája dokumentált és ellenőrzött.
- [x] Az Ubuntu 26.04 migráció Python 3.11.9 kompatibilitási akadálya rögzített,
  és a folytatás a szinkronizált Python-frissítéshez kapcsolódik.
- [x] A Linux csomagolt startup és natív crash regresszió sikeres.
- [x] A releváns helyi tesztek sikeresek.
- [x] A releváns CI/CD workflow-k sikeresek.
- [x] A dokumentáció és a roadmap frissült.

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
| 2026-09-29 | A migráció 1.0.0 utáni, alacsony prioritású tétel. | A jelenlegi build működött; a runner-váltás akkor még nem indokolt release-scope bővítést. |
| 2026-10-07 | A migráció az 1.0.0 scope-jába került és megkezdődött. | Az automatikus rollout október 19-én indul; a lebegő baseline nagyobb kockázat, mint a most végigvalidált explicit átállás. |
| 2026-10-07 | Az 1.0.0 explicit Ubuntu 24.04-en marad. | Az Ubuntu 26.04 runneren a `setup-python` nem biztosítja a rögzített Python 3.11.9-et; a Python-baseline önálló, 1.0.0 utáni szinkronizált fejlesztés. |

## Megvalósítási napló

Branch: `feature/license-compliance`.

- A célzott 1.0.0 runner-label `ubuntu-24.04`; a lebegő `ubuntu-latest`
  megszűnik.
- Az első `ubuntu-26.04` próba a `setup-python` lépésben igazolta, hogy a
  rögzített Python 3.11.9 nem érhető el ezen az image-en; alkalmazáskód nem
  futott le.
- Helyi ellenőrzés: `QT_QPA_PLATFORM=offscreen python -m pytest -q` —
  618 sikeres teszt.
- Sikertelen 26.04 kompatibilitási próba: commit `34ad407`,
  [CI futás](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/37656127350).
- Elfogadott 1.0.0 megoldás: commit `3dbff2c`, explicit `ubuntu-24.04` runner;
  [teljes Linux CI](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/37656512883)
  sikeres.
