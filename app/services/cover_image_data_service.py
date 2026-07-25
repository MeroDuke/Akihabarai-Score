"""Download AniList cover image data into process memory only."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from app.logger import log_debug, log_warning
from app.services.anilist_api_provider import ANILIST_REQUEST_HEADERS

DEFAULT_COVER_TIMEOUT_SECONDS = 8


@dataclass(frozen=True)
class CoverImageDataResponse:
    image_bytes: bytes | None
    content_type: str | None = None
    error: str | None = None
    error_detail: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.image_bytes is not None


def download_cover_image_data(
    url: str | None,
    *,
    timeout_seconds: int = DEFAULT_COVER_TIMEOUT_SECONDS,
) -> CoverImageDataResponse:
    """Return downloaded bytes without caching, persistence, or Qt objects."""
    normalized_url = (url or "").strip()
    if not normalized_url:
        return _error_response("cover_url_missing", "empty cover URL")

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
            return _error_response("cover_rate_limited", detail)
        response.raise_for_status()
    except requests.Timeout as exc:
        return _error_response("cover_request_timeout", exc)
    except requests.RequestException as exc:
        return _error_response("cover_request_failed", exc)

    content_type = response.headers.get("Content-Type", "")
    if content_type and "image" not in content_type.casefold():
        return _error_response(
            "cover_response_not_image",
            f"content_type='{content_type}'",
        )
    if not response.content:
        return _error_response("cover_response_empty", "empty response body")

    log_debug(
        "cover_image",
        f"cover_download_completed: url='{normalized_url}' "
        f"bytes={len(response.content)}",
    )
    return CoverImageDataResponse(
        image_bytes=bytes(response.content),
        content_type=content_type or None,
    )


def _error_response(reason: str, detail: Any) -> CoverImageDataResponse:
    detail_text = str(detail)
    log_warning("cover_image", f"{reason}: {detail_text}")
    return CoverImageDataResponse(
        image_bytes=None,
        error=reason,
        error_detail=detail_text,
    )
