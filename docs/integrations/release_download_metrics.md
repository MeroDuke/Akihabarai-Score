# GitHub release-letöltési metrikák

Az adatgyűjtő nem része a desktop runtime-nak. A
[`release_download_metrics.py`](../../scripts/release_download_metrics.py) kizárólag
a GitHub release API-ját olvassa. Nem tölt le alkalmazáscsomagot, nem figyel
felhasználókat, és nem növeli a release assetek letöltési számlálóját.

## Adatok és számlálás

- A kiadások és az egyes kiadások assetjei külön, 100 elemű lapokkal kérdezhetők le.
- Csak publikált stabil release-ek számítanak; draft és prerelease kimarad.
- Kizárólag az `AkihabaraiScore-windows.zip` és
  `AkihabaraiScore-linux-x86_64.tar.gz` fájlok számítanak alkalmazásletöltésnek.
  Új csomagnév bevezetésekor a whitelist és a teszt együtt frissítendő.
- A platformonkénti jelvény az összes jelenleg meglévő stabil alkalmazás-asset
  számlálójának összege. Nem tartalmaz már törölt asseteket, nem egyedi emberek,
  telepítések vagy aktív felhasználók száma. Saját és automata letöltések is
  benne lehetnek. A release-/assetazonosító és név megmarad az előzményben.
- Naponta az első sikeres UTC-minta marad meg. Ugyanaznap újrafuttatva nem kérdez
  újra API-t és nem cseréli a mintát; másnap már új állapotot figyel meg.
- Hiányzó napot nem becslünk meg. Asset törlés/újrafeltöltés, számlálócsökkenés
  és kimaradt nap külön `events.json` esemény. A grafikon ilyenkor nem rajzol
  megtévesztő összekötő vonalat. Visszamenőleges mintát nem fogadunk el.

## Ütemezés, tárolás és jogosultság

A [workflow](../../.github/workflows/download-metrics.yml) napi **05:17 UTC**
ütemezésű, kézzel is indítható az Actions felületén, és a releváns main push
után is lefut. Az ütemezés GitHub-oldalon késhet vagy kimaradhat.

A gyűjtő csak az eredeti repository `main` ágán futhat. PR-, feature- és
release-ágon csak offline teszt fut, nincs éles adatírás. Az olvasási jogosultság
az alapértelmezés; `contents: write` csak a gyűjtőjobhoz szükséges. Az aktuális
`GITHUB_TOKEN` kezeli az API-t és git hitelesítést, nem kerül jelentésbe.

Az automata kizárólag a **`metrics/downloads`** adatágra pushol, force nélkül.
Nem írja a maint, nem hoz létre taget vagy release-t. Első futáskor létrehozza
az adatágat. A minták nem lejáró workflow-artifactok:

- `history.json`: schema v1, repository és napi minták, UTC-idővel;
- `events.json`: megfigyelt törlések, új assetek, csökkenések és hiányok;
- `windows.json`, `linux.json`: Shields endpoint JSON, dátumozott címkével;
- `downloads.svg`, `README.md`: újragenerálható grafikon és részletes jelentés.

Az API vagy validáció hibája a push előtt leállítja a jobot. A publikált
előzmény és jelvények az utolsó sikeres, dátumozott mintán maradnak, nem lesz
hamis nulla. A dátumot kell nézni: egy régi jelvény nem friss mérés.
A Shields és GitHub képcache miatt a megjelenés késhet. A gyűjtőworkflow hibája
nem blokkolja a desktop buildet, indítást vagy release-workflow-t.

## Kipróbálás

Helyi, csak olvasó valós lekérdezés (a kimenet nem kerül Gitbe):

```powershell
python scripts/release_download_metrics.py --output build/download-metrics-preview
```

Nyisd meg a kimeneti `downloads.svg` fájlt és a `README.md` jelentést. GitHub API
limit esetén `GH_TOKEN` adható meg környezeti változóként, soha nem parancssori
argumentumként. Ugyanaznap friss lekérdezéshez válassz új kimeneti könyvtárat;
ne töröld a tartós adatág előzményeit.

Offline teljes workflow-próba:

```powershell
python -m pytest tests/test_release_download_metrics.py -q
```

A teszt fixture-API-val és subprocess CLI-vel ellenőrzi az adat → tartós minta →
grafikon → jelvény útvonalat, újrafuttatást és hiba utáni helyreállást.

Éles aktiválás a jóváhagyott main-integráció után: Actions → Release download
metrics → Run workflow → main. Ellenőrzendő a külön adatág, a jelentés dátuma,
a whitelistelt platformösszegek, a README-jelvények és a grafikon világos/sötét
témában. Ugyanazon napi ismétlés nem készíthet új adatcommitot. Main-integráció
előtt a letöltési endpointok még nem léteznek, ezért a jelvények még nem mutatnak
éles értéket; az offline teszt nem jelenti az ütemezés aktiválását.

Források: [GitHub Releases API](https://docs.github.com/en/rest/releases/releases),
[ütemezett workflow-k](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule),
[Shields endpoint](https://shields.io/badges/endpoint-badge).
