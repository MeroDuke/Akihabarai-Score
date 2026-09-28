# Akihabarai Score roadmap

Ez a fájl a projekt tervezett irányainak rövid, release-szintű áttekintése.
A részletes célokat, döntéseket, kockázatokat és elfogadási feltételeket a
kapcsolódó `plans/` dokumentumok tartalmazzák.

A roadmapbe kerülés önmagában nem engedélyezi a fejlesztést, a release-t, a
tag létrehozását vagy a `main` ágba történő merge-et.

## 1.0.0 — cél: 2027. március vége

### Elkészült

- [Natív crash-diagnosztikai alap](plans/completed/native-crash-diagnostics.md)
- [Csomagolt alkalmazás startup crash-védelme és hiteles smoke tesztje](plans/completed/packaged-startup-crash-protection.md)
- [UI-független alkalmazásmag refaktor](plans/completed/ui_independent_core_refactor.md)
- [Refaktor stabilizációs kapu](plans/completed/refactor_stabilization.md)

### Release előtt

- A closed beta alatt megerősített kritikus regressziók javítása.
- Az 1.0.0 verzió-, changelog- és felhasználói dokumentációjának véglegesítése.
- Teljes Windows- és Linux-integrációs/regressziós ellenőrzés.
- Zöld CI/CD és külön tulajdonosi jóváhagyás a `main` merge, majd a release előtt.

## Távolabbi irányok

- Webes frontend — külön részletes terv és célverzió még nincs elfogadva.

## Státuszjelölések

- **Javaslat:** vizsgálható irány, még nem vállalt release-scope.
- **Elfogadva:** a cél és a célverzió jóváhagyott, a megvalósítás még nem indult el.
- **Folyamatban:** aktív fejlesztés és tesztelés zajlik.
- **Blokkolva:** ismert akadály miatt nem haladhat.
- **Elhalasztva:** megőrzött terv, de nincs aktív célverziója.
- **Elkészült:** az elfogadási feltételek teljesültek és az eredmény dokumentált.
- **Törölve:** tudatosan elvetett terv, a döntés indoklása megmarad.
