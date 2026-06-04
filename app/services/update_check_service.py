from dataclasses import dataclass
import json
import urllib.error
import urllib.request

from app.version import APP_USER_AGENT

GITHUB_LATEST_RELEASE_API_URL = (
    "https://api.github.com/repos/MeroDuke/Akihabarai-Score/releases/latest"
)


@dataclass(frozen=True)
class UpdateCheckResult:
    ok: bool
    update_available: bool = False
    local_version: str = ""
    latest_version: str = ""
    error: str = ""


def normalize_version(version: str) -> str:
    cleaned = version.strip()
    if not cleaned:
        raise ValueError("empty version")

    if cleaned.startswith("v"):
        cleaned = cleaned[1:]

    parts = cleaned.split(".")
    if len(parts) != 3:
        raise ValueError(f"invalid version format: {version!r}")

    for part in parts:
        if not part.isdigit():
            raise ValueError(f"invalid version format: {version!r}")

    return ".".join(parts)


def version_to_tuple(version: str) -> tuple[int, int, int]:
    normalized = normalize_version(version)
    return tuple(int(part) for part in normalized.split("."))


def format_version(version: str) -> str:
    return f"v{normalize_version(version)}"


def fetch_latest_release_version(timeout_seconds: int = 5) -> str:
    request = urllib.request.Request(
        GITHUB_LATEST_RELEASE_API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": APP_USER_AGENT,
        },
    )

    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))

    tag_name = payload.get("tag_name", "")
    return format_version(tag_name)


def check_for_update(local_version: str) -> UpdateCheckResult:
    try:
        local_display_version = format_version(local_version)
        latest_display_version = fetch_latest_release_version()

        update_available = (
            version_to_tuple(latest_display_version) > version_to_tuple(local_display_version)
        )

        return UpdateCheckResult(
            ok=True,
            update_available=update_available,
            local_version=local_display_version,
            latest_version=latest_display_version,
        )
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        return UpdateCheckResult(ok=False, error=str(exc))
