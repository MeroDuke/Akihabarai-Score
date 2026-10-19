# Desktop onboarding

- Plan ID: `PLAN-015`
- Status: `accepted`
- Target release: `1.2.0`
- Type: `feature`
- Priority: `medium`
- Created: `2026-10-19`
- Last reviewed: `2026-10-19`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

Az első használatkor a desktop alkalmazás működését és az első értékelés
lépéseit nem feltétlenül fedezi fel magabiztosan a felhasználó. A
[usability backlogból](desktop_usability_backlog.md) az onboardingot a
tulajdonos külön kiválasztotta az 1.2.0 funkcióbővítő kiadásba.

## Cél

Alkalmazáson belüli, érthető bevezetés az első desktop használathoz. A konkrét
UX-et és a bemutatott lépéseket fejlesztés előtt tulajdonosi review pontosítja.

## Nem cél

- A teljes usability backlog megvalósítása.
- Általános súgórendszer, minden funkció tooltipje vagy teljes UI-újratervezés.
- Linux feliratvágások automatikus hozzácsapása a release-hez.
- Webes onboarding.

## Jelenlegi állapot

Az ötlet a PLAN-007 backlogban szerepelt. A
[PLAN-006 specifikáció és User Guide](product_specification_and_user_guide.md)
releváns, felülvizsgált tartalmát használjuk alapként; a teljes dokumentációs
program ettől nem kap automatikusan 1.2.0 célverziót.

## Tervezett megoldás

- Az első értékeléshez szükséges minimális bevezető út kijelölése.
- A bevezetés formájának, első indításos megjelenésének és későbbi elérésének
  pontosítása tulajdonosi UX-review-val, implementáció előtt.
- A szövegek összevetése az alkalmazás tényleges működésével és felirataival.
- A normál használatot nem akadályozó, biztonságosan elhagyható bevezetés.

## Platform- és kompatibilitási szempontok

Desktop-first, Windows elsődleges; magyar és angol felület, támogatott
ablakméret és Linux referencia-környezet ellenőrzésével. Az onboarding nem
igényelhet AniList-elérhetőséget az alapfolyamat bemutatásához.

## Tesztstratégia

- Unit/low-level tesztek a véglegesen elfogadott megjelenési és állapotszabályokra.
- Teljes felhasználói workflow: a bevezetésből az első értékelés és Tier Board
  kártya létrehozásáig, a jóváhagyott UX szerinti interakciókkal.
- Kilépés/kihagyás után a normál workflow regressziós ellenőrzése.
- Hálózat mock/fake, Qt-tesztek helyben offscreen módban, majd CI-ben.
- HU/EN kézi ellenőrzés Windows és Linux csomagolt builden.

## Elfogadási feltételek

- [ ] A minimális bevezető út és megjelenési/elhagyási szabályok tulajdonosi review-ja kész.
- [ ] A felhasználó a bevezetés alapján el tudja készíteni első értékelését és kártyáját.
- [ ] A bevezetés elhagyása nem módosítja vagy akadályozza a normál használatot.
- [ ] A szövegek HU/EN felirattal a tényleges működést tükrözik, nem vágódnak le.
- [ ] A releváns helyi tesztek és a teljes workflow/regressziós teszt sikeresek.
- [ ] A releváns CI/CD workflow-k sikeresek.
- [ ] A dokumentáció és a roadmap frissült.

## Kockázatok és visszaállítás

Túl hosszú vagy tolakodó bevezetés ronthatja a használatot. A bemutatott
folyamatot kis scope-ban, felülvizsgált szövegekkel vezetjük be; az onboarding
kikapcsolása nem érintheti a scoringot és a meglévő workflow-kat.

## Nyitott kérdések

- Mi legyen a bevezetés konkrét formája és kötelezően bemutatott lépéssora?
- Mikor jelenjen meg, és hogyan lehessen később újra elérni?
- Mely releváns specifikáció/User Guide részeket kell előbb elkészíteni?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-10-19 | Az onboarding elfogadva az `1.2.0` tartalmaként, külön tervben. | A tulajdonos csak ezt választotta ki a usability backlogból; a részletes UX még pontosítandó. |

## Megvalósítási napló

Még nem indult el.
