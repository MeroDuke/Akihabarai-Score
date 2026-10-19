# AniList Integration Runtime & Data Lifecycle

## Scope

This document describes the current AniList integration architecture used by the AkihabaraiScore application.

The purpose of this document is to provide:
- runtime data lifecycle transparency
- architectural ownership clarification
- persistence policy documentation
- third-party integration behavior overview
- audit-friendly technical traceability

This document focuses specifically on the optional AniList title-search integration currently implemented in the application.

---

## Document Status

```text
CURRENT IMPLEMENTATION NOTE
Reviewed against the 1.0.0 implementation on 2026-10-19.
```

This document reflects the current implementation state after:
- main-window responsibility extraction
- title-search workflow extraction
- AniList disabled-mode hardening
- runtime-only cover image handling hardening
- Tier Board card metadata and runtime visual ownership separation
- Freehand mode runtime editor-state preservation
- empty autocomplete result popup hardening
- scored Tier card input snapshot and edit-session lifecycle introduction
- edit-session cleanup hardening for card deletion and full-board clearing
- UI-independent title-search state extraction
- cover image byte transport and Qt pixmap decoding separation
- UI-independent Tier Board card lifecycle and row-state extraction
- UI-independent Tier Board movement and scored-order restoration
- UI-independent scored-card edit-session lifecycle
- runtime Hungarian/English localization with application-owned language preference
- user-visible AniList search error status with runtime-only diagnostic state
- manual exact-match paste, selection debounce cancellation, and stale-result handling
- reuse of the displayed autocomplete result during selection

Future architectural changes may alter:
- threading behavior
- image handling
- caching behavior
- UI ownership
- runtime object lifecycle
- localization ownership

---

## Standards & Methodology Notes

This document is not an official ISO or IEEE certification artifact.

However, its structure and terminology are intentionally inspired by:
- ISO/IEC 25010 software quality principles
- audit-oriented software traceability practices
- runtime lifecycle transparency concepts commonly used in regulated software environments

The goal is engineering transparency and maintainability, not formal certification claims.

---

## AI-Assisted Authoring Disclosure

This document was initially drafted with AI-assisted tooling and subsequently reviewed, curated, and validated by the project author.

All architectural decisions, implementation policies, and runtime behavior descriptions remain under the responsibility of the project author.

---

# 1. Integration Purpose

The AniList integration provides:
- online anime title lookup
- autocomplete suggestions
- structured anime metadata retrieval

The provider retrieves the following runtime metadata:
- Romaji titles
- English titles
- Native titles
- AniList IDs
- Season year
- Cover image URLs

Autocomplete suggestions display Romaji titles. English and Native titles,
season year, AniList ID, and cover URL remain metadata on `AnimeSearchResult`;
they are not separate selectable autocomplete labels. The online search term
is passed to AniList, whose API determines the matching titles.

The integration is optional and can be disabled through application configuration.

Third-party attribution note:

```text
Anime metadata and cover image references are retrieved from AniList at runtime.
```

This attribution is intentionally documented here rather than rendered as a mandatory UI element, because the AniList integration is designed to be optional and removable from the user-facing application if required.

---

# 2. Configuration Boundary

AniList can be disabled with:

```json
{
  "features": {
    "anilist_enabled": false
  }
}
```

When `anilist_enabled` is `false`, the application currently guarantees:
- the title mode button is hidden
- the title input remains in offline mode
- the title autocomplete controller is not created
- the title completer and completer model are not created
- title-search controller accessors return empty or `None` values
- online title-search scheduling is skipped
- debounced online search is skipped
- title lookup through the AniList controller returns `None`
- autocomplete selection does not call stale controller paths
- cover pixmap loading for AniList-selected results is skipped
- the tier flip button is hidden while Tier Board deletion and image-copy actions remain available

---

# 3. Current Architecture Overview

Current architecture layers:

```text
MainWindow compatibility wrapper layer
|
Main-window workflow services
|
AniList Title Search Controller
|
AniList Service Layer
|
AniList API Provider
|
AniList GraphQL API
```

Primary files for the main-window integration boundary:

```text
app/main.py
app/services/main_window_title_workflow_service.py
app/services/title_search_workflow_service.py
app/controllers/anilist_title_search_controller.py
app/services/anilist_service.py
app/services/anilist_api_provider.py
app/services/title_search_state_service.py
app/presenters/anilist_error_presenter.py
app/widgets/top_inputs_panel_widget.py
app/services/cover_image_data_service.py
app/services/cover_image_qt_adapter.py
app/services/cover_image_service.py
app/core/models.py
app/widgets/tier_board_widget.py
app/widgets/tier_entry_widget.py
```

