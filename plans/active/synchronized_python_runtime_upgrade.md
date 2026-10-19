# Szinkronizált Python runtime-frissítés

- Plan ID: `PLAN-011`
- Status: `accepted`
- Target release: `1.1.0`
- Type: `reliability`
- Priority: `medium`
- Created: `2026-09-29`
- Last reviewed: `2026-10-19`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

Az Akihabarai Score fejlesztői és CI baseline-ja Python 3.11.9. A fejlesztői
gépen Python 3.11 és 3.10 található. A kapcsolódó Akihabarai Könyvespolc
webprojekt Docker runtime-ja jelenleg Python 3.13 Alpine. A különböző
baseline-ok idővel növelik a kompatibilitási és karbantartási költséget.

Az `1.0.0` után mindkét projektet és a fejlesztői PC-t ugyanarra a bizonyított,
akkor legfrissebb stabil Python-vonalra kell frissíteni.

## Cél

- A Score CI, helyi fejlesztői környezet és csomagolt runtime egységesítése.
- A webprojekt Python runtime-jának összehangolt frissítése külön, saját
  repository-változtatásban.
- A fejlesztői gép Python-verziójának csak a projektkompatibilitás bizonyítása
  után történő frissítése.
- A PC alapértelmezett interpreterének, PATH-jának, launcherének, pipjének és
  VS Code környezeteinek összehangolása; a régi Pythonok végső eltávolítása.

## Nem cél

- Python prerelease használata.
- A Python frissítése az `1.0.0` előtt.
- Egy ma ismert patch-verzió előre történő beégetése.
- A régi helyi Python-verziók eltávolítása az új környezet bizonyítása előtt.

## Jelenlegi állapot és várható cél

2026. október 19-i ellenőrzés: a PC alapértelmezett Pythonja 3.11.9, mellette
3.10.5 is telepítve van. A Score CI-je pontosan 3.11.9-et és explicit Ubuntu
24.04-et használ. A webprojekt Docker-alapja digesttel rögzített
`python:3.13-alpine`, a Python CI-je 3.13; runnerjei `ubuntu-latest` címkét
használnak. A VM SSH-n nem volt elérhető, ezért a ténylegesen futó konténer
patch- és Alpine-verziója még ellenőrzendő.

A Python 3.10 támogatása 2026-10-01-én lejárt; a 3.11-é 2027 októberéig,
a 3.13-é 2029 októberéig tart. Az ág támogatása nem teszi naprakésszé a régi
3.11.9 javítóverziót. A Python 3.15.0 végleges kiadása 2026-10-09-én jelent
meg, majd körülbelül kéthavonta hibajavító kiadások várhatók:

- <https://devguide.python.org/versions/>
- <https://www.python.org/downloads/release/python-3119/>
- <https://peps.python.org/pep-0790/>

Az `1.0.0` 2026-10-19-én megjelent; tulajdonosi döntés alapján az `1.1.0`
tartalma ez a környezetfrissítés. A javasolt célablak 2026 december–2027 január,
nem merev kiadási határidő. A migráció várható célvonala
**Python 3.15 legfrissebb akkori stabil patch kiadása**. A pontos verziót a
végrehajtás napján kell kiválasztani; nem szabad most `3.15.0`-ra vagy egy
feltételezett patch-számra rögzíteni.

Az `ubuntu-latest` 26.04-re átirányítása 2026-10-19 és 2026-11-19 között
nem a 24.04 runner megszüntetése. Az Ubuntu 24.04 normál biztonsági támogatása
2029 májusáig tart; ez nem garantál azonos GitHub runner-élettartamot.

- <https://github.com/actions/runner-images/issues/14748>
- <https://ubuntu.com/about/release-cycle>

A PyInstaller 6.21.0 óta hivatalosan támogatja a Python 3.15-öt:
<https://pyinstaller.org/en/latest/CHANGES.html>

Ez szükséges, de nem elégséges bizonyíték: a lockolt PyQt6, Qt, sip,
teszteszközök és mindkét projekt összes runtime-függőségének kompatibilitását a
migrációkor külön ellenőrizni kell.

## Tervezett megoldás

1. A végrehajtáskor újra meghatározzuk a legfrissebb stabil CPython-kiadást és
   ellenőrizzük a függőségi támogatást.
2. Az új Pythont a PC-n először side-by-side telepítjük; a 3.11 környezet
   megmarad visszaállási pontnak.
3. Frissítjük és újrageneráljuk a Score dependency lockokat, SBOM-ot,
   provenance- és compliance-adatokat.
4. Lefuttatjuk a teljes helyi teszt-, build-, startup- és crash workflow-t.
5. A Score Windows CI-jét az új pontos verzióra, Linux CI-jét pedig az új
   pontos verzióval kompatibilis explicit Ubuntu 26.04 runnerre rögzítjük.
6. A webprojekt külön változtatásban ugyanarra a Python feature-vonalra és
   kompatibilis patchre áll át, beleértve a Docker base image digestjét.
