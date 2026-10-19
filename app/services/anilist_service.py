"""AniList service layer.

This module is the single application-facing entry point for AniList searches.
Offline search uses the bundled mock data, while online search delegates to the
real AniList API provider through explicit response objects.
"""

from app.core.models import AnimeSearchResult
from app.services.anilist_api_provider import (
    AniListApiSearchResponse,
    search_anime_api,
    search_anime_api_response,
)
from app.services.anilist_mock_provider import get_mock_anime_results


def search_anime(query: str = "") -> list[AnimeSearchResult]:
    """Return structured mock anime matches for the given query.

    This is the application's Offline-mode search path.
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


def search_anime_online(query: str = "") -> list[AnimeSearchResult]:
    """Return online anime matches from the real AniList API provider."""
    return search_anime_api(query)


def search_anime_online_response(query: str = "") -> AniListApiSearchResponse:
    """Return structured online search results plus explicit error state."""
    return search_anime_api_response(query)


def search_anime_titles_online(query: str = "") -> list[str]:
    """Return romaji anime titles from the real AniList API provider."""
    return [result.title_romaji for result in search_anime_online(query)]


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
