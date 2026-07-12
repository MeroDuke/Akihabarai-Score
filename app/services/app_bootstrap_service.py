from __future__ import annotations

import ctypes
import sys
from collections.abc import Callable, Sequence

from PyQt6.QtWidgets import QApplication

from app.core.runtime import load_app_icon
from app.logger import init_logger, log_info

DEFAULT_APP_USER_MODEL_ID = "akihabarai_konyvespolc.score"


def set_windows_app_user_model_id(
    app_user_model_id: str,
    *,
    ctypes_module=ctypes,
):
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


def run_qt_application(
    *,
    window_factory: Callable,
    argv: Sequence[str] | None = None,
    app_user_model_id: str = DEFAULT_APP_USER_MODEL_ID,
    qapplication_class=QApplication,
    init_logger_func: Callable[[], None] = init_logger,
    log_info_func: Callable[[str, str], None] = log_info,
    load_icon_func: Callable = load_app_icon,
    ctypes_module=ctypes,
    exit_func: Callable[[int], None] = sys.exit,
):
    init_logger_func()
    log_info_func("app", "Starting AkihabaraiScore")

    set_windows_app_user_model_id(
        app_user_model_id,
        ctypes_module=ctypes_module,
    )

    app = qapplication_class(list(sys.argv if argv is None else argv))
    window = window_factory()

    apply_app_icon(
        app,
        window,
        load_icon_func=load_icon_func,
    )
    show_main_window(window)

    exit_func(app.exec())