---

## 3.1 MainWindow Compatibility Layer

Primary file:

```text
app/main.py
```

Responsibilities:
- owning the `MainWindow` object and public callback method names
- keeping signal-compatible method entry points
- delegating title, input, output, lifecycle, and bootstrap work to services
- preserving user-facing behavior during refactors

The `MainWindow` layer does NOT:
- directly perform HTTP requests
- directly parse AniList JSON payloads
- directly persist AniList-derived data
- own AniList network behavior

---

## 3.2 Main-Window Title Workflow Layer

Primary file:

```text
app/services/main_window_title_workflow_service.py
```

Responsibilities:
- window-specific title-search setup
- optional AniList boundary checks
- mode switching delegation
- title selection state updates
- controller accessors
- cover pixmap loading delegation
- creating, presenting, and clearing localized AniList search error state

This layer is the current guard for `anilist_enabled=false` behavior. When the integration is disabled, this layer avoids creating the controller/completer infrastructure and skips stale controller paths.

---

## 3.3 Title Search Workflow Layer

Primary file:

```text
app/services/title_search_workflow_service.py
```

Responsibilities:
- constructing autocomplete UI support when enabled
- binding `QCompleter` and `QStringListModel`
- synchronizing offline/online title input UI state
- enabling/disabling title autocomplete
- clearing selected runtime title state when manual text changes
- handling title autocomplete selection

This layer owns the reusable title-search workflow behavior but does not perform HTTP requests directly.

---

## 3.4 Controller Layer

Primary file:

```text
app/controllers/anilist_title_search_controller.py
```

Responsibilities:
- debounce handling
- online/offline routing
- popup suppression logic
- explicit popup closing for empty queries, empty results, connection errors, and exact-match suppression
- runtime query state
- re-query handling
- autocomplete orchestration
- async worker isolation for online searches

The controller owns Qt timers, threads, workers, and autocomplete widgets. Its
query values are held by the UI-independent, immutable `TitleSearchState`
model. The state model contains strings only; it does not contain Qt objects,
network clients, AniList results, image data, or persistence behavior.

The controller separately retains the latest successful result set in
`_online_results_by_title`, keyed by normalized Romaji title. Selection reuses
that result instead of issuing an immediate duplicate lookup. This small,
session-only lookup table is replaced by the next successful result set and
cleared when results or online state are cleared. It is not a disk cache or
search-history store. If a selected title is absent from the table, the
controller performs a synchronous provider lookup as a fallback.

### Search and selection rules

- The shipped debounce interval is 1000 ms, configured in `config/ui.json`.
- A manually typed or pasted exact title still opens a single matching
  suggestion; the user selects it to load its metadata and cover.
- Selecting a suggestion stops the pending debounce and hides the popup.
- Selection of a title different from the last manually entered query may
  schedule one debounced full-title requery. Its single exact-match response
  keeps the popup hidden. A later manual edit restores normal popup behavior.
- One asynchronous autocomplete request runs at a time; a single queued slot
  retains the latest scheduled query. Results for an inactive mode, a stale
  active query, or input superseded by a newer query are ignored.
- Switching to Offline stops the debounce and detaches autocomplete. An
  already running HTTP request is not cancelled; its result is ignored while
  Offline is active.

Autocomplete HTTP requests run in a worker thread. The selection fallback
lookup and cover download are synchronous on the calling UI path; worker
isolation is not a guarantee for every integration request.

---

## 3.5 Service Layer

Primary file:

```text
app/services/anilist_service.py
```

Responsibilities:
- application-facing AniList entry points
- provider abstraction
- offline/online routing

---

## 3.6 Provider Layer

Primary file:

```text
app/services/anilist_api_provider.py
```

Responsibilities:
- HTTP communication
- GraphQL request construction
- User-Agent header ownership
- rate-limit response handling
- rate-limit diagnostic logging
- JSON response validation
- runtime object mapping

The provider is the only layer performing AniList GraphQL network communication.

---

## 3.7 Cover Image Layer

Primary files:

```text
app/services/cover_image_data_service.py
app/services/cover_image_qt_adapter.py
app/services/cover_image_service.py (compatibility facade)
```

