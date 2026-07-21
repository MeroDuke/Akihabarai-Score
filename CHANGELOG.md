# Changelog

A projekt fontosabb változásainak összefoglalója.

## [0.21.0] - 2026-07-21

### Added

- A Tier listához adott adatvezérelt kártyák kattintással újra megnyithatók és szerkeszthetők.
- A szerkesztő visszatölti a kártyához mentett profil-mix módot, profilokat, súlyokat és dimenzióértékeket.
- A szerkesztett kártyát erős kék keret és `SZERK.` jelvény azonosítja; a művelet menthető vagy megszakítható.

### Changed

- Szerkesztés mentésekor az eredeti kártya frissül, megőrzi belső azonosítóját, és nem keletkezik belőle másolat.
- A szerkesztés alatt álló kártya továbbra is megfordítható, de az egyedi törlési gombja a munkamenet lezárásáig rejtve marad.
- Szabadkezes módban az adatvezérelt kártyákra kattintás kizárólag a mozgatási folyamat része; nem nyit szerkesztést és nem vált vissza adatvezérelt módba.

### Fixed

- A teljes Tier lista megerősített törlése szabályosan lezárja az aktív kártyaszerkesztést, így a felület nem marad nem létező kártyához tartozó mentési vagy megszakítási állapotban.
- A kártya más törlési útvonalon történő megszűnése is automatikusan felszabadítja a szerkesztési állapotot.
- A Tier lista törlése megtartja az aktuális Adatvezérelt vagy Szabadkezes alkalmazásmódot.

### Documentation

- Az AniList runtime- és adat-életciklus dokumentációja kiegészült a szerkeszthető adatvezérelt kártyák session-only bemeneti snapshotjával, runtime borítókezelésével és szerkesztési állapotának lezárásával.

### Technical

- A `TierCardData` opcionális, sorosítható pontozási bemeneti snapshotot kapott; a borítóképek továbbra is kizárólag runtime `QPixmap` állapotban maradnak.
- A kártyaszerkesztést, a szabadkezes módhatárt és a törlési védőhálót kibővített automata regressziós tesztek ellenőrzik.

## [0.20.0] - 2026-07-18

### Added

- Kísérleti Linux x86_64 kiadás került a GitHub Releases csomagjai közé.
- A Linux build automatikus tesztelést, PyInstaller-csomagolást és grafikus környezetben végzett indítási smoke tesztet kapott.

### Changed

- Kikapcsolt AniList integráció esetén az „Összes kártya megfordítása” gomb nem jelenik meg; a Tier lista törlési és képmásolási műveletei változatlanul elérhetők maradnak.
- A GitHub Actions workflow-k támogatott, Node.js 24-alapú action-verziókra frissültek.

### Documentation

- A README kiegészült a Linux kiadás elérhetőségével és támogatási szintjével.

### Technical

- Az alkalmazásindítás platformfüggő Windows-integrációja Linuxon biztonságosan kihagyásra kerül.
- A Windows és Linux buildet, teszteket, indítási smoke teszteket és platformonkénti csomagolást külön GitHub Actions workflow-k ellenőrzik.

## [0.19.1] - 2026-07-17

### Fixed

- Javítva a GitHub #8 hiba: Szabadkezes módban a kártyák teljes felülete használható beszúrási célként; a kártya bal felére ejtés elé, a jobb felére ejtés mögé helyezi az áthúzott kártyát.

## [0.19.0] - 2026-07-16

### Added

- Új kétállású Adatvezérelt / Szabadkezes módváltó.
- Szabadkezes módban offline címmel vagy AniList-borítóval is létrehozhatók pontszám nélküli Tier kártyák.
- A Szabadkezes mód élő, pontszám nélküli kártya-preview-t biztosít.
- A mentett kártyák Szabadkezes módban drag & drop módszerrel mozgathatók a tierek között és tieren belül.
- Húzás közbeni cél-tier- és beszúrási pozíció-jelölés, automatikus lista-scroll, valamint sikeres és elutasított drop-visszajelzés került a felületre.

### Changed

- Szabadkezes módban a pontozási vezérlők letiltásra, az Eredmény panel elrejtésre kerül, a Tier lista pedig kitölti a felszabaduló helyet.
- A score, flip vezérlők és pontozáshoz kötött műveletek Szabadkezes módban nem jelennek meg vagy nem használhatók.
- Adatvezérelt módba visszaváltva a score-os kártyák a konfigurált tierhatárok szerint visszarendeződnek, tieren belül csökkenő pontszámsorrendben.
- A pontszám nélküli manuális kártyák módváltáskor a felhasználó által választott tierben maradnak, a score-os kártyák után.
- Az utolsó adatvezérelt szerkesztési állapot — cím, online/offline mód, AniList-kiválasztás és runtime borító — munkameneten belül visszaáll.
- A Reset megtartja az aktuális alkalmazásmódot és nem törli a Tier listát.
- A Tier lista módváltáskor és scrollbar-megjelenéskor újratördeli a kártyákat a ténylegesen látható terület alapján.

### Fixed

- Javítva a GitHub #7 hiba: üres AniList keresési eredménynél nem marad nyitva üres autocomplete lista.
- A Tier lista scrollbarja nem takarja el többé a jobb szélső kártyák vezérlőit.
- Adatvezérelt módba visszatérve nem keveredik a Freehandben utoljára megadott cím a korábbi pontozási értékekkel.

