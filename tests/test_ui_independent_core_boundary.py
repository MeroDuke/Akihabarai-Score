"""Architecture gate for the reusable application core."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


UI_INDEPENDENT_MODULES = (
    "app.core.constants",
    "app.core.formatters",
    "app.core.models",
    "app.scoring",
    "app.services.application_session_service",
    "app.services.app_mode_service",
    "app.services.localization_service",
    "app.services.profile_mix_service",
    "app.services.result_content_service",
    "app.services.scoring_pipeline",
    "app.services.tier_board_service",
    "app.services.tier_card_edit_session_service",
    "app.services.title_search_state_service",
    "app.services.title_selection_service",
)


def test_reusable_application_core_imports_without_pyqt():
    project_root = Path(__file__).resolve().parents[1]
    import_script = f"""
import builtins

real_import = builtins.__import__

def import_without_qt(name, *args, **kwargs):
    if name == "PyQt6" or name.startswith("PyQt6."):
        raise AssertionError(f"UI-independent core imported {{name}}")
    return real_import(name, *args, **kwargs)

builtins.__import__ = import_without_qt

for module_name in {UI_INDEPENDENT_MODULES!r}:
    __import__(module_name)
"""
    completed = subprocess.run(
        [sys.executable, "-c", import_script],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