Responsibilities:
- downloading cover image bytes at runtime in a Qt-independent service
- using the shared AniList User-Agent header
- handling HTTP errors, including explicit 429 and `Retry-After` details
- converting valid in-memory bytes to transient `QPixmap` objects only in the
  Qt adapter

The byte response crosses into the Qt adapter only for immediate runtime
decoding. Neither layer persists images to disk, maintains a cache, retries
requests automatically, or serializes the response.

---

# 4. Runtime Data Lifecycle

## 4.1 Data Flow

Current enabled-mode runtime flow:

```text
User enters title
|
MainWindow title workflow
|
AniList Title Search Controller
|
AniList service/provider
|
AniList GraphQL API response
|
JSON validation and mapping
|
AnimeSearchResult runtime object creation
|
Autocomplete/UI rendering
|
Optional cover image download
|
QPixmap runtime object creation
|
Tier card rendering
|
User interaction
|
Object dereference
|
Python process termination
|
Memory release
```

Failed enabled-mode request flow:

```text
User enters title
|
MainWindow title workflow
|
AniList Title Search Controller
|
AniList service/provider
|
HTTP, timeout, or connection failure
|
Runtime-only TitleSearchErrorState creation
|
Localized inline information-bar rendering
|
Successful later request or switch to Offline mode
|
Runtime error state clearing
```

The information bar displays only the error category or HTTP status required
to explain the unavailable online lookup, together with the available Offline
mode fallback. Provider error details remain diagnostic data and are not
rendered as arbitrary server-response text in the UI. Changing the UI language
re-renders the existing runtime state locally and does not start another
AniList request.

Disabled-mode runtime flow:

```text
User enters manual title
|
Offline title input
|
No AniList controller/completer
|
No AniList API call
|
No AniList cover image loading
|
Text-only scoring and tier interaction
```

---

## 4.2 Runtime-Only Policy

AniList-derived application state is held in transient runtime memory. Local
diagnostic logs, possible crash dumps, and user-initiated clipboard exports
are explicit boundaries described below; runtime-only does not imply that
these artifacts cannot contain AniList-derived content.

The application may persist its own UI language preference in a user-scoped
JSON file. The application writes `schema_version` and `ui.language` and
preserves pre-existing unknown fields for forward compatibility. Its language
preference code does not add AniList IDs, selected or searched titles, result
objects, cover URLs, image bytes, pixmaps, or search history. This
application-owned preference does not weaken the runtime-only policy for
third-party AniList-derived data.

The application currently does NOT:
- persist AniList responses to disk
- maintain a local AniList database
- create long-term AniList caches
- serialize AniList runtime objects
- store an AniList search history or persistent cache

The current title-search error category, diagnostic detail, and
optional HTTP status may be held in `TitleSearchErrorState` for the active
application session. This state is cleared after a successful request or when
the user switches to Offline mode, and it is not written to application
settings or another persistence mechanism.

Diagnostic logging exception: when logging is enabled, selected runtime
metadata may appear in local diagnostic log entries. Logs are not an AniList
cache and are not read back into application behavior. With the shipped
configuration they are retained for at most 14 days and then removed on a
later logger startup. To make user-submitted bug reports reproducible, these
entries may contain user-entered titles, search queries, returned AniList title
metadata and IDs, cover URLs, result counts, and AniList error details.

For HTTP failures, extracted GraphQL explanations are limited to five messages
of 500 characters each and whitespace is normalized. This bound does not apply
to every error path: a GraphQL `errors` value received in an HTTP-success
response is currently converted to a diagnostic string without that limit.
The UI presenter uses only the error category and HTTP status, never this
arbitrary diagnostic detail.

---

## 4.3 Memory Ownership

Current ownership model:

| Layer | Responsibility |
|---|---|
| Provider | Creates runtime result objects |
| Service | Pass-through orchestration |
| UI-independent title-search state service | Immutable runtime query values |
| `TitleSearchErrorState` | Immutable runtime-only error category, diagnostic detail, and optional HTTP status |
| Controller | Qt timer, worker, thread, model, popup, and latest-result lookup ownership |
| Cover image data service | Runtime-only HTTP response bytes until Qt decoding |
| Cover image Qt adapter | Transient `QPixmap` decoding and preview presentation |
| Main-window title workflow | Selected runtime object assignment and title-search error-state creation, clearing, and presentation orchestration |
| AniList error presenter | Maps runtime error state to application-owned localized text without network access |
| Top-inputs panel widget | Renders the inline error information bar without owning AniList network or persistence behavior |
| Main-window mode workflow | Temporarily snapshots the scored editor title mode, selected AniList result, and runtime-only cover pixmap while Freehand mode is active |
| `TierCardData` core model | Owns runtime card metadata such as title, current tier, card type, optional score, score tier, optional AniList ID, and an optional scored-input snapshot |
| `TierBoardState` domain model | Owns runtime tier rows, card identity lookup, normalized-title uniqueness, and scored/manual card lifecycle rules |
| `TierBoardWidget` | Renders the runtime card collection and owns Qt interaction state |
| `TierEntryWidget` | Owns transient visual state, including runtime-only `QPixmap`, card-side presentation, and card controls |

