from dataclasses import dataclass

from app.services.update_check_service import UpdateCheckResult
from app.services.localization_service import translate


UPDATE_AVAILABLE_BUTTON_STYLE = """
    QPushButton {
        background-color: #dc3545;
        color: white;
        font-weight: bold;
    }
"""


@dataclass(frozen=True)
class VersionButtonPresentation:
    text: str
    style_sheet: str


def build_version_button_text(app_version: str) -> str:
    version = app_version.strip()
    if not version.startswith("v"):
        version = f"v{version}"

    return translate("version.current", version=version)


def build_update_check_version_button_presentation(
    result: UpdateCheckResult,
    default_text: str,
) -> VersionButtonPresentation | None:
    if not result.ok:
        return None

    if not result.update_available:
        return VersionButtonPresentation(text=default_text, style_sheet="")

    return VersionButtonPresentation(
        text=translate(
            "version.update_available",
            version=result.latest_version,
        ),
        style_sheet=UPDATE_AVAILABLE_BUTTON_STYLE,
    )
