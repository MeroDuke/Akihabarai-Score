# <Terv címe>

- Plan ID: `PLAN-XXX`
- Status: `proposed`
- Target release: `TBD`
- Type: `<feature|reliability|architecture|usability|compliance|documentation>`
- Priority: `<low|medium|high|critical>`
- Created: `YYYY-MM-DD`
- Last reviewed: `YYYY-MM-DD`
- Roadmap: [`ROADMAP.md`](../ROADMAP.md)

## Probléma

Milyen megfigyelt probléma, kockázat vagy igény indokolja a tervet? Hivatkozz
reprodukcióra, logokra vagy felhasználói visszajelzésre, ha rendelkezésre áll.

## Cél

Milyen felhasználói vagy műszaki eredményt akarunk elérni?

## Nem cél

Mi nincs benne ebben a változtatásban?

## Jelenlegi állapot

Mi működik már, és hol vannak a jelenlegi korlátok?

## Tervezett megoldás

A megközelítés, felelősségi határok és várhatóan érintett komponensek.

## Platform- és kompatibilitási szempontok

Windows, Linux, csomagolt alkalmazás, fejlesztői futtatás és szükséges
visszafelé kompatibilitás.

## Tesztstratégia

- Unit vagy low-level tesztek.
- Legalább egy teljes felhasználói workflow/regressziós teszt.
- Külső szolgáltatások mock/fake kezelése.
- Helyi ellenőrzés a CI-be történő feltöltés előtt.
- Platformspecifikus build- és smoke tesztek.

## Elfogadási feltételek

- [ ] <Mérhető feltétel>
- [ ] A releváns helyi tesztek sikeresek.
- [ ] A teljes workflow/regressziós teszt helyben sikeres.
- [ ] A releváns CI/CD workflow-k sikeresek.
- [ ] A dokumentáció és a roadmap frissült.

## Kockázatok és visszaállítás

Milyen regressziók lehetségesek, hogyan észleljük őket, és hogyan állítható
vissza biztonságosan a változtatás?

## Nyitott kérdések

- <Még eldöntendő kérdés>

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| YYYY-MM-DD | A terv létrejött. | <Indok> |

## Megvalósítási napló

Kapcsolódó branch, commit, CI futások, manuális ellenőrzések és a tervtől való
eltérések. A megvalósítás megkezdéséig maradjon üres.