### 4.3.1 Tier Card Metadata Boundary

`TierCardData` is an internal UI-independent runtime model. Its purpose is to
keep card metadata separate from Qt widget state so that different application
modes can render the same card data without copying or destructively rewriting
it.

`TierBoardState` groups these cards into UI-independent tier rows and owns
addition, case-insensitive duplicate rejection, scored/manual invariants,
scored-card replacement, deletion, full-board clearing, cross-tier movement,
within-tier ordering, and score-derived restoration. Its mutation results use
structured reason and action identifiers rather than user-facing text.
`TierBoardWidget` renders the domain cards and retains only Qt presentation
objects such as entry widgets and pixmaps. Qt translates pointer and drop
geometry into a requested tier/index, while the domain decides whether and how
the card order changes.

The model is intentionally restricted to small value-type fields. It must not
contain:
- `QPixmap` objects
- downloaded image bytes
- base64-encoded images
- local cover image paths
- cached cover files

Cover images remain transient runtime visual state owned by the widget or the
active in-memory UI flow. The introduction of `TierCardData` does not change the
current persistence policy and does not create a user-facing storage capability.
The same restriction applies to `TierBoardState`: it references card metadata
only and does not own cover bytes, `QPixmap` instances, cache paths, or
serialization behavior.

### 4.3.2 Freehand Mode Snapshot Boundary

Switching from scored mode to Freehand mode creates a session-only snapshot of
the scored editor state. The snapshot may reference the selected
`AnimeSearchResult` and its already loaded runtime `QPixmap` so the matching
title and cover can be restored when scored mode is re-entered.

This snapshot:
- exists only in process memory
- is not serialized or written to disk
- does not download an additional cover image
- is replaced by later scored-to-Freehand transitions
- is released with the application process

It therefore does not change the persistence or third-party ownership policy.

### 4.3.3 Scored Tier Card Edit Snapshot Boundary

Newly created scored Tier cards retain a session-only input snapshot so the
user can reopen the card and continue editing the values that produced it. The
snapshot contains only application-owned scoring inputs:

- profile mix mode
- selected profile names
- profile weights
- dimension values

The snapshot does not contain image bytes, cover URLs, `QPixmap` objects, or an
`AnimeSearchResult`. The optional AniList ID remains a separate small metadata
field on `TierCardData`, while the already loaded cover pixmap remains owned by
the runtime `TierEntryWidget`.

Opening a scored card for editing copies the snapshot values back into the
active editor and reuses the card widget's in-memory cover pixmap. It does not
perform another AniList request. Saving replaces the card's input snapshot and
preserves the existing AniList ID when no new AniList result was selected.

The UI-independent `TierCardEditSessionState` owns the active card identity and
a defensive copy of its original metadata/input snapshot. It contains no
widget, pixmap, cover URL, or `AnimeSearchResult` reference. Session transitions
use stable reasons for save, cancellation, card deletion, and board clearing.
The Qt workflow only restores editor widgets and presents the active/finished
state.

The edit session exists only while the process is running. It is closed when
the user saves or cancels, and is also closed automatically if the edited card
is removed or the Tier Board is cleared. Freehand mode does not open scored
card editing sessions; clicking scored cards there remains a positioning-only
interaction.

This capability does not change the persistence policy: neither the input
snapshot nor the runtime cover is written to disk or retained between
application launches.

---

# 5. Persistence Policy

## Current Policy

The project uses a runtime-only policy for third-party AniList application
state, with the explicit diagnostic and user-initiated export boundaries
documented here.

Application-owned settings are outside this third-party data boundary. The
language preference store manages only the active `hu` or `en` UI language
and is not connected to the AniList controller, provider, result models, cover
image pipeline, Tier card metadata, or diagnostic search state.

