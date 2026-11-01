# Release-letöltések, grafikon és README-jelvények

- Plan ID: `PLAN-017`
- Status: `in-progress`
- Target release: `1.0.1`
- Type: `reliability`
- Priority: `medium`
- Created: `2026-10-19`
- Last reviewed: `2026-11-01`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

A GitHub release assetenként összesített `download_count` értéket ad, de a
korábbi napi alakulás ebből utólag nem rekonstruálható. A repository forgalmi
és klónozási statisztikája nem a csomagok letöltésszáma.

## Cél

Napi pillanatképek és verziónkénti/platformonkénti grafikon GitHub-oldali
adatokból, az alkalmazás módosítása és használati telemetria nélkül.
Emellett rövid, felhasználóközpontú README-jelvénysor a kiadásról,
támogatásról és letöltésekről.

## Nem cél

- Egyedi emberek, telepítések vagy aktív felhasználók mérése.
- Visszamenőleges napi számok kitalálása.
- Az AS runtime-jának, csomagjának vagy hálózati működésének módosítása.

## Jelenlegi állapot

2026-10-19-én egyszeri, lapozott GitHub API-lekérdezés készült. Az alkalmazás-
csomagok számai: v0.21.0 Windows/Linux 0/0; v0.22.0 0/0; v0.23.0 4/2;
v1.0.0 2/1. A v1.0.0 három külön függőségforrás-assetje egyenként 1 letöltést
mutatott; ezek nem alkalmazásletöltések, ezért a grafikonból kimaradtak.
Saját tesztek és automatizált lekérések is szerepelhetnek a számlálóban.

