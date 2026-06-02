# AniList Integration Runtime & Data Lifecycle (Draft)

## Scope

This document describes the current AniList integration architecture used by the AkihabaraiScore application.

The purpose of this document is to provide:
- runtime data lifecycle transparency
- architectural ownership clarification
- persistence policy documentation
- third-party integration behavior overview
- audit-friendly technical traceability

This document focuses specifically on the AniList title-search integration currently implemented in the application.

---

## Document Status

```text
DRAFT
Subject to implementation changes.
```

This document reflects the current implementation state of the project after the initial AniList integration hardening pass.

Future architectural changes may alter:
- threading behavior
- image handling
- caching behavior
- UI ownership
- runtime object lifecycle

A final compliance-style review is planned after the AniList integration feature set is considered functionally complete.

---

## Standards & Methodology Notes

This document is not an official ISO or IEEE certification artifact.

However, its structure and terminology are intentionally inspired by:
- ISO/IEC 25010 software quality principles
- audit-oriented software traceability practices
- runtime lifecycle transparency concepts commonly used in regulated software environments

The goal is engineering transparency and maintainability — not formal certification claims.

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

This attribution is intentionally documented here rather than rendered as a mandatory UI element, because the AniList integration is designed to be fully optional and removable from the user-facing application if required.

---

# 2. Current Architecture Overview

Current architecture layers:

```text
UI Layer
↓
AniList Title Search Controller
↓
AniList Service Layer
↓
AniList API Provider
↓
AniList GraphQL API
```

---

## 2.1 UI Layer

Primary file:

```text
app/main.py
```

Responsibilities:
- UI widget ownership
- autocomplete widget binding
- mode switching (offline/online)
- runtime selection ownership
- result rendering
- signal connections

The UI layer does NOT:
- directly perform HTTP requests
- directly parse AniList JSON payloads
- persist AniList-derived data

---

## 2.2 Controller Layer

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

The controller owns transient runtime-only search state.

---

## 2.3 Service Layer

Primary file:

```text
app/services/anilist_service.py
```

Responsibilities:
- application-facing AniList entry points
- provider abstraction
- offline/online routing

---

## 2.4 Provider Layer

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

# 3. Runtime Data Lifecycle

## 3.1 Data Flow

Current runtime flow:

```text
AniList GraphQL API Response
↓
JSON Parsing
↓
AnimeSearchResult runtime object creation
↓
Autocomplete/UI rendering
↓
Optional cover image download
↓
QPixmap runtime object creation
↓
Tier card rendering
↓
User interaction
↓
Object dereference
↓
Python process termination
↓
Memory release
```

---

## 3.2 Runtime-Only Policy

AniList-derived data is currently treated as transient runtime memory only.

The application currently does NOT:
- persist AniList responses to disk
- maintain a local AniList database
- create long-term AniList caches
- serialize AniList runtime objects
- store AniList session history

---

## 3.3 Memory Ownership

Current ownership model:

| Layer | Responsibility |
|---|---|
| Provider | Creates runtime result objects |
| Service | Pass-through orchestration |
| Controller | Search state ownership |
| UI | Selected runtime object ownership |

---

# 4. Persistence Policy

## Current Policy

The project currently follows a strict runtime-only policy regarding third-party AniList-derived data.

AniList-derived data is NOT:
- stored in databases
- exported automatically
- synchronized
- uploaded elsewhere
- cached on disk
- retained between application launches

---

## 4.1 Cover Image Policy

Current policy:

```text
Memory-only usage planned.
No disk persistence intended.
```

At the current implementation stage:
- cover image URLs may exist in runtime memory
- cover images may be downloaded during runtime
- cover image requests use the shared AniList User-Agent header
- cover image HTTP 429 responses are handled explicitly
- cover image `Retry-After` headers are preserved in the returned error detail when available
- cover images are converted into transient `QPixmap` objects
- cover images are displayed inside Tier Board cards
- cover images are not persisted to disk
- cover images are not cached between application launches

Current implementation intentionally avoids:
- image database creation
- local image cache folders
- thumbnail persistence
- long-term image retention

All downloaded cover images are expected to be released together with the Python process lifecycle.

---

# 5. Logging Policy

The application uses structured application logging with multiple log levels.

Current logging categories include:
- UI events
- controller lifecycle events
- provider/API events
- debug diagnostics

---

## 5.1 AniList Logging Behavior

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

# 6. Networking Behavior

Current implementation characteristics:

| Behavior | Status |
|---|---|
| GraphQL API usage | Yes |
| HTTPS communication | Yes |
| Authentication | No |
| User AniList account access | No |
| Background synchronization | No |
| Telemetry upload | No |

---

## 6.1 API Etiquette & Hardening Behavior

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

## 6.2 Current Technical Limitations

Current implementation limitations:
- no retry policy
- no automatic rate-limit backoff system
- no cache layer

The implementation has already introduced worker-based online search isolation and explicit rate-limit response handling. Additional backoff or retry behavior may be considered later, but is intentionally not part of the current runtime-only MVP.

---

# 7. Third-Party Dependency Notes

Current AniList integration depends on:
- AniList GraphQL API
- Python requests library
- PyQt6 UI framework

No AniList SDK is currently used.

---

# 8. Security & Privacy Considerations

The current implementation intentionally avoids:
- user authentication
- token storage
- account linkage
- analytics systems
- remote telemetry
- persistence of third-party metadata

The design goal is minimizing retained third-party data ownership.

---

# 9. Future Planned Improvements

Planned future improvements may include:
- optional retry/backoff policy evaluation
- enhanced timeout behavior
- user-facing rate-limit messaging improvements
- expanded third-party service documentation

Any future persistence-related design change would require:
- architectural review
- lifecycle reassessment
- documentation update

---

# 10. Final Compliance Review (Planned)

A final implementation audit is planned after the AniList feature set stabilizes.

The planned review scope includes:
- runtime ownership verification
- persistence verification
- logging verification
- image handling verification
- API header verification
- rate-limit behavior verification
- threading verification
- temporary storage verification
- dependency review

This document will be updated after that review phase.