7. Újralétrehozzuk az érintett virtuális környezeteket, beállítjuk a VS Code
   interpreterét és ellenőrizzük a `python`, `py`, `pip`, PATH és indítók
   feloldását új terminálból is.
8. Felmérjük a régi interpreterek más helyi fogyasztóit. Mindkét projekt és az
   érintett eszközök bizonyítása után eltávolítjuk a régi 3.10 és 3.11
   telepítéseket, majd ismét ellenőrizzük az indítást. A Debian host
   rendszer-Pythonját nem cseréljük: a webalkalmazás runtime-ja konténeres.

## Platform- és kompatibilitási szempontok

- Windows: python.org telepítő/launcher, PyQt és PyInstaller wheel-ek,
  Microsoft runtime provenance.
- Linux: GitHub runner, PyInstaller build, Qt rendszerkönyvtárak.
- Ubuntu 26.04-en buildelt bináris indítása a támogatott Linux referencia-
  környezetben; a magasabb build-baseline nem szűkítheti észrevétlenül a támogatást.
- Web: Alpine/musl wheel- és buildkompatibilitás, Docker image digest.
- A Score és a webprojekt összehangolt célvonalat kap, de külön repositoryban,
  külön teszt- és rollback-bizonyítékkal változik.

## Tesztstratégia

- Az összes unit, low-level és end-user workflow teszt az új interpreterrel.
- Windows és Linux PyInstaller build, native inventory és portable validáció.
- Csomagolt startup smoke és mesterséges natív crash workflow mindkét platformon.
- A webprojekt teljes backend tesztje és konténeres startup/healthcheck tesztje.
- Side-by-side helyi manuális indítás, mielőtt a gép alapértelmezett Pythonja
  megváltozik.

## Elfogadási feltételek

- [ ] A kiválasztott verzió a migráció napján stabil, nem prerelease Python.
- [ ] A Score összes közvetlen és csomagolt függősége támogatja.
- [ ] A Windows és Linux onefile build, startup és crash diagnosztika sikeres.
- [ ] A webprojekt kompatibilis runtime-ra frissült és saját CI-je zöld.
- [ ] A fejlesztői PC side-by-side frissítése és manuális ellenőrzése sikeres.
- [ ] A `python`, `py`, `pip`, VS Code és projektindítók az új környezetet használják.
- [ ] A régi helyi Pythonok fogyasztóit felmértük, a 3.10/3.11 eltávolítása után
  mindkét projekt és az érintett eszközök ellenőrzése sikeres.
- [ ] Az Ubuntu 26.04 CI és a csomagolt Linux build referencia-környezeti próbája sikeres.
- [ ] A releváns helyi tesztek sikeresek.
- [ ] A releváns CI/CD workflow-k sikeresek.
- [ ] A dokumentáció és a roadmap frissült.

## Kockázatok és visszaállítás

Hiányzó bináris wheel, PyInstaller hook-regresszió, Qt plugineltérés vagy Alpine
musl inkompatibilitás jelentkezhet. A 3.11-es Score és a webprojekt korábbi
Docker digestje visszaállási pont marad, amíg az új baseline mindkét projektben
nem bizonyított.

## Nyitott kérdések

- Pontosan melyik 3.15.x kiadás lesz stabil a végrehajtás napján?
- Azonos patch-verzió szükséges-e a desktop CI-ben és az Alpine image-ben, vagy
  elegendő az azonos 3.15 feature-vonal?
- Mikor változzon meg a PC `py` launcherének alapértelmezett interpretere?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-09-29 | A migráció csak az 1.0.0 után indul. | Az 1.0.0 stabil baseline-ját nem terheljük interpreterváltással. |
| 2026-09-29 | A várható cél Python 3.15 legfrissebb stabil patch kiadása. | 2027 tavaszán ez lesz a legfrissebb stabil feature-vonal; a patch-számot végrehajtáskor kell rögzíteni. |
| 2026-09-29 | A Score, a webprojekt és a PC összehangoltan, de bizonyítékvezérelten frissül. | A közös baseline csökkenti a környezeti eltérést, a külön rollback megőrzi a biztonságot. |
| 2026-10-07 | Az Ubuntu 26.04 Linux runnerre váltás ennek a tervnek a része lett. | Az image nem biztosítja a jelenlegi, rögzített Python 3.11.9-et; az 1.0.0 ezért explicit Ubuntu 24.04-en marad, a két baseline együtt frissül. |
| 2026-10-19 | A terv elfogadva az `1.1.0` tartalmaként. | A környezetkarbantartás megelőzi a tracinget; javasolt célablak 2026 december–2027 január. |
| 2026-10-19 | A PC eszközbekötése és a régi Pythonok végső eltávolítása a scope része. | Nem elég a repositoryk verziószámait átírni; működő és rendezett fejlesztői gép is szükséges. |

## Megvalósítási napló
Még nem indult el.
