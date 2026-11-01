# Eredménytáblázat tördelése és másolásgomb elhelyezése

- Plan ID: `PLAN-018`
- Status: `accepted`
- Target release: `1.1.0`
- Type: `usability`
- Priority: `medium`
- Created: `2026-11-01`
- Last reviewed: `2026-11-01`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

A tulajdonos 2026-11-01-én képernyőképpel jelezte az eredménypanel
elrendezési hibáját. A részletes táblázat alsó sora csak részben látszik,
a „Részletes adatok másolása vágólapra” gomb a táblázat alsó részére fed.
A többsoros dimenziófeliratok tördelését és a sormagasságokat is vizsgálni kell.

A képernyőkép megfigyelési bizonyíték, nem igazolt reprodukció. A pontos
alkalmazásverzió, ablakméret, DPI/skálázás és kiváltó lépések még nem ismertek;
gyökérokot nem állapítottunk meg. Nem feltételezzük, hogy Linux-specifikus.

## Cél

Az 1.1.0-ban az eredménytáblázat és a másolásgomb átfedésmentes, használható
elrendezése; minden dimenzió és érték olvasható vagy szabályosan görgethető.

## Nem cél

- Azonnali implementáció vagy teljes eredménypanel-újratervezés.
- Scoring, kerekítés vagy a vágólapra másolt adatformátum módosítása.
- A későbbre hagyott általános Linux vizuális rendbetétel előrehozása.

## Jelenlegi állapot

A hiba felhasználói képen látható, helyben még nem reprodukáltuk. A javítás
elfogadott release-scope, de fejlesztése nem indult el.

## Tervezett megoldás

Előbb reprodukáljuk a hibát, ellenőrizzük a layout méretkorlátait, a táblázat
szövegtördelését, sormagasságát és a gomb helyfoglalását. Az igazolt ok alapján
célzott javítás készül. Kis magasság esetén a táblázat görgethető maradjon,
ne a gomb takarja el az adatokat.

## Platform- és kompatibilitási szempontok

Windows az elsődleges cél. HU/EN nyelv, hosszú feliratok, támogatott minimális
ablakméret, átméretezés és eltérő DPI/skálázás vizsgálandó. Linuxon célzott
regresszióellenőrzés indokolt, nem teljes általános layout-review.

## Tesztstratégia

- Low-level/layout regressziós teszt az igazolt kiváltó méret- és tördelési esetre.
- Teljes Qt workflow: pontozás felhasználói vezérlőkkel, eredmény megjelenése,
  átméretezés/nyelvváltás, majd a részletes másolás gomb használata és a
  vágólaptartalom ellenőrzése; külső API nélkül.
- A táblázat és gomb geometriája nem fedheti egymást; mind a nyolc sor
  hozzáférhetőségét ellenőrizni kell, szükség esetén görgetéssel.
- Helyi Qt-tesztek `QT_QPA_PLATFORM=offscreen` módban, majd CI-regresszió.
- Kézi vizuális ellenőrzés csomagolt builden, a reprodukált DPI- és méretesettel.

## Elfogadási feltételek

- [ ] A reprodukció és gyökérok dokumentált.
- [ ] A táblázat és a másolásgomb nem fedik egymást.
- [ ] Minden sor/érték olvasható vagy görgetéssel elérhető, a tördelés megfelelő.
- [ ] A másolás gomb elérhető és változatlanul helyes tartalmat másol.
- [ ] HU/EN, átméretezési és releváns DPI-regressziók ellenőrzése sikeres.
- [ ] A low-level és teljes workflow-teszt helyben, majd CI-ben sikeres.
- [ ] A dokumentáció és a roadmap frissült.

## Kockázatok és visszaállítás

Fix méretek beégetése más DPI-n vagy nyelven újabb levágást okozhat. A javítás
a meglévő eredménypanelre korlátozott, regressziós teszttel és külön fix-ágon
készül; probléma esetén önállóan visszavonható.

## Nyitott kérdések

- Mely alkalmazásverzióban, ablakmérettel és skálázással jelentkezik?
- Induláskor is fennáll, vagy átméretezés/nyelvváltás után alakul ki?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-11-01 | A táblázat és másolásgomb layout-hibájának javítása az `1.1.0` elfogadott eleme. | Tulajdonosi hibajelzés képernyőképpel; most csak rögzítés, későbbi célzott javítás. |

## Megvalósítási napló

Még nem indult el.
