"""Real AniList GraphQL API provider.

This module contains the network-facing AniList implementation.
It is intentionally not wired into the UI yet; the current feature slice is a
connectivity and JSON-mapping proof only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from app.core.models import AnimeSearchResult
from app.logger import log_debug, log_warning

ANILIST_GRAPHQL_URL = "https://graphql.anilist.co"
DEFAULT_TIMEOUT_SECONDS = 8
DEFAULT_PER_PAGE = 10
ANILIST_APP_USER_AGENT = "AkihabaraiScore/0.13.0"
ANILIST_REQUEST_HEADERS = {
    "User-Agent": ANILIST_APP_USER_AGENT,
}


@dataclass(frozen=True)
class AniListApiSearchResponse:
    results: list[AnimeSearchResult]
    error: str | None = None
    error_detail: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None


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
    """Backward-compatible list-only AniList search helper."""
    return search_anime_api_response(
        query,
        per_page=per_page,
        timeout_seconds=timeout_seconds,
    ).results


def search_anime_api_response(
    query: str,
    *,
    per_page: int = DEFAULT_PER_PAGE,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> AniListApiSearchResponse:
    """Search AniList and return both results and explicit error state."""
    normalized_query = query.strip()
    if not normalized_query:
        return AniListApiSearchResponse(results=[])

    log_debug(
        "anilist",
        f"api_search_started: query='{normalized_query}' per_page={per_page}",
    )

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
            headers=ANILIST_REQUEST_HEADERS,
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
    except requests.Timeout as exc:
        return _api_error_response("api_request_timeout", exc)
    except requests.RequestException as exc:
        return _api_error_response("api_request_failed", exc)
    except ValueError as exc:
        return _api_error_response("api_response_json_parse_failed", exc)

    if not isinstance(data, dict):
        return _api_error_response(
            "api_response_invalid",
            "root is not an object",
        )

    if data.get("errors"):
        return _api_error_response("api_response_errors", data.get("errors"))

    media_items = (
        data.get("data", {})
        .get("Page", {})
        .get("media", [])
    )

    if not isinstance(media_items, list):
        return _api_error_response(
            "api_response_invalid",
            "media is not a list",
        )

    results = [
        result
        for item in media_items
        if (result := _map_media_to_result(item)) is not None
    ]

    log_debug(
        "anilist",
        f"api_search_results: query='{normalized_query}' count={len(results)} "
        f"results={_format_results_for_debug_log(results)}",
    )

    return AniListApiSearchResponse(results=results)


def _api_error_response(reason: str, detail: Any) -> AniListApiSearchResponse:
    detail_text = str(detail)
    log_warning("anilist", f"{reason}: {detail_text}")
    return AniListApiSearchResponse(
        results=[],
        error=reason,
        error_detail=detail_text,
    )


def _format_results_for_debug_log(results: list[AnimeSearchResult]) -> list[dict[str, Any]]:
    return [
        {
            "anilist_id": result.anilist_id,
            "title_romaji": result.title_romaji,
            "title_english": result.title_english,
            "title_native": result.title_native,
            "season_year": result.season_year,
            "cover_url": result.cover_url,
        }
        for result in results
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
