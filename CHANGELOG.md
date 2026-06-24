# Changelog

A projekt fontosabb változásainak összefoglalója.

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
