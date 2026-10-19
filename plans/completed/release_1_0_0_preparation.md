# 1.0.0 release-előkészítés

- Plan ID: `PLAN-014`
- Status: `completed`
- Target release: `1.0.0`
- Type: `reliability`
- Priority: `critical`
- Created: `2026-10-19`
- Last reviewed: `2026-10-19`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

A closed beta stabilizációja lezárható: hosszabb ideje nem érkezett új,
megerősített regresszió, a vegyes DPI-s indulást pedig három eltérő monitoron
kézzel is sikerült ellenőrizni. A forrás ugyanakkor még `0.23.0` verziót jelez,
nincs összeállított 1.0.0 changelog, és a tagelt release workflow nem ellenőrzi,
hogy a Git tag megegyezik-e az alkalmazás és a Python csomag verziójával.

## Cél

Az elkészült termékből reprodukálható, dokumentált és ellenőrizhető 1.0.0
release-jelölt előállítása úgy, hogy a tényleges tagelés, GitHub Release és
`main` merge külön tulajdonosi jóváhagyáshoz kötött maradjon.

## Nem cél

- Új felhasználói funkció bevezetése.
- Nem igazolt vagy nem kritikus QoL-ötletek hozzáadása az 1.0.0 scope-hoz.
- Python-, Qt- vagy Ubuntu-baseline frissítése.
- Tag, GitHub Release, deployment vagy `main` merge létrehozása.

## Jelenlegi állapot

Az 1.0.0 funkcionális és stabilizációs fejlesztései elkészültek. A Windows és
Linux CI a release-csomagolást, startupot, natív crash diagnosztikát és GPLv3
megfelelőségi bizonyítékokat ellenőrzi. A következő minor release kapuja
teljesül: az 1.1.0 elfogadott első terve a kereszt-réteges tracing.

## Tervezett megoldás

1. Az alkalmazás- és csomagverzió átállítása `1.0.0` értékre.
2. Az 1.0.0 változásainak felhasználóközpontú összefoglalása a changelogban,
   `Unreleased` állapotban a tényleges kiadás napjáig.
3. Verziókonzisztencia-ellenőrzés az alkalmazás, a csomag, a changelog és
   tagelt build esetén a Git tag között.
4. Felhasználói dokumentáció, aktuális műszaki dokumentáció és release-layout
   célzott lezáró ellenőrzése.
5. Teljes helyi regresszió, majd Windows és Linux CI-validáció.
6. A release-jelölt kézi ellenőrzése, végleges dátumozása és csak külön
   jóváhagyással történő integrálása, tagelése és kiadása.

## Platform- és kompatibilitási szempontok

A Windows marad az elsődleges platform, Linux x86_64 kísérleti támogatással.
Az 1.0.0 Python 3.11.9 és Ubuntu 24.04 baseline-ját nem változtatjuk meg. A
release-előkészítés nem módosíthatja a már kézzel validált desktop működést.

## Tesztstratégia

- Low-level tesztek a verzióforrások és a changelog egyezésére.
- Negatív teszt eltérő release tag esetére.
- A meglévő teljes Qt workflow/regressziós tesztkészlet headless futtatása.
- Windows és Linux csomagolási, startup-, crash- és compliance-workflow CI-ben.
- Kézi indítás és fő felhasználói workflow a release-jelölt csomagból.

## Elfogadási feltételek

- [x] Az alkalmazás és a csomag verziója `1.0.0`.
- [x] Az 1.0.0 changelog felhasználóközpontúan összefoglalja a kiadást.
- [x] Hibás vagy eltérő Git tag esetén a release workflow build előtt megáll.
- [x] A README és a releváns aktuális dokumentáció megfelel a jelenlegi release-jelölt implementációnak.
- [x] A teljes helyi tesztkészlet sikeres.
- [x] A teljes workflow/regressziós teszt helyben sikeres.
- [x] A Windows és Linux CI/CD workflow sikeres.
- [x] A release-jelölt kézi ellenőrzése dokumentált.
- [x] A dokumentáció és a roadmap frissült.

## Kockázatok és visszaállítás

A túl korai verziódátum vagy tag publikálása félkész release-t hozhatna létre,
ezért a changelog a tényleges kiadásig `Unreleased`, és tag nem készül ebben a
fázisban. A metadata-változtatások egyetlen release-előkészítési commitból
visszaállíthatók; a korábbi `0.23.0` tag változatlan marad.

## Nyitott kérdések

Nincs nyitott kiadási kérdés. Az 1.0.0 2026-10-19-én külön tulajdonosi
jóváhagyással megjelent; a részletes bizonyíték a
[kiadási validációban](../../docs/validation/release_1_0_publication.md) található.

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-10-19 | Megkezdődött az 1.0.0 release-előkészítés. | Hosszabb ideje nem érkezett új hiba, a tulajdonos lezárhatónak ítélte a closed-beta stabilizációt. |
| 2026-10-19 | A tényleges release külön jóváhagyás marad. | A metadata előkészítése nem jelent tagelési vagy publikálási engedélyt. |

