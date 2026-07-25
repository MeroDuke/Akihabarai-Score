"""UI-independent transient state for AniList title-search orchestration."""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class TitleSearchState:
    pending_query: str = ""
    last_manual_online_query: str = ""
    last_online_requery_title: str = ""
    active_query: str = ""
    queued_query: str | None = None


def reset_title_search_state() -> TitleSearchState:
    return TitleSearchState()


def with_pending_query(state: TitleSearchState, query: str) -> TitleSearchState:
    normalized = query.strip()
    return replace(
        state,
        pending_query=normalized,
        queued_query=None if not normalized else state.queued_query,
    )


def with_manual_query(state: TitleSearchState, text: str) -> TitleSearchState:
    return replace(
        state,
        last_manual_online_query=text.strip(),
        last_online_requery_title="",
    )


def queue_or_activate_query(
    state: TitleSearchState,
    query: str,
    *,
    search_running: bool,
) -> tuple[TitleSearchState, bool]:
    normalized = query.strip()
    if search_running:
        return replace(state, queued_query=normalized), False
    return replace(state, active_query=normalized), True


def finish_active_query(state: TitleSearchState) -> tuple[TitleSearchState, str | None]:
    queued = state.queued_query
    return replace(state, active_query="", queued_query=None), queued


def should_apply_search_result(state: TitleSearchState, query: str) -> bool:
    return query.strip().casefold() == state.active_query.strip().casefold()
