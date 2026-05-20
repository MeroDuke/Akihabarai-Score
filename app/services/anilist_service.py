"""AniList service layer.

This module is the single application-facing entry point for AniList title
searches. The current implementation intentionally delegates to the mock
provider, so the UI can depend on the service interface before real network
logic is introduced.
"""

from app.services.anilist_mock_provider import get_mock_anime_titles


def search_anime_titles(query: str = "") -> list[str]:
    """Return anime title matches for the given query.

    For now this uses local mock data only. Later this function can be replaced
    or extended with a real AniList GraphQL request without changing the UI
    call site.
    """
    titles = get_mock_anime_titles()
    normalized_query = query.strip().casefold()

    if not normalized_query:
        return titles

    return [
        title
        for title in titles
        if normalized_query in title.casefold()
    ]
