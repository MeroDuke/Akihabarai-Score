# Refactor stabilization gate

## Scope

This gate validates the UI-independent-core refactor before localization
switching or WebUI implementation begins. It does not add either capability.

## Automated gates

- The complete pytest suite must pass.
- The reusable application core must import while all `PyQt6` imports are
  blocked.
- The application entry point and the application-session module must import
  successfully.
- `git diff --check` must report no whitespace errors.
- Linux and Windows CI must pass their tests, packaging, and executable startup
  smoke checks.

The Qt-free import boundary is enforced by
`tests/test_ui_independent_core_boundary.py`. Its explicit module list covers
the scoring models and rules, application session, modes, profile mixing,
structured/localized result content, Tier Board state and edit lifecycle, and
title-search value state.

## Manual smoke result

The project owner confirmed the desktop application after each refactor slice,
including the final Qt reconnection. The confirmed flows cover:

- scored input, recomputation, and result presentation;
- profile mixing and weight normalization;
- online/offline title input and AniList cover selection;
- scored and manual Tier Board card creation;
- Freehand movement and scored-order restoration;
- scored-card editing, cancellation, deletion, and board clearing;
- text and image clipboard actions;
- Hungarian default and fallback presentation.

## Intentional Qt boundaries

Qt remains in the desktop entry point, widgets, dialogs, rendering and
clipboard adapters, layout construction, autocomplete controller, and
widget-oriented workflow adapters. These modules translate desktop gestures
and presentation objects to and from the reusable application services; they
are not part of the Qt-free import gate.

`MainWindow` retains signal-compatible property and callback names for the
desktop UI, but delegates business-session storage to
`ApplicationSessionState`. Runtime-only pixmaps and widget references remain
owned by the Qt layer.

## Known non-regressions and deferred work

- Runtime language switching is not implemented yet; Hungarian remains the
  default and fallback language.
- WebUI and web transport/API adapters are not implemented yet.
- AniList autocomplete threading and Qt presentation remain desktop-specific;
  the provider, structured results, and value-state rules are reusable.
- AniList data and cover images remain runtime-only and are not persisted.

These are planned boundaries, not deviations from the pre-WebUI refactor
scope. Any new known behavioral difference must be resolved or documented here
before the stabilization gate can be considered green.
