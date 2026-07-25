"""Compatibility facade for Qt desktop clipboard operations."""

from app.adapters.qt_desktop_adapter import (
    render_widget_to_clipboard_pixmap as copy_widget_as_pixmap,
)
from app.adapters.qt_desktop_adapter import set_clipboard_text as copy_text_to_clipboard

__all__ = ["copy_text_to_clipboard", "copy_widget_as_pixmap"]
