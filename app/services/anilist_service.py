"""AniList service layer.

This module is the single application-facing entry point for AniList searches.
The current implementation intentionally delegates to the mock provider, so the
UI can depend on the service interface before real network logic is introduced.
"""

from app.core.models import AnimeSearchResult
from app.services.anilist_mock_provider import get_mock_anime_results


def search_anime(query: str = "") -> list[AnimeSearchResult]:
    """Return structured anime matches for the given query.

    For now this uses local mock data only. Later this function can be replaced
    or extended with a real AniList GraphQL request without changing the UI
    call site.
    """
    results = get_mock_anime_results()
    normalized_query = query.strip().casefold()

    if not normalized_query:
        return results

    return [
        result
        for result in results
        if _matches_query(result, normalized_query)
    ]


def search_anime_titles(query: str = "") -> list[str]:
    """Return romaji anime title matches for UI autocomplete."""
    return [result.title_romaji for result in search_anime(query)]


def _matches_query(result: AnimeSearchResult, normalized_query: str) -> bool:
    searchable_values = (
        result.title_romaji,
        result.title_english,
        result.title_native,
        str(result.season_year) if result.season_year is not None else None,
    )

    return any(
        normalized_query in value.casefold()
        for value in searchable_values
        if value
    )
