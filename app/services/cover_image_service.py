"""Runtime-only cover image loading service.

This module downloads cover images into memory and converts them to QPixmap.
It intentionally does not persist AniList-derived image data to disk and does
not implement any file-system cache.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from PyQt6.QtGui import QPixmap

from app.core.models import AnimeSearchResult
from app.services.anilist_api_provider import ANILIST_REQUEST_HEADERS
from app.logger import log_debug, log_warning

DEFAULT_COVER_TIMEOUT_SECONDS = 8


@dataclass(frozen=True)
class CoverImageLoadResponse:
    """Result object for runtime-only cover image loading."""

    pixmap: QPixmap | None
    error: str | None = None
    error_detail: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.pixmap is not None


def load_cover_pixmap_from_url(
    url: str | None,
    *,
    timeout_seconds: int = DEFAULT_COVER_TIMEOUT_SECONDS,
) -> CoverImageLoadResponse:
    """Download a cover image and return it as a runtime-only QPixmap.

    The image is never written to disk and no cache is created. On any network,
    HTTP, or image-decoding error, the function returns an explicit error state
    with ``pixmap=None``.
    """
    normalized_url = (url or "").strip()
    if not normalized_url:
        return _cover_error_response("cover_url_missing", "empty cover URL")

    log_debug("cover_image", f"cover_download_started: url='{normalized_url}'")

    try:
        response = requests.get(
            normalized_url,
            headers=ANILIST_REQUEST_HEADERS,
            timeout=timeout_seconds,
        )
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            detail = (
                f"rate limit exceeded; retry_after={retry_after}"
                if retry_after
                else "rate limit exceeded"
            )
            return _cover_error_response("cover_rate_limited", detail)

        response.raise_for_status()
    except requests.Timeout as exc:
        return _cover_error_response("cover_request_timeout", exc)
    except requests.RequestException as exc:
        return _cover_error_response("cover_request_failed", exc)

    content_type = response.headers.get("Content-Type", "")
    if content_type and "image" not in content_type.casefold():
        return _cover_error_response(
            "cover_response_not_image",
            f"content_type='{content_type}'",
        )

    image_bytes = response.content
    if not image_bytes:
        return _cover_error_response("cover_response_empty", "empty response body")

    pixmap = QPixmap()
    if not pixmap.loadFromData(image_bytes):
        return _cover_error_response(
            "cover_pixmap_decode_failed",
            "QPixmap.loadFromData returned False",
        )

    log_debug(
        "cover_image",
        "cover_download_completed: "
        f"url='{normalized_url}' bytes={len(image_bytes)} "
        f"width={pixmap.width()} height={pixmap.height()}",
    )
    return CoverImageLoadResponse(pixmap=pixmap)


def load_selected_cover_preview_pixmap(
    selected_anime_result: AnimeSearchResult | None,
) -> QPixmap | None:
    if selected_anime_result is None:
        return None

    if not selected_anime_result.cover_url:
        log_debug(
            "cover_image",
            "cover_preview_skipped: reason='missing_cover_url' "
            f"title='{selected_anime_result.title_romaji}'",
        )
        return None

    response = load_cover_pixmap_from_url(selected_anime_result.cover_url)
    if response.ok:
        log_debug(
            "cover_image",
            "cover_preview_loaded: "
            f"title='{selected_anime_result.title_romaji}' "
            f"anilist_id={selected_anime_result.anilist_id}",
        )
        return response.pixmap

    log_warning(
        "cover_image",
        "cover_preview_fallback_to_text: "
        f"title='{selected_anime_result.title_romaji}' "
        f"reason='{response.error}' detail='{response.error_detail}'",
    )
    return None


def _cover_error_response(reason: str, detail: Any) -> CoverImageLoadResponse:
    detail_text = str(detail)
    log_warning("cover_image", f"{reason}: {detail_text}")
    return CoverImageLoadResponse(
        pixmap=None,
        error=reason,
        error_detail=detail_text,
    )
