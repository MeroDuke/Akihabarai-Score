"""Real AniList GraphQL API provider.

This module contains the network-facing AniList implementation.
It is intentionally not wired into the UI yet; the current feature slice is a
connectivity and JSON-mapping proof only.
"""

from __future__ import annotations

from typing import Any

import requests

from app.core.models import AnimeSearchResult
from app.logger import log_warning

ANILIST_GRAPHQL_URL = "https://graphql.anilist.co"
DEFAULT_TIMEOUT_SECONDS = 8
DEFAULT_PER_PAGE = 10

ANIME_SEARCH_QUERY = """
query ($search: String, $perPage: Int) {
  Page(page: 1, perPage: $perPage) {
    media(search: $search, type: ANIME) {
      id
      title {
        romaji
        english
        native
      }
      coverImage {
        large
        extraLarge
      }
      seasonYear
    }
  }
}
"""


def search_anime_api(
    query: str,
    *,
    per_page: int = DEFAULT_PER_PAGE,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> list[AnimeSearchResult]:
    """Search AniList for anime and map the response to AnimeSearchResult.

    This is a synchronous proof-of-connectivity implementation. It is safe for
    manual smoke tests, but should not be called from a live UI typing event
    until debounce/threading is added.
    """
    normalized_query = query.strip()
    if not normalized_query:
        return []

    payload = {
        "query": ANIME_SEARCH_QUERY,
        "variables": {
            "search": normalized_query,
            "perPage": per_page,
        },
    }

    try:
        response = requests.post(
            ANILIST_GRAPHQL_URL,
            json=payload,
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        log_warning("anilist", f"api_request_failed: {exc}")
        return []
    except ValueError as exc:
        log_warning("anilist", f"api_response_json_parse_failed: {exc}")
        return []

    if not isinstance(data, dict):
        log_warning("anilist", "api_response_invalid: root is not an object")
        return []

    if data.get("errors"):
        log_warning("anilist", f"api_response_errors: {data.get('errors')}")
        return []

    media_items = (
        data.get("data", {})
        .get("Page", {})
        .get("media", [])
    )

    if not isinstance(media_items, list):
        log_warning("anilist", "api_response_invalid: media is not a list")
        return []

    return [
        result
        for item in media_items
        if (result := _map_media_to_result(item)) is not None
    ]


def _map_media_to_result(item: Any) -> AnimeSearchResult | None:
    if not isinstance(item, dict):
        return None

    anilist_id = item.get("id")
    title = item.get("title") or {}
    cover_image = item.get("coverImage") or {}

    if not isinstance(anilist_id, int) or not isinstance(title, dict):
        return None

    title_romaji = title.get("romaji")
    if not title_romaji:
        return None

    cover_url = None
    if isinstance(cover_image, dict):
        cover_url = cover_image.get("extraLarge") or cover_image.get("large")

    return AnimeSearchResult(
        anilist_id=anilist_id,
        title_romaji=title_romaji,
        title_english=title.get("english"),
        title_native=title.get("native"),
        cover_url=cover_url,
        season_year=item.get("seasonYear"),
    )


if __name__ == "__main__":
    results = search_anime_api("Re:Zero", per_page=3)
    for result in results:
        print(
            f"{result.anilist_id} | {result.title_romaji} | "
            f"{result.season_year} | {result.cover_url}"
        )
