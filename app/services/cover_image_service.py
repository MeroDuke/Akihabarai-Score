"""Compatibility facade for the runtime-only Qt cover preview workflow."""

from app.services.cover_image_qt_adapter import (
    CoverPixmapResponse,
    decode_cover_pixmap,
    load_cover_pixmap_from_url,
    load_selected_cover_preview_pixmap,
)

CoverImageLoadResponse = CoverPixmapResponse

__all__ = [
    "CoverImageLoadResponse",
    "decode_cover_pixmap",
    "load_cover_pixmap_from_url",
    "load_selected_cover_preview_pixmap",
]
