# Opcionális webes Pontozó irány

- Plan ID: `PLAN-008`
- Status: `deferred`
- Target release: `TBD`
- Type: `feature`
- Priority: `low`
- Created: `2026-09-29`
- Last reviewed: `2026-09-29`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

A külön Akihabarai Könyvespolc webprojektben már létezik Vue 3, TypeScript,
Vite és FastAPI infrastruktúra, `/score` placeholder és tervezett `0.2.0`
webes Pontozó release. A webes felület azonban opcionális: nem előzheti meg a
desktop munkát, és nem indokolhat desktop regressziót vagy szükségtelen
architekturális bonyolítást.

## Cél

A pontozási rendszer későbbi, iteratív és webnatív megvalósítása a külön
webprojektben. A számítási szabályok maradjanak konzisztensek, miközben a
böngészős és mobilos workflow eltérhet a desktop UI-tól.

## Nem cél

- A desktop alkalmazás egy az egyben történő lemásolása.
- SDK, publikus Core API vagy külső kompatibilitási ígéret.
- A desktop architektúra webes igények alá rendelése.
- AniList, Tier Board, autentikáció, adatbázis és mentés az első szeletben.
- A webprojekt release-scope-jának ebből a repóból történő jóváhagyása.

## Jelenlegi állapot

A desktop scoring, profile mix és strukturált eredménymodellek jelentős része
UI-független. A webprojektben működik a frontend, backend, deployment,
request-ID diagnosztika, Playwright és accessibility tesztalap. Scoring endpoint
és webes scoring workflow még nincs.

## Tervezett megoldás

Az első szelet egyprofilos pontozást, validációt, eredményt és újrakezdést
tartalmazhat. Később jöhet többprofilos keverés, webes lokalizáció, reszponzív
finomítás és használati tapasztalat alapján módosított workflow.

A scoring request/response és strukturált állapot csak az aktuális szelethez
szükséges minimális formában készül el. Belső integrációs szerződés, nem SDK.
A web használhat böngészőnyelvet és webes preferenciát; nem kötelező átvennie
a desktop külön nyelvváltó gombját.

A későbbi webes Tier Boardnak a desktop releváns képességeit kell biztosítania,
de az interakció web- és mobilnatív lehet. Webes AniList csak minden fontosabb
webes képesség után vizsgálandó, a dokumentált runtime-only, no-cache,
no-history és no-image-persistence szabályok megtartásával. Sessionmentés csak
felhasználói profil, autentikáció, adatbázis és külön adatvédelmi döntés mellett
kerülhet elő.

## Platform- és kompatibilitási szempontok

A desktop és web verziózása független. A web a Könyvespolc Vue/FastAPI
stackjéhez igazodik. A desktop buildje, tesztje és release-e nem függhet webes
komponenstől.

## Tesztstratégia

- Scoring szabályok regressziós összevetése a desktop eredményekkel.
- FastAPI contract és Vue komponens tesztek.
- Legalább egy teljes Playwright scoring workflow.
- Mobil viewport és accessibility vizsgálat.
- Külső szolgáltatások mockolása; AniList nem hívható megbízhatatlanul CI-ből.

## Elfogadási feltételek

- [ ] A webprojektben külön elfogadtuk az első iteráció pontos scope-ját.
- [ ] A workflow webnatív és nem puszta desktopmásolat.
- [ ] A közös pontozási szabályok eredménye konzisztens.
- [ ] A desktopban nincs webspecifikus regresszió vagy indokolatlan függőség.
- [ ] A webprojekt saját helyi és CI-tesztjei sikeresek.
- [ ] Mindkét projekt érintett dokumentációja frissült.

## Kockázatok és visszaállítás

A scope könnyen teljes desktop-paritási projektté nőhet. Kis, önmagukban
használható szeletekkel kell haladni. A webes munka megszakítása nem hagyhat
működésképtelen vagy webfüggő desktop állapotot.

## Elhalasztás oka és újranyitási feltétel

A desktop alkalmazás minden fejlesztése magasabb prioritású. A terv akkor
nyitható újra, ha nincs fontosabb desktop feladat, és a webprojektben külön
elfogadjuk az első iteráció scope-ját.

## Nyitott kérdések

- Mi legyen az első valóban használható webes függőleges szelet?
- Mely szabályokat használjuk közösen, és mely interakciókat tervezzük újra?
- Mikor indokolt a Tier Board és később az AniList hozzáadása?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-09-29 | A WebUI opcionális és desktop alatti prioritású. | A desktop az elsődleges, önálló termék. |
| 2026-09-29 | A megvalósítás webnatív és iteratív. | A böngészős workflow nem desktopmásolat. |
| 2026-09-29 | SDK-irány nincs. | Belső vagy publikus SDK nem része a stratégiának. |

## Megvalósítási napló

