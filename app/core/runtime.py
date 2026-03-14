import sys
from pathlib import Path
from PyQt6.QtGui import QIcon

from app.logger import log_debug, log_warning


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def load_app_icon() -> QIcon | None:
    icon_path = app_dir() / "assets" / "icon.ico"

    if icon_path.exists():
        log_debug("runtime", f"Application icon loaded from {icon_path}")
        return QIcon(str(icon_path))

    log_warning("runtime", f"Application icon not found: {icon_path}")
    return None