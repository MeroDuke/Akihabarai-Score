# Logging boundaries and future tracing

## Purpose

AkihabaraiScore logs both sides of important application boundaries. A
frontend records what it sent, while the reusable application workflow records
what it received and how it responded. These are intentionally separate
events, not duplicate noise.

This makes silent communication failures observable and keeps the current Qt
frontend and a future WebUI on equal architectural footing.

## Component identity

New boundary events use stable component identifiers:

| Component | Responsibility |
|---|---|
| `qt_ui` | User actions and values emitted by the Qt frontend |
| `web_ui` | Reserved for values emitted by the future browser frontend |
| `core` | Frontend-independent workflow input, decisions, and outcomes |
| `tier_board` | Tier Board state mutations and presentation interaction |
| `anilist` | AniList request and search orchestration |
| `clipboard` | Platform clipboard operation lifecycle |
| `app` | Process startup, shutdown, and unhandled failures |

The older generic `ui` component remains valid for existing events during the
incremental migration. New frontend-boundary events should prefer `qt_ui` or
`web_ui`.

## Event naming

Events use lower-case `snake_case` names followed by structured `key=value`
fields:

```text
[qt_ui] clear_confirmation_answered: decision='yes'
[core] clear_confirmation_received: decision='yes'
[tier_board] all_entries_removed: count=3
[core] clear_entries_completed: count=3
```

Names describe the observation made by that layer:

- `answered`, `clicked`, `submitted`: the frontend emitted something;
- `received`: the core accepted the frontend value;
- `started`, `completed`, `failed`, `cancelled`, `skipped`: workflow lifecycle;
- domain-specific verbs such as `added`, `removed`, `moved`: state mutation.

A frontend event must not claim that the core completed an operation. A core
event must not claim which visual gesture occurred unless that information was
explicitly passed across the boundary.

## Current implemented slice

Tier Board clearing is the first flow using the convention:

```text
Qt confirmation dialog
  -> [qt_ui] clear_confirmation_answered
  -> [core] clear_confirmation_received
  -> [tier_board] all_entries_removed
  -> [core] clear_entries_completed
```

Cancellation ends with `[core] clear_entries_cancelled`. Empty-board requests
end with `[core] clear_entries_skipped`.

Tests protect the frontend and core event names independently. This establishes
the convention without coupling the UI-independent domain models to the
logger.

## Architectural constraints

- Domain value models do not import or call the logger.
- Frontend adapters identify themselves at the boundary.
- Core workflow services log accepted input and outcomes.
- Qt objects, HTTP request objects, and future WebUI request objects do not
  enter domain state merely for logging.
- Logs are diagnostic output, not an event store and not an application input.
- Diagnostic data follows the local 14-day retention policy documented in
  `anilist_data_lifecycle.md`.

## Deferred tracing feature

A later dedicated feature may add:

- correlation IDs spanning frontend, core, and adapters;
- a per-action tracing context;
- structured JSON output alongside the human-readable log;
- WebUI request/session identity;
- concurrent-client separation;
- middleware or adapter helpers that apply component identity automatically;
- broader migration of legacy `ui` events to `qt_ui`.

Those capabilities are intentionally not part of the current UI-independent
core refactor. The convention above provides a compatible foundation without
prematurely selecting a WebUI framework or transport protocol.