## Megvalósítási napló

Branch: `feature/license-compliance` (a korábbi döntés alapján az 1.0.0
integrációs ága).

- `2026-10-19`: az alkalmazás- és csomagverzió `1.0.0` lett; elkészült az
  `Unreleased` changelog és a verzió/tag/changelog konzisztencia kapuja.
- Implementációs commit: `7e100cd` (`release: prepare 1.0.0 metadata and validation`).
- Helyi ellenőrzés: `QT_QPA_PLATFORM=offscreen python -m pytest -q` —
  623 sikeres teszt.
- CI: [Windows](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/39207352529)
  és [Linux](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/39207352543)
  sikeres, beleértve a csomagolási, startup-, crash- és portable-validációt.
- Az előkészítés utáni kiadási kapu: changelog dátumozása a kiadás napján,
  külön main-integrációs és publikálási jóváhagyás, majd a tag-only folyamat
  és a publikált csomagok ellenőrzése.
- `2026-10-19`: az AniList működési dokumentumának kód- és tesztalapú review-ja
  elkészült. Pontosítottuk a romaji autocomplete, exact-match/debounce,
  runtime találat-újrahasználat, retry, szinkron hálózati fallback, preference,
  clipboard-export és crash-diagnosztika határait. A kapcsolódó 141 teszt zöld;
  a GraphQL hibadetail korlátjának hiányát a dokumentum tényszerűen rögzíti.
- `2026-10-19`: a [dokumentációs lezáró review](../../docs/validation/release_1_0_documentation_review.md)
  elkészült. README, indítás, hibajelentés, crash-megőrzés, lokalizáció,
  Linux-runtime és compliance történeti/jelenlegi határok pontosítva;
  licenc- és brandpolicy-döntés nem változott. A célzott 52 meglévő teszt
  sikeres, a helyi Markdown-célok ellenőrzése és `git diff --check` hibamentes.
- `2026-10-19`: átmeneti, kézzel indított CI-csomagok készültek a `da914f3`
  commitból a felhasználói átvételi próbához. A
  [Windows](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/39211213850)
  és [Linux](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/39211216646)
  futás a forrásarchívum-letöltést/hash-ellenőrzést, Qt jogi anyaggyűjtést és
  tag-szintű portable-validációt is végrehajtotta, publikálás nélkül.
  A preview artifactok 2026-10-26-ig érhetők el. Az ideiglenes workflow-opció
  a `3f2b3fa` visszaállítással megszűnt; a normál csomagmegőrzés továbbra is
  release-only. A visszaállítás után a célzott 22 helyi teszt sikeres.
- `2026-10-19`: a tulajdonos a `da914f3` Windows preview csomag kézi
  átvételét elfogadta: a próbában nem talált hibát. A Linux preview kézi
  próbája VMware Workstation Pro VM-ben szintén sikeres; csak a már ismert,
  korábban elfogadott Linux megjelenítési eltérések maradtak. Ezek a
  [desktop QoL-backlogban](../active/desktop_usability_backlog.md) szerepelnek.
- A két átvett csomag SHA-256 értéke:
  Windows `69e210b15f24ce5f7f34266488426e84ea475ee3a87b6943cb3f45949118a333`;
  Linux `e072e9c1cf4c1cfafbe1db8e079fc483e70782224ad1a578bb8ccc94c97e14ce`.
- A preview óta az `app/`, `config/`, `assets/`, spec és dependency lock
  tartalma változatlan; az ideiglenes CI-opció visszaállt.
- `2026-10-19`: az előkészítést a tulajdonos engedélyével lezárjuk.
  A verzió `1.0.0`, a changelog tartalma elfogadásra kész, dátuma a tényleges
  publikálásig `Unreleased`. Az 1.1.0 elfogadott tracing terve teljesíti a
  következő minor release tervezési kapuját.
- Lezáró helyi regresszió: `QT_QPA_PLATFORM=offscreen python -m pytest -q` —
  624 sikeres teszt; a release-verzió validáció és `git diff --check` sikeres.
  A friss `origin/main` a munkabranch előzménye; `git merge-tree --write-tree`
  konfliktusmentes integrációt mutatott a main módosítása nélkül.
- `2026-10-19`: main-integráció `8545205`, dátumozott kiadási commit
  `21cd3a1`; a tulajdonos jóváhagyására létrejött a `v1.0.0` tag és a
  GitHub Release. Mindkét tag-workflow, a forrásletöltés, valamint a
  publikált csomagok utólagos letöltése/validációja sikeres.
