# Desktop-first termékirány

## Döntés

Az Akihabarai Score elsődleges és önálló terméke a desktop alkalmazás. A
desktop változat a jelenlegi funkciókészletével működő, közel kész termék; az
`1.0.0` kiadás ennek stabil baseline-ja lesz.

A webes Pontozó opcionális, kísérleti és tanulási célú kiegészítés. Sikere nem
feltétele a desktop projekt sikerének, és elmaradása nem számít a Score projekt
kudarcának.

## Prioritási sorrend

1. Desktop kritikus hibák és regressziók.
2. Desktop stabilitás, diagnosztika és karbantarthatóság.
3. Desktop felhasználói funkciók.
4. Desktop Quality of Life fejlesztések.
5. Olyan közös belső fejlesztés, amely önmagában a desktop számára is értékes.
6. Webes Pontozó és más webspecifikus fejlesztések.
7. Távoli, opcionális integrációs kísérletek.

## Következmények

- Webes igény nem ronthat el működő desktop workflow-t.
- A Core nem alakítható át kizárólag azért, hogy a WebUI fejlesztése
  kényelmesebb legyen.
- A desktop release-ek nem várnak a webprojektre.
- A desktop alkalmazás önállóan buildelhető, tesztelhető és kiadható marad.
- A web felhasználhatja a desktopban már ésszerűen leválasztott szabályokat,
  de a böngészős felület saját, webnatív workflow-t kaphat.
- A közös pontozási szabályoknak konzisztensnek kell maradniuk, de a két UI-nak
  nem kell képernyőről képernyőre vagy vezérlőről vezérlőre megegyeznie.
- A hobbi projektet nem hajtja mesterséges határidő vagy minimális
  release-méret.

## Elfogadott fejlesztési irányok

- Az `1.0.0` utáni első desktop fejlesztés a kereszt-réteges tracing és
  diagnosztika.
- A jelenlegi működés visszaalakítása belső termékspecifikációvá, majd abból
  felhasználói útmutató készítése.
- Később a User Guide tartalmából kiválasztott, alkalmazáson belüli onboarding
  és kontextuális segítség vizsgálata.
- A használhatósági ötletek gyűjtő backlogban maradnak, és csak külön döntéssel
  kerülnek release-scope-ba.
- A Linux UI ismert szövegvágása alacsony prioritású desktop QoL-jelölt.
- A webes Pontozó csak iteratív, webnatív szeletekben fejlődhet, a saját
  projektjének és roadmapjének megfelelően.

## AniList-helyreállási irány

Az AniList-hibakezelés szándékosan egyszerű marad:

- az inline információs sáv közli az aktuális hibát;
- a háttérben nincs periodikus vagy önálló automatikus retry;
- amikor a felhasználó újra címet keres, a program normál új kérést indít;
- sikeres későbbi kéréskor a hibaállapot megszűnik;
- a kliens nem terheli szükségtelenül az AniList API-t.

Ez jelenleg védendő meglévő viselkedés, nem külön elfogadott feature.

## Tudatosan elvetett irányok

Az alábbiak nem halasztott roadmap-elemek, hanem elvetett termékirányok:

- publikus vagy belső SDK-termék;
- külső fejlesztőknek ígért kompatibilis Core API;
- CLI kliens;
- generatív AI-alapú Strengths funkció.

A UI-független Core továbbra is értékes belső desktop architektúra, de nem
alakul önálló SDK-vá.

## Távoli, nem vállalt lehetőségek

- OBS-integráció, lehetőleg először browser source vagy overlay formájában;
- Discord bot, kizárólag későbbi konkrét igény esetén;
- profilhoz kötött session- és pontozásmentés;
- AI-alapú GitHub issue-triage és hotfix-előkészítési kísérlet.

Ezek egyike sem elfogadott release-scope.

## Döntési dátum

2026-09-29
