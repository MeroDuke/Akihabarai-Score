# Profilkínálat és súlyozások bővítése — QoL

- Plan ID: `PLAN-022`
- Status: `accepted`
- Target release: `1.7.0`
- Type: `usability`
- Priority: `medium`
- Created: `2026-11-03`
- Last reviewed: `2026-11-03`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)
- Kapcsolódó feature: [AniList-profiljavaslat](anilist_profile_suggestions.md)

## Probléma

A jelenlegi tíz profil nem fed le minden olyan műfaji megközelítést, amelyet
a tulajdonos használna. Az AniList műfajlistája hasznos összehasonlítási alap,
de nem kötelező saját profilrendszer vagy minden elemre kiterjedő feladatlista.

## Cél

Az offline is teljes értékű profilkínálat bővítése tulajdonossal átbeszélt
elnevezésekkel és súlyozásokkal. Önálló QoL-ként, az AniList-feature előtt is
kiadható; szükség esetén több kisebb, külön elfogadott csomagra bontható.

## Nem cél

- AniList-lekérés vagy automatikus profilválasztás.
- Minden műfajhoz kötelezően új, külön súlyvektor készítése.
- A meglévő profilok vagy pontozási eredmények csendes átírása.

## Jelenlegi állapot

Forrás: [profiles.json](../../config/profiles.json),
[magyar elnevezések](../../config/locales/hu.json).
Tíz profil, nyolc dimenziónkénti relevanciával. A relevancia nem százalék;
a profilmix aránya ettől külön beállítás.

| Profil | Történet | Karakter | Tempó | Rendezés | Animáció | Dizájn | Hang | Élmény |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fantasy | 0,9 | 0,8 | 0,6 | 0,8 | 0,7 | 1,0 | 0,7 | 0,9 |
| Rejtély | 1,0 | 0,7 | 0,8 | 0,9 | 0,4 | 0,6 | 0,8 | 0,9 |
| Romantika | 0,7 | 1,0 | 0,7 | 0,6 | 0,3 | 0,5 | 0,7 | 1,0 |
| Dráma | 0,9 | 1,0 | 0,7 | 0,8 | 0,3 | 0,5 | 0,8 | 1,0 |
| Akció | 0,6 | 0,6 | 0,9 | 0,8 | 1,0 | 0,8 | 0,7 | 0,8 |
| Kaland | 0,8 | 0,7 | 0,8 | 0,7 | 0,8 | 0,8 | 0,6 | 0,9 |
| Humor | 0,5 | 0,8 | 0,9 | 0,6 | 0,4 | 0,6 | 0,8 | 0,9 |
| Mindennapi Élet | 0,6 | 0,9 | 0,7 | 0,6 | 0,2 | 0,5 | 0,7 | 0,9 |
| Sci-fi | 0,9 | 0,7 | 0,6 | 0,9 | 0,6 | 1,0 | 0,8 | 0,9 |
| Horror | 0,8 | 0,7 | 0,7 | 0,9 | 0,4 | 0,7 | 1,0 | 1,0 |

## Tervezett megoldás

Először katalógus-review: meglévő profil, új név közös súlyozással, valóban új
súlyozás, illetve egyelőre nem támogatott jelölt elkülönítése.

- Mecha: saját megjelenített név, a Sci-fi mögötti közös súlyozással; ezt a
  tulajdonos kifejezetten így képzeli el. Ne másolt, később széteső értékek legyenek.
- Thriller: a tulajdonos nehezen választja el a Horrortól; közös súlyozás
  jelöltje. A külön név és végleges megfeleltetés még jóváhagyandó.
- Mahou Shoujo: nincs elfogadott súlyozás. Felmerült Fantasy + Mindennapi Élet,
  de a Madoka Magica ellenpélda megmutatta, hogy ez nem általánosítható.
  A battle shounen hiánya és a Mahou Shoujo külön műfaja is jelzi, hogy az
  AniList taxonómiája nem automatikusan saját pontozási elvárás.
- További jelöltek: Ecchi, Hentai, Music, Psychological, Sports, Supernatural.
  Ezek nem vállalt új profilok; külön döntés szükséges mindegyikhez.

Minden elfogadott új súlyozás nyolc relevanciát és rövid indoklást kapjon.
A közös súlyozás technikai megoldása tervezendő, a publikus profilazonosítók
és a meglévő konfigurációk kompatibilitásának megőrzésével.

## Platform- és kompatibilitási szempontok

Windows elsődleges, Linux támogatási szintje változatlan. HU/EN nevek,
csomagolt konfiguráció, profilmix és kártyaszerkesztés egyaránt ellenőrzendő.
Offline használat nem igényelhet hálózatot vagy AniList-adatot.

## Tesztstratégia

- Konfiguráció/alias feloldás, hiányzó cél, ciklus, nyolc érvényes relevancia.
- Azonos súlyozású nevek azonos bemenetre azonos pontszámot adnak.
- Meglévő profilok eredménye változatlan, kivéve külön jóváhagyott módosítás.
- Teljes offscreen UI-flow: új profil kézi kiválasztása → pontozás → Tier
  listához adás → szerkesztés, HU/EN és többprofilos esetekkel.
- Helyi tesztek után platform-CI és csomagolt smoke; nincs külső API-függés.

## Elfogadási feltételek

- [ ] A konkrét profilcsomag és célrelease tulajdonosi jóváhagyása megvan.
- [ ] Minden bevezetett névhez jóváhagyott közös vagy új súlyozás tartozik.
- [ ] Közös súlyozások nem csúszhatnak szét; meglévő profilok regressziója védett.
- [ ] Offline teljes workflow helyben és CI-ben sikeres, HU/EN nevekkel.
- [ ] A dokumentáció, súlyozási indoklások és roadmap frissült.

## Kockázatok és visszaállítás

Önkényes műfaji elvárások, túl sok azonos működésű név, alias-kompatibilitás.
Új súlyozás nem változtathat meg régi értékelést észrevétlenül. Visszaállításnál
az új profilra hivatkozó meglévő kártyák kezelését előre meg kell határozni.

## Nyitott kérdések

- Mely új profilok kerüljenek az első csomagba, milyen indokolt relevanciákkal?
- A Thriller kapjon-e saját nevet közös Horror-súlyozással?
- Két azonos súlyozású név egyszerre választható legyen-e a három helyre?
- Az első csomag konkrét profiljai még pontosítandók; célrelease: `1.7.0`.

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-11-03 | Külön QoL-terv, célverzió nélkül. | A profilbővítés önmagában is hasznos, nem függ az AniList-feature-től. |
| 2026-11-03 | Mecha saját név, közös Sci-fi súlyozás tervezett. | Tulajdonosi pontozási szemlélet; nem minden névhez kell új vektor. |

## Megvalósítási napló

Tervezési jóváhagyás: 2026-11-03, célrelease `1.7.0`, státusz `accepted`.
Implementáció nem indult; a konkrét profilcsomag és súlyozások review-ja megmarad.

