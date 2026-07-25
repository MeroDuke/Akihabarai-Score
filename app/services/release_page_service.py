from collections.abc import Callable

from app.adapters.qt_desktop_adapter import build_native_url, open_native_url


def open_release_page(
    releases_url: str,
    open_url: Callable[[object], object] | None = None,
) -> object:
    if open_url is None:
        return open_native_url(releases_url)

    return open_url(build_native_url(releases_url))
