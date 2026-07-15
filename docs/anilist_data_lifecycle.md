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
Updated after the main-window refactor and AniList optional-boundary hardening pass.
```

This document reflects the current implementation state after:
- main-window responsibility extraction
- title-search workflow extraction
- AniList disabled-mode hardening
- runtime-only cover image handling hardening
- Tier Board card metadata and runtime visual ownership separation

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

The integration currently supports:
- Romaji titles
- English titles
- Native titles
- AniList IDs
- Season year
- Cover image URLs

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

Current intentionally separate UI follow-up:
- The tier flip button may still be visible but disabled when no flippable cards exist.
- Hiding that button in disabled AniList mode is tracked as a separate UI feature/bugfix, because it affects tier panel layout behavior rather than the integration data boundary itself.

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
- runtime query state
- re-query handling
- autocomplete orchestration
- async worker isolation for online searches

The controller owns transient runtime-only search state.

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

Primary file:

```text
app/services/cover_image_service.py
```

Responsibilities:
- downloading cover image bytes at runtime
- using the shared AniList User-Agent header
- handling HTTP and image-decoding errors
- converting valid image responses to transient `QPixmap` objects

The cover image layer does not persist images to disk and does not maintain a cache.

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

AniList-derived data is currently treated as transient runtime memory only.

The application currently does NOT:
- persist AniList responses to disk
- maintain a local AniList database
- create long-term AniList caches
- serialize AniList runtime objects
- store AniList session history

---

## 4.3 Memory Ownership

Current ownership model:

| Layer | Responsibility |
|---|---|
| Provider | Creates runtime result objects |
| Service | Pass-through orchestration |
| Controller | Search state ownership |
| Main-window title workflow | Selected runtime object assignment |
| `TierCardData` core model | Owns runtime card metadata such as title, current tier, card type, optional score, score tier, and optional AniList ID |
| `TierBoardWidget` | Owns the runtime card collection, tier placement, and board interaction state |
| `TierEntryWidget` | Owns transient visual state, including runtime-only `QPixmap`, card-side presentation, and card controls |

### 4.3.1 Tier Card Metadata Boundary

`TierCardData` is an internal UI-independent runtime model. Its purpose is to
keep card metadata separate from Qt widget state so that different application
modes can render the same card data without copying or destructively rewriting
it.

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

---

# 5. Persistence Policy

## Current Policy

The project currently follows a strict runtime-only policy regarding third-party AniList-derived data.

AniList-derived data is NOT:
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
Image data remains excluded from persistence in all cases under this policy.
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

All downloaded cover images are expected to be released together with the Python process lifecycle.

---

# 6. Logging Policy

The application uses structured application logging with multiple log levels.

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
- returned title metadata
- AniList API rate-limit diagnostics when response headers are available
- Tier Board interaction events
- flip-card state transitions
- entry add/remove diagnostics

This information is intended solely for:
- debugging
- reproducibility
- runtime diagnostics

Logs are local application logs only.

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
| Bulk synchronization | No | The application does not perform background database synchronization. |

The application is designed to avoid abusive API usage patterns. It performs user-driven title lookup only and does not attempt to mirror, bulk export, or continuously synchronize AniList data.

---

## 7.2 Current Technical Limitations

Current implementation limitations:
- no retry policy
- no automatic rate-limit backoff system
- no cache layer
- no user-facing rate-limit recovery workflow beyond safe fallback behavior

The implementation has worker-based online search isolation and explicit rate-limit response handling. Additional backoff or retry behavior may be considered later, but is intentionally not part of the current runtime-only MVP.

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
- persistence of third-party metadata

The design goal is minimizing retained third-party data ownership.

---

# 10. Future Planned Improvements

Planned future improvements may include:
- optional retry/backoff policy evaluation
- enhanced timeout behavior
- user-facing rate-limit messaging improvements
- expanded third-party service documentation
- optional hiding of flip-card UI when AniList is disabled
- future localization via language files

Any future persistence-related design change would require:
- architectural review
- lifecycle reassessment
- documentation update
- explicit classification of each proposed metadata field as application-owned or AniList-derived
- verification that no image bytes, `QPixmap`, base64 image data, local cover files, or image cache paths are included

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
