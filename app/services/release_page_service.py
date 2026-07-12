from collections.abc import Callable

from PyQt6.QtCore import QUrl


def open_release_page(
    releases_url: str,
    open_url: Callable[[QUrl], object],
) -> object:
    return open_url(QUrl(releases_url))
