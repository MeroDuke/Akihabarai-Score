from __future__ import annotations

import ctypes
import sys
import traceback
from collections.abc import Callable, Sequence

from PyQt6.QtWidgets import QApplication

from app.core.runtime import load_app_icon
from app.logger import init_logger, log_error, log_info

DEFAULT_APP_USER_MODEL_ID = "akihabarai_konyvespolc.score"


def set_windows_app_user_model_id(
    app_user_model_id: str,
    *,
    ctypes_module=ctypes,
    platform: str = sys.platform,
):
    if platform != "win32":
        return

    windll = getattr(ctypes_module, "windll", None)
    if windll is None:
        return

    windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_user_model_id)


def apply_app_icon(
    app,
    window,
    *,
    load_icon_func: Callable = load_app_icon,
):
    icon = load_icon_func()
    if icon is None:
        return None

    app.setWindowIcon(icon)
    window.setWindowIcon(icon)
    return icon


def _format_rect(rect) -> str:
    return f"{rect.x()},{rect.y()} {rect.width()}x{rect.height()}"


def select_and_log_startup_screen(
    app,
    *,
    log_info_func: Callable[[str, str], None] = log_info,
):
    """Freeze the primary screen as the startup target and record DPI context."""
    primary_screen = app.primaryScreen()
    screens = list(app.screens())
    if primary_screen is not None and primary_screen not in screens:
        screens.insert(0, primary_screen)

    for screen in screens:
        log_info_func(
            "app",
            "display_detected: "
            f"name='{screen.name()}' "
            f"primary={str(screen is primary_screen).lower()} "
            f"geometry={_format_rect(screen.geometry())} "
            f"available={_format_rect(screen.availableGeometry())} "
            f"device_pixel_ratio={screen.devicePixelRatio():.3f} "
            f"logical_dpi={screen.logicalDotsPerInch():.3f}",
        )

    return primary_screen


def show_main_window(
    window,
    *,
    screen=None,
    log_info_func: Callable[[str, str], None] = log_info,
):
    window_width, window_height = window.get_default_window_size()
    minimum_width, minimum_height = window.get_minimum_window_size()

    if screen is None:
        window.resize(window_width, window_height)
        window.setMinimumSize(minimum_width, minimum_height)
        window.show()
        return

    available = screen.availableGeometry()
    available_width = max(1, available.width())
    available_height = max(1, available.height())
    applied_width = min(max(window_width, minimum_width), available_width)
    applied_height = min(max(window_height, minimum_height), available_height)
    applied_minimum_width = min(minimum_width, applied_width)
    applied_minimum_height = min(minimum_height, applied_height)
    window_x = available.x() + (available_width - applied_width) // 2
    window_y = available.y() + (available_height - applied_height) // 2

    window.setMinimumSize(applied_minimum_width, applied_minimum_height)
    window.setGeometry(
        window_x,
        window_y,
        applied_width,
        applied_height,
    )
    log_info_func(
        "app",
        "startup_window_geometry: "
        f"screen='{screen.name()}' "
        f"available={_format_rect(available)} "
        f"requested_size={window_width}x{window_height} "
        f"requested_minimum={minimum_width}x{minimum_height} "
        f"applied_size={applied_width}x{applied_height} "
        f"applied_minimum={applied_minimum_width}x{applied_minimum_height} "
        f"position={window_x},{window_y}",
    )
    window.show()


def build_unhandled_exception_hook(
    *,
    log_error_func: Callable[[str, str], None] = log_error,
    fallback_hook: Callable = sys.__excepthook__,
):
    def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
        formatted = "".join(
            traceback.format_exception(exc_type, exc_value, exc_traceback)
        ).strip()
        log_error_func("app", f"unhandled_exception: {formatted}")
        fallback_hook(exc_type, exc_value, exc_traceback)

    return handle_unhandled_exception


def run_qt_application(
    *,
    window_factory: Callable,
    argv: Sequence[str] | None = None,
    app_user_model_id: str = DEFAULT_APP_USER_MODEL_ID,
    qapplication_class=QApplication,
    init_logger_func: Callable[[], None] = init_logger,
    log_info_func: Callable[[str, str], None] = log_info,
    log_error_func: Callable[[str, str], None] = log_error,
    load_icon_func: Callable = load_app_icon,
    ctypes_module=ctypes,
    platform: str = sys.platform,
    exit_func: Callable[[int], None] = sys.exit,
    set_exception_hook_func: Callable[[Callable], None] | None = None,
    fallback_exception_hook: Callable = sys.__excepthook__,
):
    init_logger_func()
    log_info_func("app", "Starting AkihabaraiScore")
    exception_hook = build_unhandled_exception_hook(
        log_error_func=log_error_func,
        fallback_hook=fallback_exception_hook,
    )
    if set_exception_hook_func is None:
        sys.excepthook = exception_hook
    else:
        set_exception_hook_func(exception_hook)

    set_windows_app_user_model_id(
        app_user_model_id,
        ctypes_module=ctypes_module,
        platform=platform,
    )

    app = qapplication_class(list(sys.argv if argv is None else argv))
    startup_screen = select_and_log_startup_screen(
        app,
        log_info_func=log_info_func,
    )
    window = window_factory()

    apply_app_icon(
        app,
        window,
        load_icon_func=load_icon_func,
    )
    show_main_window(
        window,
        screen=startup_screen,
        log_info_func=log_info_func,
    )
    log_info_func("app", "Main window ready")

    exit_code = app.exec()
    log_info_func("app", f"AkihabaraiScore stopped: exit_code={exit_code}")
    exit_func(exit_code)