### Documentation

- Az AniList adat-életciklus dokumentáció kiegészült a Freehand runtime snapshot és autocomplete-popup kezelésével.
- A README új Freehand mód fejezetet és frissített Tier lista funkcióleírást kapott.

### Technical

- Bevezetésre került a UI-független `TierCardData` kártyamodell; az AniList képek továbbra is kizárólag runtime widgetállapotban maradnak.
- A módváltás, drag & drop, sorrendezés, autoscroll, visszarendezés és AniList üres találati lista viselkedését új automata tesztek védik.
- A Freehand műveletek és módváltási állapotok strukturált logger-integrációt kaptak.

## [0.18.0] - 2026-07-12

### Changed

- A főablak működése kisebb, célzott service- és widget-modulokba lett kiszervezve.
- A pontozási, profilkeverési, címkezelési, eredménymegjelenítési, Tier lista és alkalmazásindítási útvonalak karbantarthatóbb belső szerkezetet kaptak.
- Az AniList integráció opcionális feature-határai egyértelműbbek lettek, a kikapcsolt állapothoz tartozó címkezelési útvonal védettebb lett.

### Fixed

- Javítva a „Tempó / epizódritmus” dimenzió hibás írásmódja a profilkonfigurációban és a dokumentációban.
- A Tier lista preview kártya nem fordul vissza automatikusan pontszámváltozáskor, ha a felhasználó előtte a hátoldalra fordította.
- Az Eredmény panel táblázata és gombelrendezése visszakapta a korábbi, 0.17.2-ben látott tördelést és scrollbar nélküli megjelenést.

### Documentation

- Új AniList adat-életciklus dokumentáció készült a feature opcionális jellegéről, adatkezelési határairól és kikapcsolási pontjairól.

### Technical

- A `main.py` mérete jelentősen csökkent, a főablak logikája tesztelhetőbb modulokra lett bontva.
- Új és frissített automata tesztek védik a magyar UI-feliratokat, a refaktorált főablak-delegálásokat, a Tier preview flip viselkedést és a verzió-metadata szinkront.
- A `pyproject.toml` csomagverziója szinkronba került az alkalmazás `APP_VERSION` értékével.

## [0.17.2] - 2026-06-25

### Changed

- A „Hozzáadás Tier listához” gomb csak megadott cím esetén aktív.

### Technical

- Új automata teszt ellenőrzi a Tier lista hozzáadás gomb címhez kötött állapotát.

## [0.17.1] - 2026-06-25

### Fixed

- Az AniList online címválasztás kezeli az API-ból érkező záró szóközöket, így az érintett címeknél is betöltődik a borítókép.

## [0.17.0] - 2026-06-24

### Added

- Új „Minden kártya törlése” funkció a Tier listához.
- Megerősítő ablak az összes mentett Tier kártya törlése előtt.

### Changed

- Az alsó akciógombok rendezettebb, következetesebb sorrendet kaptak.
- Az ablak alapértelmezett és minimum mérete a `config/ui.json` konfigurációba került.
- A „Minden kártya törlése” megerősítő ablak magyar szövegezése pontosabb lett.
- Az „Összes kártya megfordítása” gomb csak akkor aktív, ha van mentett, megfordítható Tier kártya.

### Fixed

- A Tier lista képként másolása nem indul el üres mentett lista esetén.
- A szöveges, borító nélküli Tier kártyák nem számítanak többé megfordítható kártyának.

### Technical

- Duplikált profile mix helper definíció eltávolítva.
- Új és frissített automata tesztek a Tier lista törlés, export, gombállapot és ablakméret konfiguráció viselkedéséhez.

## [0.16.0] - 2026-06-09

### Changed

- Az erősség/gyengeség összefoglaló most intelligensebben kezeli a szélsőséges értékeléseket.
- Ha minden dimenzió maximális pontszámot kap, a rendszer nem jelenít meg mesterséges „Gyengeség” elemet.
- Ha minden dimenzió minimális pontszámot kap, a rendszer nem jelenít meg mesterséges „Erősség” elemet.

### Tests

- Új automata tesztek az erősség/gyengeség edge case viselkedés ellenőrzésére.

## [0.15.0] - 2026-06-04

### Added

- GitHub Releases alapú automatikus verzióellenőrzés alkalmazásindításkor.
- Verzió gomb az alsó kezelősávban.
- Új verzió esetén piros, feltűnő vizuális jelzés a verziógombon.
- Kattintásra megnyíló GitHub Releases oldal.
- Új automata tesztek a verzióellenőrzéshez és a verziógomb működéséhez.

### Changed

- A „Részletes adatok másolása vágólapra” gomb átkerült az Eredmény panelbe, a részletes táblázat alá.
- Az alsó gombsor tisztább, feature-központú elrendezést kapott.

### Technical

- Új `update_check_service.py` service a GitHub Releases API lekérdezéséhez.
- A verzió-összehasonlítás `vX.Y.Z` / `X.Y.Z` formátumot kezel, tuple-alapú összehasonlítással.
- A verzióellenőrzés nem használ cache-t, és hiba vagy internetkapcsolat hiánya esetén nem akadályozza az alkalmazás indulását.
- Az alkalmazás továbbra sem tölt le automatikusan frissítéseket.
