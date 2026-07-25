from collections.abc import Callable

from app.services.app_mode_qt_adapter import (
    apply_app_mode_to_window,
    capture_scored_editor,
    restore_scored_editor,
)
from app.services.app_mode_service import (
    APP_MODE_SCORED,
    build_app_mode_capabilities,
    toggle_app_mode,
)


def apply_app_mode_for_window(
    window,
    *,
    log_debug_func: Callable[[str, str], None],
) -> None:
    apply_app_mode_to_window(
        window,
        capabilities=build_app_mode_capabilities(window.app_mode_state.mode),
        log_debug_func=log_debug_func,
    )


def toggle_app_mode_for_window(
    window,
    *,
    log_info_func: Callable[[str, str], None],
    log_debug_func: Callable[[str, str], None],
) -> None:
    log_info_func("ui", "button_click: toggle_app_mode")
    leaving_scored_mode = window.app_mode_state.mode == APP_MODE_SCORED
    transition = toggle_app_mode(
        window.app_mode_state,
        current_editor=(
            capture_scored_editor(window)
            if leaving_scored_mode
            else None
        ),
    )
    window.app_mode_state = transition.state

    if window.app_mode_state.mode == APP_MODE_SCORED:
        restored_editor = restore_scored_editor(
            window,
            transition.editor_to_restore,
        )
        window.tier_board.restore_scored_order(window.tier_thresholds)
        log_debug_func(
            "ui",
            f"scored_editing_state_restored: restored={restored_editor}",
        )

    apply_app_mode_for_window(window, log_debug_func=log_debug_func)
    if window.app_mode_state.mode == APP_MODE_SCORED:
        window.recompute()
    log_info_func(
        "ui",
        f"app_mode_changed: mode='{window.app_mode_state.mode}'",
    )
