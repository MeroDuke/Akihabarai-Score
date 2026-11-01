# Helyi Tier-lista mentése és visszatöltése

- Plan ID: `PLAN-019`
- Status: `proposed`
- Target release: `TBD`
- Type: `feature`
- Priority: `medium`
- Created: `2026-11-01`
- Last reviewed: `2026-11-01`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

A Tier lista jelenleg munkamenet-alapú. A képexport a megosztható eredményt
őrzi meg, nem a tovább szerkeszthető pontozási bemeneteket és kártyaállapotot.
A felhasználó később vagy másik gépen is folytatná a saját munkáját.

## Cél

Önálló, helyi fájlos mentés és visszatöltés AniList, internet, felhasználói
profil, adatbázis és szerver nélkül. A javasolt irány rögzített, célrelease és
végleges UX még nincs elfogadva; a terv nem indít fejlesztést.

## Nem cél

- AniList-adatok tartós mentése, API-válasz, médiaazonosító, borító-URL vagy
  kép beágyazása az alapváltozatba.
- Automatikus online újrapárosítás vagy borító-visszatöltés.
- Fiók, felhőszinkron, szerveroldali mentés vagy teljes alkalmazás-session mentése.
- A jelenlegi AniList runtime-only politika átírása ezzel a tervezési bejegyzéssel.

## Jelenlegi állapot

A kártyaadatok és pontozási bemenetek elkülönülnek a Qt képi állapotától:
`app/core/models.py` tartalmazza a `TierCardData` és `TierCardInputSnapshot`
modelleket. Ez használható alap, nem kész fájlformátum vagy mentési API.
A modellek AniList-azonosítót és AniListből kiválasztott címet is hordozhatnak,
ezért teljes objektumaik automatikus szerializálása nem megfelelő megoldás.
A diagnosztikai log nem visszatölthető munkamenet és nem mentési adatforrás.

## Tervezett megoldás

- Verziózott, validálható helyi formátum kizárólag engedélyezett mezőkkel.
- Saját, kézzel megadott címek, kártyatípusok, tierek és sorrend mentése.
- Adatvezérelt kártyák nyolc pontszámának, profiljainak és súlyainak megőrzése,
  hogy betöltés után is szerkeszthetők legyenek; szabadkezes elrendezés megőrzése.
- Több külön fájl és másik gépen történő folytatás támogatása.
- Betöltés hálózati hívás nélkül; sérült vagy ismeretlen formátum nem írhatja
  felül részlegesen az aktuális listát. Fájlmentési hiba ne tegye tönkre a
  korábbi érvényes mentést.
- Saját kártyacím és opcionális szolgáltatói kapcsolat szerkezeti szétválasztása.
  Bővíthető formátum megengedett, de az AniList-specifikus rész kezdetben üres.

### Online eredetű kártyák — kiadás előtti döntési kapu

Az AniListből kiválasztott cím nem válik automatikusan kézzel megadott saját
adattá attól, hogy a címszerkesztőben látható. Megvalósítás előtt eldöntendő,
hogyan kezeljük az ilyen kártyákat mentéskor és az Online mód későbbi
bekapcsolásakor. Nem veszítünk el csendben kártyát/adatot, és nem ígérünk
teljes vizuális helyreállítást, ha a képek nem állíthatók vissza.

Az önálló mentés és az AniList-kiegészítés két fejlesztési lépcső lehet, de
ezek nem szükségképpen két külön release. Az első önálló kiadásának UX-ét és
korlátait tulajdonosi review hagyja jóvá.

### Későbbi AniList-bővítés — nem vállalt scope

Külön társterv: [PLAN-020](anilist_saved_list_enrichment.md), célverzió `TBD`.
Az írásos szolgáltatói tisztázás és a felajánlott review keretét ez kezeli.

Opcionális szolgáltatói hivatkozás és felhasználó által indított futásidejű
borító-helyreállítás csak külön lifecycle/feltétel-review után kerülhet elő.
A mentés továbbra sem függhet a szolgáltató rendelkezésre állásától.

