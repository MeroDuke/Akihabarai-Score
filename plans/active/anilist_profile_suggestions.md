# AniList-műfajok alapján választható profiljavaslatok

- Plan ID: `PLAN-023`
- Status: `accepted`
- Target release: `1.8.0`
- Type: `feature`
- Priority: `medium`
- Created: `2026-11-03`
- Last reviewed: `2026-11-03`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)
- Kapcsolódó QoL: [profilkínálat bővítése](profile_catalog_expansion.md)

## Probléma

Online animeválasztáskor a user ma kézzel választja ki a pontozási profilokat.
Az AniList műfajai segíthetnének, de nem azonosak a saját profilkatalógussal,
és egy anime háromnál több műfajhoz is tartozhat.

## Cél

Megvizsgálni és később megvalósítani a műfajok lekérését, érthető megjelenítését
és a hozzájuk illő profilok felajánlását. A user legfeljebb három profilt választ;
nem az API-lista első három elemét alkalmazzuk automatikusan.
A profilkínálat QoL-bővítésétől külön funkcióbővítő release-ben is kiadható.

## Nem cél

- Kézi beállítások automatikus felülírása vagy rejtett újrapontozás.
- Minden AniList-taghoz profil készítése, katalógustükrözés vagy persistencia.
- Offline pontozás AniList-függővé tétele; új scoring engine.

## Jelenlegi állapot és kutatási alap

A 2026-11-03-i élő, csak olvasó API-lekérdezés 19 `GenreCollection` műfajt
és 430 `MediaTagCollection` címkét adott. Ez dátumozott kutatási megfigyelés,
nem örök érvényű elemszám vagy mentett szolgáltatói katalógus.
[Hivatalos query-referencia](https://docs.anilist.co/reference/query),
[Media mezők](https://docs.anilist.co/reference/object/media).

Első vizsgálandó alap a `Media.genres`, nem a sokkal részletesebb `tags`.
A műfajok a meglévő animelekérdezésben is elkérhetők; a tényleges query,
adapter és UI adatútját implementáció előtt át kell tekinteni.
Az AS jelenlegi tíz profilja lefedi: Action, Adventure, Comedy, Drama,
Fantasy, Horror, Mystery, Romance, Sci-Fi, Slice of Life.
További műfajok: Ecchi, Hentai, Mahou Shoujo, Mecha, Music, Psychological,
Sports, Supernatural, Thriller. A profilnevek és súlyozások döntéseit a
PLAN-022 tartalmazza; ez nem kész automatikus megfeleltetés.

## Tervezett megoldás

1. Adatút- és UX-kutatás: milyen adatot kérünk az aktuálisan kiválasztott
   animéhez, hol és hogyan jelennek meg a javaslatok, mi indítja az alkalmazást.
2. Explicit AniList-műfaj → AS-profil megfeleltetés; ismeretlen műfaj nem hiba.
   A műfajnév és a mögötte használt súlyozás külön fogalom.
3. A user által preferált javaslatválasztó: legfeljebb három profil, kézi
   módosíthatóság és egyértelmű alkalmazás/megszakítás. Háromnál több találatot
   is értelmesen mutatunk, nem állítunk API-sorrendből műfaji fontosságot.
4. Meglévő kézi beállítások, mixarányok, kártyaszerkesztés és animeváltás
   pontos szabályai tulajdonosi UX-döntést igényelnek. Nincs csendes felülírás.

A közös súlyozású nevek (például Mecha/Sci-fi) deduplikálása még nyitott:
a saját nevük megtartását nem írhatja felül egy korábbi automatikus összevonási
ötlet. El kell dönteni, mit jelenítünk meg, és mi számít külön profilhelynek.

## Platform- és kompatibilitási szempontok

Offline működés és kézi profilválasztás változatlanul önálló. Hiányzó műfaj,
403/429, hálózati hiba vagy kikapcsolt integráció nem akadályozhatja a pontozást.
HU/EN és szűk ablak/DPI mellett is használható UI szükséges.
Az [AniList adat-életciklus](../../docs/integrations/anilist_data_lifecycle.md)
és a kapcsolódó audit követelményeit implementáció előtt felülvizsgáljuk;
nincs új tartós AniList-adattárolás. A mentett listákhoz tartozó PLAN-020
szolgáltatói tisztázása külön scope, nem helyettesítik egymást.

## Tesztstratégia

- Mock/fake API: megfeleltetés, ismeretlen/üres/duplikált műfaj, több mint három
  javaslat, azonos súlyozású profilnevek elfogadott szabálya.
- Teljes offscreen flow: online keresés → animeválasztás → javaslatok → maximum
  három kiválasztása → alkalmazás → pontozás és Tier-kártya létrehozása.
- Megszakítás, kézi módosítás, animeváltás, elavult válasz, Offline-váltás és
  szerkesztési állapot védelme; 403/429 és API-hiba mellett működő kézi út.
- Lokális zöld tesztek után platform-CI; CI nem hív valódi AniList API-t.
- Jóváhagyott kézi UX-review és adat-életciklus ellenőrzés.

## Elfogadási feltételek

- [ ] Célrelease, adatút és UX-scope tulajdonosi elfogadása megvan.
- [ ] Jóváhagyott műfaj–profil megfeleltetés és közös súlyozású nevek szabálya kész.
- [ ] Több mint három javaslatból is legfeljebb három profil választható.
- [ ] Mixarányok és kézi beállítások alkalmazási/felülírási szabálya egyértelmű.
- [ ] Offline/hibás hálózat esetén a saját pontozás megmarad; nincs új persistencia.
- [ ] Teljes workflow és regresszió helyben, majd CI-ben sikeres.
- [ ] AniList működési dokumentáció, User Guide releváns részei és roadmap frissült.

## Kockázatok és visszaállítás

Taxonómia és értékelési elvárások összekeverése, meglepő profilcsere, dupla
súlyozás, elavult aszinkron válasz. A javaslatfunkció eltávolítható legyen
az offline profilkínálat és meglévő pontozási út sérülése nélkül.

## Nyitott kérdések

- Hol és milyen felhasználói műveletre mutassuk a javaslatokat?
- Milyen mixarányt ajánljunk, és mikor változtathatunk meglévő beállítást?
- Mi legyen a részben támogatott műfajokkal és azonos súlyozású nevekkel?
- A kutatás és implementáció egy vagy több külön release-elemmé váljon-e?
- Célrelease: `1.8.0`. A teljes profilbővítés nem kötelező
  előfeltétel, de a választott scope profiljainak stabilnak kell lenniük.

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-11-03 | Külön új feature-terv, `TBD` célverzióval. | A profilbővítés és az online javaslat önállóan ütemezhető, további részekre is bontható. |
| 2026-11-03 | A user választ legfeljebb három javaslatból. | Tulajdonosi preferencia, nem önkényes első-három kiválasztás. |

## Megvalósítási napló

Tervezési jóváhagyás: 2026-11-03, célrelease `1.8.0`, státusz `accepted`.
Implementáció nem indult; részletes UX és megfeleltetési szabályok még pontosítandók.

