# UI-independent core refactor completion

## Status

The pre-WebUI refactor is complete on `feature/ui-independent-core`.

This document closes the refactor phase only. It does not authorize or perform
a merge to `main`, a release, runtime language switching, or WebUI
implementation.

## Original objective

The objective was to preserve the existing Qt desktop behavior while moving
application rules and transient business state behind UI-independent
boundaries. The resulting core must be reusable by a future browser frontend
without requiring the browser implementation to reproduce rules hidden inside
Qt widgets.

## Completed architecture

### Profile mixing and scoring

- Profile selection, uniqueness, ratio normalization, and 100-percent weight
  rules have UI-independent state and transitions.
- Scoring inputs and results use structured models.
- Score calculation no longer produces Hungarian presentation HTML.
- Qt controls are read and updated through presentation/workflow adapters.

### Application session and modes

- `ApplicationSessionState` owns the reusable runtime business session.
- Scored and Freehand mode state and capabilities are UI-independent.
- Returning to scored mode restores the scored editor and score-derived Tier
  Board order.
- `MainWindow` keeps signal-compatible entry points but delegates business
  session storage.

### AniList boundary

- Search values and selection state are structured independently of Qt.
- Cover download returns bytes from a data service.
- `QPixmap` decoding remains in the Qt adapter.
- Mode restoration does not start an unintended AniList request.
- AniList runtime, diagnostic logging, and retention behavior are documented in
  `anilist_data_lifecycle.md`.

### Tier Board

- Cards, rows, identity, duplicate detection, deletion, movement, ordering, and
  scored restoration are represented by a UI-independent domain model.
- Manual and scored card invariants are enforced outside Qt presentation.
- Scored-card edit sessions retain an original snapshot and have explicit
  start, save, cancellation, deletion, and board-clear transitions.
- Qt remains responsible for pointer gestures, drop geometry, widgets, and
  pixmaps.

### Result and platform boundaries

- Result summaries and detailed export content are generated separately from
  clipboard and image-rendering operations.
- Desktop clipboard, pixmap rendering, native URL opening, and dialogs are
  isolated behind Qt desktop adapters.

### Localization foundation

- Stable translation keys and a catalog format exist.
- Hungarian is the default and fallback language.
- Main visible presentation strings use the localization service.
- Runtime language switching is intentionally deferred.

### Diagnostics

- UI and workflow actions have explicit lifecycle and outcome logs.
- Logger filesystem failures cannot break the diagnosed user action.
- Application startup, shutdown, exit code, and unhandled exceptions are
  logged.
- Local diagnostic data has a 14-day retention policy and is never uploaded
  automatically.
- Frontend and core observations can be logged independently. The initial
  `qt_ui -> core -> tier_board -> core` boundary is implemented for Tier Board
  clearing and documented in `logging_boundaries.md`.

## Verification evidence

At closure:

- the complete local suite contains 485 passing tests;
- a dedicated architecture test imports the reusable core while `PyQt6`
  imports are blocked;
- the application entry point and application-session module import
  successfully;
- Linux CI passes tests, PyInstaller packaging, and binary startup smoke;
- Windows CI passes tests, PyInstaller packaging, EXE startup smoke, and
  portable package assembly;
- `git diff --check` reports no whitespace errors;
- the working tree is clean after the closure commit.

The project owner manually confirmed each large refactor slice. Confirmed flows
include scoring, profile mixing, online/offline title handling, AniList cover
selection, scored/manual Tier Board cards, Freehand movement, scored-order
restoration, card editing and cleanup, clipboard operations, localization
fallback, diagnostic content, and frontend/core logging boundaries.

## Intentional remaining boundaries

These are deferred work, not incomplete refactor tasks:

- runtime language selection and additional language catalogs;
- WebUI presentation and its transport/API adapter;
- authentication, hosting, server integration, and other website concerns;
- full cross-layer tracing with correlation IDs or JSON logs;
- migration of every legacy `ui` log event to frontend-specific component
  identities;
- persistence of application or AniList runtime state.

The AniList autocomplete controller remains Qt-specific because it owns Qt
timers, workers, threads, and completer presentation. Its value state, provider,
result models, and cover-byte transport are reusable.

## Merge and next-phase gate

The feature branch is eligible for merge review only when:

1. the closure commit is pushed;
2. Linux and Windows CI are green for that exact commit;
3. the final working tree is clean;
4. the project owner explicitly approves merging to `main`.

Merging does not imply a release.

After merge approval, recommended future phases are:

1. runtime language switching as a separate feature;
2. WebUI architecture and transport design as a separate feature;
3. WebUI implementation in independently testable vertical slices.

No next phase starts automatically from this closure.