A 2026-11-01-i kutatáskor a jelenlegi
[API-feltételek](https://docs.anilist.co/guide/terms-of-use) tiltják az API
backup/adattárolási szolgáltatásként használatát, a tömeges adatgyűjtést és a
versengő, nem kiegészítő szolgáltatásokat; az utóbbi a médiaadatokra is vonatkozik.
Nem találtunk külön, egyértelmű rendelkezést néhány kiválasztott cím/ID helyi
megőrzésére. Ez nem engedély és nem teljes megfelelőségi állásfoglalás.
A régi GitBook-oldal kivételszövegére nem alapozunk; végrehajtáskor új ellenőrzés
szükséges. A cím szerzői jogi helyzete önmagában nem dönti el az API-feltételeket.

Tisztázási lehetőség: `contact@anilist.co`, az
[AniList hivatalos GitHub-oldalán](https://github.com/anilist) feltüntetett cím;
illetve [hivatalos Discord](https://discord.com/invite/anilist).
Külön kérdés a cím, az ID megőrzése, a későbbi kérés és az AS kiegészítő
pontozóeszközként történő besorolása. Megkeresést nem küldtünk.

## Platform- és kompatibilitási szempontok

Windows elsődleges, Linuxon is olvasható formátum. Unicode-címek, HU/EN
nyelvváltástól független stabil profil-/dimenzióazonosítók szükségesek.
Profil- vagy pontozási szabályváltozás esetére verziókezelés és egyértelmű
kompatibilitási viselkedés kell. Importált fájlt nem megbízható bemenetként
kezelünk: típus-, érték- és méretellenőrzés, végrehajtható szerializálás nélkül.

## Tesztstratégia

- Unit/low-level round-trip tesztek az engedélyezett mezőkre, scored/manual
  kártyákra, Unicode-ra, sorrendre és a harmadik féltől származó mezők kizárására.
- Hibás, túl nagy, ismeretlen verziójú fájl, hiányzó profil és írási hiba vizsgálata.
- Teljes felhasználói workflow: offline lista összeállítása vezérlőkkel,
  mentés, új alkalmazáspéldányban betöltés, szerkesztés és újramentés.
- Letiltott AniListtel és tiltott hálózattal is sikeres workflow; későbbi
  Online módváltás az elfogadott döntési kapu szerint viselkedik.
- Qt-tesztek helyben offscreen módban, majd CI; kézi fájlátviteli próba.

## Elfogadási feltételek

- [ ] Tulajdonos által elfogadott célrelease és részletes mentési UX készült.
- [ ] Az online eredetű kártyák mentésének és a módváltásnak a szabálya tisztázott.
- [ ] Saját scored/manual adatok és elrendezés hálózat nélkül visszatölthetők és szerkeszthetők.
- [ ] A mentés nem tartalmaz AniList-címet/ID-t, képet, URL-t vagy API-választ az alap scope-ban.
- [ ] Verziókezelés és hibás import/mentés adatvesztés nélküli kezelése tesztelt.
- [ ] A releváns low-level és teljes workflow-tesztek helyben és CI-ben zöldek.
- [ ] A korlátok a felületen és útmutatóban egyértelműek; dokumentáció és roadmap frissült.

## Kockázatok és visszaállítás

Hibás import, részleges írás, profilváltozás és online adatok véletlen mentése
adatvesztést vagy policy-sértést okozhat. Explicit mezőlista, validált teljes
betöltés és biztonságos fájlcsere szükséges. Az új funkció visszavonása nem
törölheti a felhasználó már elkészített mentési fájljait.

## Nyitott kérdések

- Célrelease, fájlkiterjesztés és végleges UX.
- Betöltés lecserél vagy összefésül; hogyan kezeljük a nem mentett aktuális munkát?
- Mit teszünk online eredetű kártyák és nem támogatott szolgáltatói mezők esetén?
- Újraszámolás vagy korábbi eredmény megőrzése megváltozott pontozási szabályoknál?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-11-01 | Helyi listamentés felvéve javaslatként, célverzió nélkül. | A saját munka folytatásához nem szükséges profil, szerver vagy AniList. |
| 2026-11-01 | AniList nélküli alap, később külön értékelt opcionális kiegészítés. | Független működés; az integrációs feltételeket és a kiadási teljességet nem tekintjük eldöntöttnek. |

## Megvalósítási napló

Még nem indult el.
