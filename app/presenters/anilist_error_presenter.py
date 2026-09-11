"""Localized presentation for runtime AniList search failures."""

from __future__ import annotations

from collections.abc import Callable


def build_anilist_error_text(
    *,
    reason: str,
    http_status: int | None,
    translate: Callable[..., str],
) -> str:
    if http_status is not None:
        return translate("anilist.error.http", status=http_status)

    if reason == "api_request_timeout":
        return translate("anilist.error.timeout")

    return translate("anilist.error.connection")
