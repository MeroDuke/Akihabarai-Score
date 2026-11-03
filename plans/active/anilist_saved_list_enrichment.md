# AniList-kiegészítés mentett listákhoz — előzetes feltételtisztázással

- Plan ID: `PLAN-020`
- Status: `proposed`
- Target release: `1.6.0` (feltételes jelölt, nem vállalt implementáció)
- Type: `feature`
- Priority: `medium`
- Created: `2026-11-01`
- Last reviewed: `2026-11-03`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)
- Kapcsolódó alap: [PLAN-019 helyi listamentés](local_tier_list_save_load.md)

## Probléma

A helyi listamentés AniList nélkül önállóan használható kell maradjon.
Opcionális bővítésként felmerült a korábban kiválasztott anime azonosítása
és borítójának friss lekérése, de nem tisztázott, milyen AniList-eredetű
mezők tárolhatók, meddig és milyen feltételekkel.

## Cél

Az `1.6.0` funkcióbővítő kiadás feltételes jelöltje. A terv `proposed`
marad: megfelelő írásos válasz, stabil `1.4.0` helyi mentési alap és a válasz
alapján pontosított scope külön tulajdonosi jóváhagyása szükséges.
Ha nincs válasz vagy nem megengedett a működés, más funkcióbővítő elemet
választunk az `1.6.0`-ba; nem tekintjük a hallgatást engedélynek.
Ez nem kapcsolatfelvételi vagy fejlesztésindítási engedély.

Először írásban tisztázni az AniListtel az engedett működést. Csak ezt követően,
javasolt célrelease és scope tulajdonosi elfogadásával kerülhet sor az opcionális
mentési kiegészítés fejlesztésére. Elutasítás is elfogadható kimenet; a helyi
mentés nem függhet az AniList együttműködésétől vagy rendelkezésre állásától.

## Nem cél

- Mostani kapcsolatfelvétel, implementáció vagy automatikus engedélykérés-küldés.
- Válasz hiányának engedélyként kezelése vagy korábbi feltételezett jogok rögzítése.
- Képadatbázis, katalógustükrözés, tömeges adatgyűjtés vagy rejtett szinkron.
- AniList review vagy jóváhagyás tényének állítása annak tényleges megtörténte nélkül.

## Jelenlegi állapot

