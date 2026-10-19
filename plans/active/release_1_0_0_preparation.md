# 1.0.0 release-előkészítés

- Plan ID: `PLAN-014`
- Status: `in-progress`
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

- [ ] Az alkalmazás és a csomag verziója `1.0.0`.
- [ ] Az 1.0.0 changelog felhasználóközpontúan összefoglalja a kiadást.
- [ ] Hibás vagy eltérő Git tag esetén a release workflow build előtt megáll.
- [ ] A README és a releváns aktuális dokumentáció megfelel a kiadott működésnek.
- [ ] A teljes helyi tesztkészlet sikeres.
- [ ] A teljes workflow/regressziós teszt helyben sikeres.
- [ ] A Windows és Linux CI/CD workflow sikeres.
- [ ] A release-jelölt kézi ellenőrzése dokumentált.
- [ ] A dokumentáció és a roadmap frissült.

## Kockázatok és visszaállítás

A túl korai verziódátum vagy tag publikálása félkész release-t hozhatna létre,
ezért a changelog a tényleges kiadásig `Unreleased`, és tag nem készül ebben a
fázisban. A metadata-változtatások egyetlen release-előkészítési commitból
visszaállíthatók; a korábbi `0.23.0` tag változatlan marad.

## Nyitott kérdések

- Mi lesz az 1.0.0 tényleges kiadási dátuma az utolsó release-jelölt próba után?
- Szükséges-e újabb külső closed-beta kör a végleges tag előtt?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-10-19 | Megkezdődött az 1.0.0 release-előkészítés. | Hosszabb ideje nem érkezett új hiba, a tulajdonos lezárhatónak ítélte a closed-beta stabilizációt. |
| 2026-10-19 | A tényleges release külön jóváhagyás marad. | A metadata előkészítése nem jelent tagelési vagy publikálási engedélyt. |

## Megvalósítási napló

Branch: `feature/license-compliance` (a korábbi döntés alapján az 1.0.0
integrációs ága).