Forrás: `gh api --paginate repos/MeroDuke/Akihabarai-Score/releases`;
[GitHub asset API](https://docs.github.com/en/rest/releases/assets).
Az egyszeri pillanatkép nem jelenti a napi gyűjtés megkezdését.

## Tervezett megoldás

- Ütemezett napi és kézzel indítható GitHub Actions workflow, alkalmazáson kívül.
- Lapozott release/asset lekérdezés, UTC lekérdezési idővel, release- és
  assetazonosítóval, névvel, platformmal és összesített letöltésszámmal.
- Alkalmazáscsomagok és compliance/függőségforrás assetek külön kezelése.
- Tartós pillanatkép-tárolás a külön `metrics/downloads` adatágon, ugyanott
  újragenerálható SVG-grafikonnal és jelentéssel. Ne függjön a normál
  release-only build-artifact retentiontől, ne hozzon létre release-t.
- Azonos nap újrafuttatása, hiányzó nap, asset törlés/újrafeltöltés és számláló-
  csökkenés explicit kezelése; nem változtatunk negatív eltérést csendben nullává.
- Minimális jogosultság, titok nem kerül az adatokba vagy logba.

### README-jelvények

- Aktuális stabil release, a letöltési oldalra mutatva.
- Windows támogatott és Linux kísérleti státusz, nem azonos támogatási szintet sugallva.
- HU/EN felület és pontos `GPL-3.0-only` licenc, releváns hivatkozásokkal.
- Windows- és Linux-csomagok külön letöltésszáma; függőségforrások nem számítanak
  alkalmazásletöltésnek. Minden jelenleg elérhető stabil release alkalmazás-
  assetjeit összesítjük; a mérési dátum a jelvény címkéjében szerepel.
- Opcionális Windows/Linux CI-jelvény explicit `main` ágra rögzítve;
  a végleges jelvénysor implementációkor tulajdonosi review-t kap.
- Nem állítunk egyedi felhasználószámot, hibamentességet vagy igazolatlan
  tesztlefedettséget; nem vezetünk be pusztán dísznek technikai jelvényeket.
- Dinamikus értékek ne igényeljenek minden release-nél kézi számátírást.
  API/szolgáltatáshibánál ne jelenjen meg megtévesztő nulla vagy sikerjelzés.

Kiinduló források:
[GitHub workflow-jelvények](https://docs.github.com/en/actions/how-tos/monitor-workflows/add-a-status-badge),
[Shields.io](https://github.com/badges/shields).
A szokásos all-assets összesítő önmagában nem megfelelő a csomagszűréshez.

## Platform- és kompatibilitási szempontok

GitHub-infrastruktúra, Windows/Linux runtime-tól függetlenül. A workflow
hibája ne blokkolja az alkalmazás használatát vagy a kiadást. A későbbi
implementáció a `release/1.0.1` ágból nyitott
`feature/1.0.1/download-metrics` ágon készül. A release ág tartalmazza a korábbi
`1.0.1/result-table-layout` teljes, elfogadott javítását is.

## Tesztstratégia

- Mock API-val lapozás, csomagszűrés, összesítés és idősor-eltérések unit tesztje.
- Teljes automatizált workflow: fixture release-ekből napi tárolt adatsor és
  helyesen feliratozott grafikon; újrafuttatás és hiba utáni helyreállás.
- API-hibánál ne írjunk nulla letöltésű hamis mintát és ne sértsük az előzményeket.
- Helyi zöld tesztek után CI és kézi workflow-próba; grafikon vizuális ellenőrzése.
- A csomagszűrés közös tesztelése a badge-adatokkal; README-képek és célhivatkozások
  ellenőrzése, vizuális próba GitHubon világos és sötét témával.

## Elfogadási feltételek

- [ ] Napi és kézi futás működik, tartós és idempotens mintatárolással.
- [x] A grafikon verzió és platform szerint az alkalmazáscsomagokat mutatja.
- [x] A lekérdezési idő, hiányok és korlátok egyértelműen láthatók.
- [x] Lapozás, hibakezelés és assetcsere helyesen kezelt és tesztelt.
- [x] A teljes adatgyűjtés–tárolás–grafikon workflow helyben és CI-ben zöld.
- [x] Az alkalmazás és a release-only csomagmegőrzés nem változik.
- [x] A jóváhagyott README-jelvények működnek, a letöltések csak AS-csomagokat
  számolnak; platformstátusz, licenc, frissesség és kattintási cél egyértelmű.
- [x] A dokumentáció és a roadmap frissült.

## Kockázatok és visszaállítás

API-limit, jogosultsági hiba, megszakadt ütemezés vagy újrafeltöltött asset
félrevezető görbét okozhat. Stabil azonosítók és az eredeti minták megőrzése
szükséges. A workflow letiltható az alkalmazás érintése és az előzmények törlése nélkül.

## Nyitott kérdések

- A jelvénysor és a külön statisztikai oldal tulajdonosi elfogadása kész.
  Kizárólag a main-integráció utáni éles workflow-írási/ismétlési próba maradt;
  emiatt a terv az üzembehelyezésig `in-progress`, nem zárjuk le hamisan.
  Új alkalmazásrelease-t nem készít az adatgyűjtő.

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-10-19 | A napi gyűjtés és grafikon az `1.1.0` elfogadott kísérő eleme. | A tulajdonos most egyszeri lekérdezést kért, az automatizálást későbbre ütemezte. |
| 2026-10-19 | A README badge-rendszere is az `1.1.0` része. | A tulajdonos a release-, platform-, nyelv-, licenc- és letöltésjelzések betervezését kérte; a végleges összeállítás review-t kap. |
| 2026-11-01 | Áthelyezve az `1.0.1` scope-jába, implementáció engedélyezve. | Tulajdonosi kérés; a release most a layout-javítást és a GitHub-oldali metrikákat tartalmazza. |
| 2026-11-01 | Külön adatág, napi 05:17 UTC, első sikeres napi minta, Shields endpoint jelvények. | Nincs automata main-commit, telemetria, lejáró artifact vagy napi duplikáció. A jelvények az összes jelenlegi stabil alkalmazás-assetet számolják; CI-jelvény egyelőre nem kerül a sorba. |

## Megvalósítási napló

- Stdlib Python CLI: `scripts/release_download_metrics.py`, külön GitHub Actions
  workflow-val; a desktop kódja és függőségei nem változnak.
- A workflow mainen napi ütemezéssel, kézzel és a releváns main push után fut.
  Feature/PR/release ágon csak offline fixture-tesztek futnak. Éles adatágat
  automatán kizárólag a main gyűjtőjobja írhat, explicit célra és force-push nélkül.
  Az első minta külön, ellenőrzött kézi bootstrapként is publikálható.
- 15 automatizált eset: szűrés, lapozás, külön asset-végpont, API-hiba,
  assetcsere, számlálócsökkenés, napi idempotencia, hiányzó nap, SVG-escaping,
  valamint teljes subprocess CLI → history → grafikon → jelvény workflow.
- Részletes üzemeltetés: [letöltési metrikák](../../docs/integrations/release_download_metrics.md).
- Helyi és CI-validáció, valós lekérdezés és vizuális átvétel eredménye a
  következő bejegyzésekben rögzítendő; a terv még nem lezárt.
- Helyi teljes regresszió: **648 passed**, ebből 15 metrikaeset. A CLI-vel
  végzett valós, csak API-metaadatot olvasó próba 2026-11-01-én 6 Windows- és
  3 Linux-letöltést mutatott (v0.23.0: 4/2, v1.0.0: 2/1, korábbiak: 0/0).
  A helyi jelentés a figyelmen kívül hagyott `build/download-metrics-preview/`
  könyvtárban van; nem írja az éles adatágat. Az SVG helyben renderelve ellenőrzött.
- A verzió/tag konzisztencia-validáció, helyi Markdown-linkek és diff-ellenőrzés
  sikeres. A feature-CI és a main utáni éles adatág/jelvény-próba még hátravan.
- A `9e26598` feature-commit mindhárom CI-je sikeres:
  [metrika](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41305768620),
  [Windows](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41305768517),
  [Linux](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41305768606).
- `2026-11-01`: a tulajdonos a működő állapot felé történő továbblépést kérte.
  Ellenőrzött kézi bootstrap publikálta az első valós mintát a külön adatágra
  (`metrics/downloads`, `b0d48a5`), main-merge és alkalmazásrelease nélkül.
  Mindkét raw JSON és Shields végpont ellenőrzött: Windows 6, Linux 3, UTC-dátummal.
  A valós adatkönyvtár ugyanazon napi újrafuttatása változatlan, nincs új commit.
  A jelvények már élnek; az automata main-workflow írási/ütemezési próbája és
  a tulajdonosi vizuális elfogadás továbbra is hátravan.
- `2026-11-01`: a tulajdonos a jelvények és a külön statisztikai oldal
  megjelenését elfogadta, majd jóváhagyta a feature integrálását a
  `release/1.0.1` ágba. A feature oda integrálva; main-merge és tag nem készült.
- A `07e0829` dokumentációs commit Linux-CI-je sikeres. A Windows-futás első
  próbáján a csomagolt EXE elindult, crash-log nem keletkezett, de a readiness
  visszajelzés nem érkezett meg a 15 másodperces határig. Ugyanazon commit
  kézi újrafuttatása teljesen sikeres, időkorlát- vagy kódmódosítás nélkül:
  [Windows, attempt 2](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41306299670/attempts/2),
  [Linux](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41306299661).
  Az egyszeri timeout pontos kiváltó oka nem bizonyított; kiadási ellenőrzésnél
  a release-ág új csomagolt startup-próbája is kötelező.
- Release-integráció: `e785ab2`. A kombinált `release/1.0.1` ágon a teljes
  helyi offscreen regresszió **648 passed**; verzió/tag validáció és helyi
  Markdown-linkellenőrzés sikeres. A release-ág platform-CI-je a push után fut.
- A startup-fix integrálása után a release implementációs scope-ja lezárt;
  a tulajdonos engedélyezte a teljes release-validációt és dokumentációs lezárást.
  A fennmaradó éles main-workflow próba a következő, külön jóváhagyandó
  main-integrációs lépés része, nem hiányzó feature-kód. A részletes kapuk a
  [release-validációban](../../docs/validation/release_1_0_1_preparation.md) találhatók.