A jelenlegi [lifecycle-dokumentum](../../docs/integrations/anilist_data_lifecycle.md)
runtime-only működést ír le. A PLAN-019 az integrációfüggetlen mentés javaslata.
Az AniListet ezzel kapcsolatban nem kerestük meg, válasz vagy engedély nincs.
A 2026-11-01-i nyilvános forrásokat és elérhetőségeket a PLAN-019 rögzíti;
végrehajtáskor a [hivatalos feltételeket](https://docs.anilist.co/guide/terms-of-use)
újra ellenőrizni kell.

## Tervezett megoldás

### Kötelező előfeltétel: írásos tisztázás

Tulajdonosi jóváhagyás után megkeressük az AniListet a hivatalosan feltüntetett
`contact@anilist.co` címen; szükség esetén a hivatalos Discordon kérünk útbaigazítást.
A megkeresés csomagja:

- Repository és termékleírás: desktop-first pontozó és Tier Board, opcionális
  AniListtel, saját értékelésekkel és helyi mentéssel; valós működés, nem pusztán címke.
- Mezőnkénti táblázat: felhasználói cím, API-ból választott cím, AniList-ID,
  egyéb párosítási adat, borító-URL és képadat. Kérdés, mi tárolható, mennyi
  ideig, helyi hordozható fájlban megosztható-e, és mi kizárt.
- Mentés–betöltés–felhasználó által indított online lekérés adatfolyama;
  nincs képtárolás tervezve, de a válasz alapján további korlátok is lehetnek.
- Kérdés az AS kiegészítő eszközként való elfogadhatóságáról, a versengő
  list/tracker korlátozásról, attribúcióról, API-terhelésről és frissítési szabályokról.

A válasz, dátum, válaszadó szerepe, engedett/tiltott/bizonytalan mezők és
feltételek döntési rekordba kerülnek. Magánlevelezést vagy személyes adatot
nem publikálunk automatikusan. Kétértelmű válasznál pontosítás szükséges;
válasz nélkül az AniList-persistencia nem indul el.

### Felajánlott szolgáltatói review

A tulajdonos kész átadni a tervet, mintamentést, adatfolyamot, tesztbizonyítékot,
majd konkrét implementációt commitazonosítóval ellenőrzésre. Megkérdezzük,
vállalnak-e ilyen review-t, milyen formában és szükséges-e kiadás előtt.
Nem feltételezünk rendelkezésre állást vagy teljes kódauditot. Review hiányában
csak akkor haladhatunk, ha az írásos használati tisztázás egyértelmű és nem
szab review-kötelezettséget; ha előírják, annak teljesülése külön kiadási kapu.

A szolgáltatói visszajelzés nem általános jogi tanúsítás, és nem feltétlenül
terjed ki a képek más jogosultjainak jogaira. Csak az igazolt scope-ra hivatkozunk.

### Feltételes implementáció

A stabil PLAN-019 alapra opcionális provider-hivatkozás épülhet, kizárólag az
engedett mezőkkel. Betöltés továbbra is hálózatfüggetlen; online kiegészítés
külön felhasználói művelet, korlátozott párhuzamossággal, rate-limit kezeléssel.
Hiba, Offline/letiltott integráció vagy törölt anime esetén a saját lista ép marad.
Cím alapján nincs automatikus első-találat párosítás bizonytalan egyezésnél.

## Platform- és kompatibilitási szempontok

A szolgáltatói részek nélkül is használható, verziózott fájlformátum. Offline
és letiltott AniList állapotban nincs API-hívás. Az aktuális adatkezelési
dokumentáció csak ténylegesen implementált változáskor frissül.

## Tesztstratégia

- Előkészítés: mezőmátrix és adatfolyam összevetése az írásos válasszal.
- Implementáció esetén unit tesztek az engedélyezett mezőlistára és kizárt adatokra.
- Teljes Qt workflow: saját lista mentése, újraindítás, offline betöltés,
  felhasználói online kiegészítés fake API-val; hibánál a lista megmarad.
- 403/429, megszakítás, hiányzó vagy kétértelmű találat és részleges képhiba tesztje.
- Helyi offscreen workflow és CI zöld; valós API-próba csak külön jóváhagyással.
- Ha szolgáltatói review szükséges, a tesztelt commit és az elfogadott commit egyezzen.

## Elfogadási feltételek

- [ ] Célrelease és feltételes implementációs scope tulajdonosi elfogadása kész.
- [ ] AniList írásos tisztázása rendelkezésre áll, a mezőszintű korlátok egyértelműek.
- [ ] A review-felajánlás és az arra kapott válasz, illetve előírások dokumentáltak.
- [ ] Negatív válasz/hiányzó tisztázás esetén a bővítés halasztása vagy elvetése rögzített.
- [ ] Ha bevezethető: engedett mezők, offline működés és hibatűrés tesztelt.
- [ ] Ha bevezethető: teljes workflow helyben és CI-ben sikeres; előírt review kész.
- [ ] Dokumentáció és roadmap az igazolt döntést/eredményt tükrözi.

## Kockázatok és visszaállítás

Válasz elmaradása, feltételek változása, szolgáltatáskiesés vagy túl tág
jóváhagyás-értelmezés. A bővítés külön kapcsolható marad; a saját értékelések
visszaállítását nem köthetjük hozzá. A szolgáltatói adatok eltávolításának és
régi fájlok kezelésének szabályát implementáció előtt meghatározzuk.

## Nyitott kérdések

- Vállal-e az AniList állásfoglalást és opcionális implementáció-review-t?
- Mely mezők, megőrzési idők, megosztási és lekérési módok elfogadhatók?
- Kiadható-e a helyi alap külön, és milyen Online/Offline UX-szel?
- Az `1.6.0` feltételei teljesülnek-e, vagy más feature-t kell választani?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-11-01 | Külön AniList társterv készült, `TBD` célverzióval. | Az önálló mentési alap nem függhet a szolgáltatói bővítéstől. |
| 2026-11-01 | Írásos AniList-tisztázás az implementáció előfeltétele; review felajánlható. | A tulajdonos kész ellenőrzésre átadni a megoldást, a szolgáltató részvételét nem tekintjük biztosítottnak. |
| 2026-11-03 | Feltételes jelölt az `1.6.0`-ra, státusz továbbra is `proposed`. | A tulajdonos a sorrendet elfogadta, a feature nem ígéret: írásos tisztázás és külön végleges scope-jóváhagyás nélkül más tartalom szükséges. |

## Megvalósítási napló

Megkeresés és implementáció még nem indult el.
