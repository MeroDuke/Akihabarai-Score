# 1.0.0 dokumentációs lezáró review

- Dátum: 2026-10-19
- Célverzió: 1.0.0, kiadás előtti állapot
- Kapcsolódó terv: [PLAN-014](../../plans/completed/release_1_0_0_preparation.md)
- Kiinduló forrásállapot: `468ae89`

## Ellenőrzött területek és eredmény

| Terület | Összevetés alapja | Eredmény |
| --- | --- | --- |
| README | Profilkonfiguráció, fordítások, scoring, módok, szerkesztés, export és update workflow | A termékleírás egyezik; bekerült a teljes portable csomag kicsomagolása és indítása, valamint az AniList kiválasztási és hibakezelési lépése. |
| AniList | Provider, controller, runtime modellek, preference, logger és clipboard | A külön audit eltérései javítva; 141 kapcsolódó teszt sikeres volt. |
| Indítás és crash | Launcher, supervisor, logger, Linux core metadata | Friss fájlnevek, fejlesztői indítási parancs, best-effort fájlírás és a különböző fájltípusok megőrzési határai dokumentálva. |
| Lokalizáció és desktop adapterek | Katalógusok, preference store, Qt adapter és workflow-k | A megszűnt fordítási kulcs és a launchert kihagyó példa javítva; az adapterhatárok megfelelnek a kódnak. |
| Linux futtatás | Ubuntu 24.04 csomaglista, spec és Linux CI | Az indítási lépések és a diagnosztikai buffer neve javítva; Debian kézi próba történeti megfigyelés marad. |
| Licenc és csomagolás | LICENSE, metadata, dependency lock, spec, gyűjtő/validáló scriptek és két workflow | A GPLv3 út, legal-layout és forrásarchívum-lánc leírása egyezik. A baseline audit múlt idejűként jelölt; az inventory/SBOM CI-bizonyíték, nem portable fájl. |
| Brand és creator policy | Korábbi tulajdonosi döntés, LICENSE, csomagolási tesztek | Megmaradt a külön arculati policy és az önkéntes kreditkérés; egyik sem kerül a portable gyökérbe. Szabálymódosítás nem történt. |
| Hibajelentés | README, issue template és tényleges diagnosztikai fájlok | Verzió/platform mezők és a megmaradt buffer bekérése pontosítva. |

A tier-jelmagyarázat emoji-színeinek eltérése a desktop színeitől korábban
elfogadott kompromisszum; ebben a review-ban nem változott.

## Ellenőrzési határ és nyitott release-kapuk

Ez a review a repository dokumentumait vetette össze az implementációval és
a meglévő bizonyítékokkal. Nem új licencelési döntés és nem igazolja előre a
még nem publikált 1.0.0 csomagokat.

- A review után előállított `da914f3` Windows és Linux preview csomagok kézi
  átvételét a tulajdonos sikeresnek ítélte. A bizonyíték és az ismert Linux
  megjelenítési eltérések a kapcsolódó PLAN-014 rekordban szerepelnek.
- A valódi tag-only forrásletöltés, Qt jogi anyaggyűjtés és publikált assetek
  ellenőrzése a release-futás kapuja marad.
- A GraphQL HTTP-success `errors` diagnosztikai stringje jelenleg nincs az
  HTTP-hibaüzenetekhez hasonlóan korlátozva; az AniList dokumentum ezt rögzíti.
- A `.tmp` fault bufferek és `.dmp` fájlok nem esnek a normál logger 14 napos
  `.log` takarítása alá. OS-managed core dumpra szintén nincs ilyen garancia.
- A Windows CI egyszer az ablak megjelenítésénél timeoutolt; ugyanaz a commit
  változtatás nélkül sikeres újrafutást adott. A gyökérok nem bizonyított.

## Ellenőrzési bizonyíték

A dokumentációváltozás ellenőrzése: helyi Markdown-célok feloldása,
`git diff --check`, valamint a meglévő licenc-, brand-, runtime-, csomagolási,
lokalizációs és launcher-tesztek célzott futtatása. Az eredményeket a
release-előkészítési terv megvalósítási naplója rögzíti.
