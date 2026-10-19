# Release-letöltések, grafikon és README-jelvények

- Plan ID: `PLAN-017`
- Status: `accepted`
- Target release: `1.1.0`
- Type: `reliability`
- Priority: `medium`
- Created: `2026-10-19`
- Last reviewed: `2026-10-19`
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
- Tartós pillanatkép-tárolás és belőlük újragenerálható grafikon; a tárolás és
  megjelenítés helyét implementáció előtt választjuk ki. Ne függjön a normál
  release-only build-artifact retentiontől, ne hozzon létre release-t.
- Azonos nap újrafuttatása, hiányzó nap, asset törlés/újrafeltöltés és számláló-
  csökkenés explicit kezelése; nem változtatunk negatív eltérést csendben nullává.
- Minimális jogosultság, titok nem kerül az adatokba vagy logba.

### README-jelvények

- Aktuális stabil release, a letöltési oldalra mutatva.
- Windows támogatott és Linux kísérleti státusz, nem azonos támogatási szintet sugallva.
- HU/EN felület és pontos `GPL-3.0-only` licenc, releváns hivatkozásokkal.
- Windows- és Linux-csomagok külön letöltésszáma; függőségforrások nem számítanak
  alkalmazásletöltésnek. Végrehajtáskor pontosítjuk, hogy minden release összesét
  vagy a legfrissebb kiadást mutatják; a felirat ezt egyértelművé teszi.
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
implementáció külön fejlesztési ágon készül az 1.1.0 szabályai szerint.

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
- [ ] A grafikon verzió és platform szerint az alkalmazáscsomagokat mutatja.
- [ ] A lekérdezési idő, hiányok és korlátok egyértelműen láthatók.
- [ ] Lapozás, hibakezelés és assetcsere helyesen kezelt és tesztelt.
- [ ] A teljes adatgyűjtés–tárolás–grafikon workflow helyben és CI-ben zöld.
- [ ] Az alkalmazás és a release-only csomagmegőrzés nem változik.
- [ ] A jóváhagyott README-jelvények működnek, a letöltések csak AS-csomagokat
  számolnak; platformstátusz, licenc, frissesség és kattintási cél egyértelmű.
- [ ] A dokumentáció és a roadmap frissült.

## Kockázatok és visszaállítás

API-limit, jogosultsági hiba, megszakadt ütemezés vagy újrafeltöltött asset
félrevezető görbét okozhat. Stabil azonosítók és az eredeti minták megőrzése
szükséges. A workflow letiltható az alkalmazás érintése és az előzmények törlése nélkül.

## Nyitott kérdések

- Hol tároljuk a mintákat és hol legyen elérhető a grafikon?
- Melyik napi UTC időpontban fusson a gyűjtés?
- Melyik badge-szolgáltatást és letöltési időtávot használjuk, és kell-e CI-jelvény?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-10-19 | A napi gyűjtés és grafikon az `1.1.0` elfogadott kísérő eleme. | A tulajdonos most egyszeri lekérdezést kért, az automatizálást későbbre ütemezte. |
| 2026-10-19 | A README badge-rendszere is az `1.1.0` része. | A tulajdonos a release-, platform-, nyelv-, licenc- és letöltésjelzések betervezését kérte; a végleges összeállítás review-t kap. |

## Megvalósítási napló

Az automatizálás még nem indult el.
