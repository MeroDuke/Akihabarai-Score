"""Qt adapter for transient cover image bytes."""

from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtGui import QPixmap

from app.core.models import AnimeSearchResult
from app.logger import log_debug, log_warning
from app.services.cover_image_data_service import (
    CoverImageDataResponse,
    download_cover_image_data,
)


@dataclass(frozen=True)
class CoverPixmapResponse:
    pixmap: QPixmap | None
    error: str | None = None
    error_detail: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.pixmap is not None


def decode_cover_pixmap(data: CoverImageDataResponse) -> CoverPixmapResponse:
    if not data.ok:
        return CoverPixmapResponse(
            pixmap=None,
            error=data.error,
            error_detail=data.error_detail,
        )

    pixmap = QPixmap()
    if not pixmap.loadFromData(data.image_bytes or b""):
        detail = "QPixmap.loadFromData returned False"
        log_warning("cover_image", f"cover_pixmap_decode_failed: {detail}")
        return CoverPixmapResponse(
            pixmap=None,
            error="cover_pixmap_decode_failed",
            error_detail=detail,
        )
    return CoverPixmapResponse(pixmap=pixmap)


def load_cover_pixmap_from_url(url: str | None) -> CoverPixmapResponse:
    return decode_cover_pixmap(download_cover_image_data(url))


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
