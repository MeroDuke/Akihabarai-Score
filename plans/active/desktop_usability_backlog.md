# Desktop usability és felfedezhetőségi backlog

- Plan ID: `PLAN-007`
- Status: `proposed`
- Target release: `TBD`
- Type: `usability`
- Priority: `medium`
- Created: `2026-09-29`
- Last reviewed: `2026-09-29`
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## Probléma

A closed-beta visszajelzés és a fejlesztés közbeni használat több lehetséges
felfedezhetőségi és platformfüggő QoL-javítást vetett fel. Ezek bizonyítottsága
és értéke eltérő, ezért nem kezelhetők egyetlen kész feature-ként vagy
automatikus release-vállalásként.

## Cél

Egy ellenőrzött gyűjtő, amelyből későbbi QoL release-ekhez külön, kis és
tesztelhető elemek választhatók. Minden kiválasztott elem saját scope-ot,
elfogadási feltételeket és regressziós workflow-t kap.

## Nem cél

- A backlog teljes tartalmának automatikus megvalósítása.
- Az `1.0.0` bővítése nem kritikus UI-változtatásokkal.
- A desktop UI teljes újratervezése.
- WebUI usability döntések meghozása.

## Jelenlegi állapot

Az első usability teszt több kérdést felvetett, de további korroboráló
visszajelzés nem érkezett. Debian 13.6 alatt az alkalmazás működött, de egyes
hosszú magyar alsó gombfeliratok eltérő Qt fontmetrikák miatt levágódtak. Az
AniList inline információs sávja és az új kereséskor induló normál újrapróbálás
már megfelel a jelenlegi szándéknak.

## Tervezett backlog

- Az elsődleges következő művelet vizuális kiemelésének vizsgálata.
- Az Online/Offline állapot érthetőbb megjelenítésének vizsgálata.
- Első indításos onboarding a későbbi User Guide alapján.
- Kontextuális súgó, tooltip és üres állapotok vizsgálata.
- A funkciók README nélküli felfedezhetőségének javítása.
- Linux alsó gombsor és hosszú lokalizált feliratok adaptív kezelése.
- Babel stresszkatalógusos és szükség szerint Linux vizuális ellenőrzés.
- Jövőbeli closed-beta visszajelzések gyűjtése és összevetése.

## Platform- és kompatibilitási szempontok

Windows marad az elsődleges desktop célplatform. Linux-javítás nem törheti el a
Windows layoutot, és fordítva. A kiválasztott UI-változtatást a támogatott
minimális ablakméreten, magyar és angol felirattal kell ellenőrizni.

## Tesztstratégia

Minden kiválasztott elemhez megvalósítás előtt külön tesztstratégia készül.
Kötelező a releváns low-level teszt és legalább egy teljes felhasználói
workflow/regressziós teszt. A Qt-tesztek helyben offscreen módban, CI előtt
zölden futnak.

## Elfogadási feltételek

- [ ] A kiválasztott elem külön elfogadott scope-ot és célverziót kapott.
- [ ] Reprodukálható probléma vagy tulajdonosi UX-döntés indokolja.
- [ ] A desktop workflow nem regresszálódott.
- [ ] A releváns helyi és CI-tesztek sikeresek.
- [ ] A dokumentáció és a roadmap frissült.

## Kockázatok és visszaállítás

A gyenge bizonyíték alapján végzett UI-változtatás ronthatja a megszokott
workflow-t. Ezért az elemek nem kerülnek csoportosan fejlesztésbe, és minden
változtatás külön visszavonható marad.

## Nyitott kérdések

- Mely ötleteket erősítik meg további felhasználói visszajelzések?
- Mi oldható meg User Guide-dal, és mi igényel alkalmazáson belüli UI-t?

## Döntési napló

| Dátum | Döntés | Indoklás |
| --- | --- | --- |
| 2026-09-29 | Az usability ötletek közös backlogba kerülnek. | Nem minden ötlet értéke vagy bizonyítottsága azonos. |
| 2026-09-29 | A Linux szövegvágás tartalék QoL-jelölt. | A funkciók működnek, Windows az elsődleges platform. |

## Megvalósítási napló

