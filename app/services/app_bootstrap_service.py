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


def show_main_window(window):
    window_width, window_height = window.get_default_window_size()
    minimum_width, minimum_height = window.get_minimum_window_size()
    window.resize(window_width, window_height)
    window.setMinimumSize(minimum_width, minimum_height)
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
    window = window_factory()

    apply_app_icon(
        app,
        window,
        load_icon_func=load_icon_func,
    )
    show_main_window(window)

    exit_code = app.exec()
    log_info_func("app", f"AkihabaraiScore stopped: exit_code={exit_code}")
    exit_func(exit_code)