Apart from the local diagnostic and user-initiated export boundaries described
here, AniList-derived data is NOT:
- stored in databases
- exported automatically
- synchronized
- uploaded elsewhere
- cached on disk
- retained between application launches

Internal maintenance reminder:

```text
TierCardData being structurally serializable does not authorize persistence.
Persisting AniList IDs, AniList-selected titles, cover URLs, or other
AniList-derived metadata requires a separate lifecycle and policy review.
Application-managed image caches and session persistence remain excluded.
User-initiated clipboard rendering is documented separately below.
```

---

## 5.1 Cover Image Policy

Current policy:

```text
Memory-only usage.
No disk persistence intended.
```

At the current implementation stage:
- cover image URLs may exist in runtime memory
- cover images may be downloaded during runtime when AniList is enabled and a selected result has a cover URL
- downloaded bytes are returned by a Qt-independent value response and passed
  directly to the Qt adapter
- cover image requests use the shared AniList User-Agent header
- cover image HTTP 429 responses are handled explicitly
- cover image `Retry-After` headers are preserved in the returned error detail when available
- cover images are converted into transient `QPixmap` objects
- cover images may be displayed inside Tier Board cards
- cover images are not persisted to disk
- cover images are not cached between application launches

Current implementation intentionally avoids:
- image database creation
- local image cache folders
- thumbnail persistence
- long-term image retention

Application-owned cover references are released when no longer referenced or
when the process terminates. The byte response and decoded pixmap are not
placed in `TierCardData`, scoring snapshots, configuration, databases, or
filesystem-backed caches.

### User-initiated clipboard export

The Tier List image-copy action renders the saved cards in their current
presentation, including visible covers, into a new pixmap and places it on the
system clipboard. The preview, card controls, and edit highlight are hidden
during rendering. Text and result-image exports can likewise contain the
selected title, but do not include raw API responses or cover URLs.

The rendered clipboard content crosses the application's runtime ownership
boundary. Its retention, clipboard-history behavior, and any later save or
sharing are controlled by the operating system and the user; process exit
does not guarantee its deletion. The application does not automatically write
these exports to disk or upload them.

### Crash diagnostic boundary

Native crash diagnostics can produce a Windows minidump or an operating-system
managed Linux core dump. Such files may contain fragments of process memory,
including runtime AniList metadata or image data. They are diagnostic artifacts,
not an application cache, and must not be described as metadata-free. Their
handling and privacy limits are documented in
[`crash_diagnostics.md`](../architecture/crash_diagnostics.md). The ordinary
session-log retention description does not guarantee deletion of OS-managed
core dumps or user-copied diagnostic artifacts.

---

# 6. Logging Policy

The application uses human-readable application logs with multiple log levels,
stable event names, and structured `key=value` diagnostic fields. JSON log
output is not part of the current implementation.

Current logging categories include:
- UI events
- controller lifecycle events
- provider/API events
- debug diagnostics

---

## 6.1 AniList Logging Behavior

Debug logging may contain:
- search queries
- autocomplete results
- AniList IDs
- returned title and cover metadata
- structured event and error metadata
- AniList API rate-limit diagnostics when response headers are available
- Tier Board interaction events
- flip-card state transitions
- entry add/remove diagnostics
- Freehand drag, reorder, mode transition, and scored-order restoration diagnostics
- scored Tier card edit-session and cleanup diagnostics

This information is intended solely for:
- debugging
- reproducibility
- runtime diagnostics

Logs are local application logs only.
With the shipped configuration, session log files have a 14-day retention
window. Cleanup is best-effort and runs when the logger starts; consequently an
old file can remain beyond 14 calendar days until the application is started
again. Logging does not create an application-readable AniList cache or search
history. Log files are never uploaded automatically; a user must explicitly
choose to share one for diagnostics. Because a shared file can contain the
runtime metadata listed above, it should be treated as diagnostic data.

The application does NOT:
- upload logs externally
- transmit telemetry
- perform analytics collection

---

# 7. Networking Behavior

Current implementation characteristics:

| Behavior | Status |
|---|---|
| GraphQL API usage | Yes, only when AniList is enabled and an online lookup path is used |
| HTTPS communication | Yes |
| Authentication | No |
| User AniList account access | No |
| Background synchronization | No |
| Telemetry upload | No |

---

## 7.1 API Etiquette & Hardening Behavior

Current AniList API hardening behavior:

