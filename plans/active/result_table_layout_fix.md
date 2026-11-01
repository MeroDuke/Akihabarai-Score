# Eredménytáblázat tördelése és másolásgomb elhelyezése

- Plan ID: `PLAN-018`
- Status: `in-progress`
- Target release: `1.0.1`
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

Az 1.0.1-ben az eredménytáblázat és a másolásgomb átfedésmentes, használható
elrendezése; minden dimenzió és érték olvasható vagy szabályosan görgethető.

## Nem cél

- Teljes eredménypanel-újratervezés.
- Scoring, kerekítés vagy a vágólapra másolt adatformátum módosítása.
- A későbbre hagyott általános Linux vizuális rendbetétel előrehozása.

## Jelenlegi állapot

A hiba offscreen Qt layout-tesztben reprodukált: 420×500-as fix befoglalóban
a nyolc sort tartalmazó táblázat alja 463, a másolásgomb teteje 434 volt.
A táblázat a teljes tartalmát minimum magasságként kérte, így túlcsordult
a kiosztott helyen. A `32376f7` commit egyszerre vezette be ezt a minimumot
és a felső eredménykártya fix magasságát; a későbbi kétsoros uniform sorok
tovább növelték a helyigényt (`595247e`). A képernyőkép pontos eredeti
körülményeit még kézi átvételben kell ellenőrizni.

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
| 2026-11-01 | Áthelyezve az `1.0.1` hotfix scope-jába; implementáció engedélyezve. | A tulajdonos a `1.0.1/result-table-layout` ágnevet kérte; nincs `hotfix/` prefix. Merge és kiadás külön jóváhagyás. |

## Megvalósítási napló

- Ág: `1.0.1/result-table-layout`, a stabil `origin/main` alapján.
- Reprodukció: a célzott layout-regressziós teszt javítás előtt elbukott
  a táblázat és gomb átfedésén, a minimumkényszer eltávolítása után átment.
- A felső eredménykártya kompakt méretezése és a uniform kétsoros alapmagasság
  megmarad; a táblázat szűk helyen görgethető, tág helyen minden sora látható.
- Új tesztek: három betűméretes, hosszabb összefoglalós panel-regresszió és
  teljes ablakos pontozás–átméretezés–HU/EN váltás–részletes másolás workflow.
- A két platform CI push-szűrője az engedélyezett `1.0.1/**` ágat is figyeli.
- Helyi ellenőrzés: `QT_QPA_PLATFORM=offscreen; python -m pytest -q`:
  **628 passed**. A workflow-teszt kivárja a másolásgomb valódi, időzített
  visszajelzésének végét, hogy a tesztablak bezárása ne hagyjon függő callbacket.
- Kézi csomagolt átvétel és platform-CI még hátravan; a terv nem lezárt.
- Az első javítás (`e4b7053`) Windows- és Linux-CI-je sikeres:
  [Windows](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41301324047),
  [Linux](https://github.com/MeroDuke/Akihabarai-Score/actions/runs/41301324022).
- Tulajdonosi visszajelzés alapján a görgetés biztonsági tartalék marad:
  a panel három és az eredménykártya két térköze 10-ről 6 logikai pixelre
  csökken (összesen 20 pixel helynyereség). Betűméret és sormagasság nem változik.
  Új határeset-teszt azonos ablakméretnél ellenőrzi, hogy a kompakt térközzel
  minden sor elfér, a korábbi térközzel görgetés szükséges. A végleges vizuális
  elfogadás és a kiegészítés platform-CI-je még hátravan.
- További kézi visszajelzés alapján reprodukált második gyökérok: hosszú cím
  megadása, törlése és reset után a rövid tartalmú kártya 131 helyett 182
  logikai pixel magas maradt. A korábbi minimumkorlátok visszacsatolódtak az új
  méretbecslésbe. Friss tartalom mérése előtt a summary és kártya régi korlátait
  feloldjuk, majd az aktuális méretet állítjuk be. Teljes UI-regresszió ellenőrzi
  a hosszú cím → üres cím → reset és ismételt HU/EN váltás stabil geometriáját.
- Következő kézi próba: a kétsoros uniform sorok extra függőleges ráhagyása
  4-ről 2 logikai pixelre csökken, betűméret-változás nélkül. Ez soronként
  legfeljebb 2, nyolc sornál legfeljebb 16 pixel további nyereség; a Qt alap-
  sormagasság alsó korlát marad. Három betűméretre külön regressziós teszt készült.
- Következő elrendezési változat: a táblázat maximuma a fejléc, a sorok, a keret
  és szükség esetén a vízszintes görgetősáv magasságából áll. Minimumot nem
  kényszerítünk. A fennmaradó hely a táblázat és az alul maradó másolásgomb
  közötti üres terület; nagy ablakban nincs üres táblázatviewport. A felső
  tartalom hosszával a táblázat teteje továbbra is mozoghat, ez nem fix felosztás.
  Panel- és teljes HU/EN másolási workflow ellenőrzi a viewport tartalmi határát.
