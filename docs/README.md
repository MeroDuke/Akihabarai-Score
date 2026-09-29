# Műszaki dokumentáció

A `docs/` könyvtár a termék és az architektúra jelenlegi, tényleges állapotát
írja le. Jövőbeli fejlesztési szándékok és release-tervek a gyökérben lévő
[`ROADMAP.md`](../ROADMAP.md), illetve a [`plans/`](../plans/README.md)
könyvtár alatt találhatók.

## Tartalom

### Architektúra

- [Desktop adapter boundary](architecture/desktop_adapters.md)
- [Runtime localization](architecture/localization.md)
- [Logging boundaries](architecture/logging_boundaries.md)
- [Crash diagnostics](architecture/crash_diagnostics.md)

### Integrációk

- [AniList runtime és adat-életciklus](integrations/anilist_data_lifecycle.md)

### Licencelés és megfelelőség

- [Alkalmazáslicencelés](compliance/application_licensing.md)
- [Licenc- és disztribúciós audit](compliance/license_compliance_audit.md)
- [Runtime licenckötelezettségek](compliance/license_obligations.md)
- [Release-források elérhetősége](compliance/release_source_availability.md)
- [Qt/PyQt runtime GPLv3 megfelelőség](compliance/qt_runtime_gpl_compliance.md)

### Döntési rekordok

- [Alkalmazáslicenc-döntés](decisions/application_license_decision.md)
- [Desktop-first termékirány](decisions/desktop_first_product_direction.md)

### Projektpolicyk

- [Brand policy](policies/brand_policy.md)
- [Alkotói irányelv](policies/creator_guidelines.md)

### Validációs rekordok

- [Pre-production validáció](validation/preproduction_validation.md)

## Elhelyezési szabály

- Ide csak jelenleg igaz architekturális, integrációs, üzemeltetési,
  megfelelőségi, döntési vagy validációs dokumentum kerüljön.
- Tervezett változtatás a `plans/` könyvtárba kerül.
- Egy lezárt fejlesztési terv a `plans/completed/` könyvtárban marad történeti
  és döntési bizonyítékként.
- Fájl áthelyezésekor minden forráskód-, workflow-, teszt- és Markdown-hivatkozást
  ugyanabban a változtatásban frissíteni kell.