| Behavior | Status | Notes |
|---|---|---|
| Explicit User-Agent | Yes | AniList GraphQL and cover image requests identify the application as `AkihabaraiScore/<version>`. |
| HTTP 429 handling | Yes | Rate-limit responses are handled as explicit error states instead of generic request failures. |
| `Retry-After` preservation | Yes | When available, the `Retry-After` value is included in the returned error detail. |
| Rate-limit diagnostics | Yes | Known AniList rate-limit headers are logged at debug level when present. |
| Automatic retry/backoff | No | The application does not currently retry failed AniList requests automatically. |
| New user-driven attempt after failure | Yes | A new non-empty search or switching Online with a non-empty title starts a normal lookup; no periodic retry runs. A successful response, including zero results, clears the information bar. |
| Bulk synchronization | No | The application does not perform background database synchronization. |
| App-mode restoration request | No | Returning from Freehand to scored mode rebinds autocomplete presentation without starting a lookup or opening the popup. |
| User-visible lookup failure status | Yes | A localized inline information bar shows the error category or HTTP status and identifies Offline mode as the available fallback. |

The application is designed to avoid abusive API usage patterns. It performs user-driven title lookup only and does not attempt to mirror, bulk export, or continuously synchronize AniList data.

---

## 7.2 Current Technical Limitations

Current implementation limitations:
- no retry policy
- no automatic rate-limit backoff system
- no persistent cache; only the latest autocomplete results are reused in memory
- no automatic user-facing recovery workflow beyond reporting the failure and
  identifying Offline mode as the safe fallback

The implementation has worker-based online search isolation, explicit
rate-limit response handling, and a localized inline failure status. The
information bar does not retry requests, alter request frequency, or persist
the failure. Additional backoff or retry behavior may be considered later, but
is intentionally not part of the current runtime-only MVP.

Request defaults are an 8-second timeout and a first page of up to 10 anime
results. Cover downloads also use an 8-second timeout. There is no pagination
loop, background polling, or automatic replay after HTTP 429. The information
bar describes title-search failures; a cover-download or decode failure is
logged and falls back to text or the existing cover-placeholder presentation.

---

# 8. Third-Party Dependency Notes

Current AniList integration depends on:
- AniList GraphQL API
- Python requests library
- PyQt6 UI framework

No AniList SDK is currently used.

---

# 9. Security & Privacy Considerations

The current implementation intentionally avoids:
- user authentication
- token storage
- account linkage
- analytics systems
- remote telemetry
- persistent application storage of third-party metadata, apart from the
  documented diagnostic artifacts and user-initiated clipboard exports

The design goal is minimizing retained third-party data ownership.

---

# 10. Change-Control Requirements

Any future persistence-related design change requires:
- architectural review
- lifecycle reassessment
- documentation update
- explicit classification of each proposed metadata field as application-owned or AniList-derived
- verification that no image bytes, `QPixmap`, base64 image data, local cover files, or image cache paths are included

Potential features and implementation intentions belong in `plans/` and
`ROADMAP.md`, not in this current-state integration document.

---

# 11. Review Scope

Future review scope includes:
- runtime ownership verification
- disabled-mode boundary verification
- persistence verification
- logging verification
- image handling verification
- API header verification
- rate-limit behavior verification
- threading verification
- temporary storage verification
- dependency review

This document should be updated whenever the AniList integration boundary, persistence behavior, or third-party data lifecycle changes.

## 11.1 Implementation review evidence — 2026-10-19

The review compared the provider, controller, title workflows, cover transport
and Qt adapter, preference store, mode/edit lifecycle, logger, and clipboard
export with this document. Relevant automated evidence includes:

- [`test_anilist_api_provider.py`](../../tests/test_anilist_api_provider.py):
  request mapping, HTTP explanations, timeout, invalid responses and rate limits.
- [`test_anilist_title_search_controller.py`](../../tests/test_anilist_title_search_controller.py):
  exact-match popup behavior, selection cancellation, result reuse and stale results.
- [`test_cover_image_service.py`](../../tests/test_cover_image_service.py):
  in-memory bytes, User-Agent, failure handling and pixmap decoding.
- [`test_main_window.py`](../../tests/test_main_window.py): pasted exact-match
  selection, inline errors, language change, disabled integration and exports.
- [`test_user_preferences_service.py`](../../tests/test_user_preferences_service.py):
  language persistence and preservation of unknown fields.

The audit's related unit and Qt workflow selection passed locally in offscreen
mode: **141 tests passed**. Network providers were mocked; this evidence
validates application behavior without calling the live AniList service.
