from collections.abc import Callable

from app.logger import log_info, log_warning
from app.services.update_check_service import UpdateCheckResult
from app.widgets.version_button_presenter import (
    build_update_check_version_button_presentation,
)


def apply_update_check_to_version_button(
    *,
    version_btn,
    app_version: str,
    default_button_text: str,
    check_for_update_func: Callable[[str], UpdateCheckResult],
) -> None:
    result = check_for_update_func(app_version)

    if not result.ok:
        log_warning("update_check", f"update_check_failed: {result.error}")
        return

    presentation = build_update_check_version_button_presentation(
        result,
        default_button_text,
    )
    if presentation is not None:
        version_btn.setText(presentation.text)
        version_btn.setStyleSheet(presentation.style_sheet)

    if not result.update_available:
        log_info(
            "update_check",
            f"no_update_available: local='{result.local_version}' latest='{result.latest_version}'",
        )
        return

    log_info(
        "update_check",
        f"update_available: local='{result.local_version}' latest='{result.latest_version}'",
    )
