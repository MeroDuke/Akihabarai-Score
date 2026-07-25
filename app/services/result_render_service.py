"""Compatibility facade for Qt pixmap rendering operations."""

from app.adapters.qt_desktop_adapter import trim_pixmap_background as trim_pixmap

__all__ = ["trim_pixmap"]
