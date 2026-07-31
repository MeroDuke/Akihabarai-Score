"""User-scoped JSON preferences independent from Qt and packaged config."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from app.logger import log_info, log_warning
from app.services.localization_service import DEFAULT_LANGUAGE


PREFERENCES_SCHEMA_VERSION = 1
SUPPORTED_LANGUAGES = {"hu", "en"}


def default_preferences_path(
    *,
    environ: dict[str, str] | None = None,
    platform: str = sys.platform,
    home: Path | None = None,
) -> Path:
    env = os.environ if environ is None else environ
    user_home = Path.home() if home is None else Path(home)
    if platform == "win32":
        base = Path(env.get("APPDATA") or user_home / "AppData" / "Roaming")
        return base / "AkihabaraiScore" / "preferences.json"

    base = Path(env.get("XDG_CONFIG_HOME") or user_home / ".config")
    return base / "akihabarai-score" / "preferences.json"


@dataclass(frozen=True)
class PreferenceSaveResult:
    success: bool
    path: Path
    reason: str | None = None


class JsonPreferenceStore:
    def __init__(
        self,
        path: str | Path | None = None,
        *,
        log_info_func: Callable[[str, str], None] = log_info,
        log_warning_func: Callable[[str, str], None] = log_warning,
    ):
        self.path = default_preferences_path() if path is None else Path(path)
        self._log_info = log_info_func
        self._log_warning = log_warning_func

    def _read_payload(self) -> dict:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else {}
        except FileNotFoundError:
            return {}
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            self._log_warning(
                "preferences",
                f"preference_load_failed: path='{self.path}' "
                f"reason='{type(exc).__name__}'",
            )
            return {}

    def load_language(self) -> str:
        payload = self._read_payload()
        ui = payload.get("ui")
        language = ui.get("language") if isinstance(ui, dict) else None
        if language not in SUPPORTED_LANGUAGES:
            return DEFAULT_LANGUAGE
        return language

    def save_language(
        self,
        language: str,
        *,
        request_id: str,
    ) -> PreferenceSaveResult:
        payload = self._read_payload()
        payload["schema_version"] = PREFERENCES_SCHEMA_VERSION
        ui = payload.get("ui")
        if not isinstance(ui, dict):
            ui = {}
            payload["ui"] = ui
        ui["language"] = (
            language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
        )
        temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            os.replace(temporary_path, self.path)
            self._log_info(
                "preferences",
                "preference_save_completed: "
                f"request_id='{request_id}' key='ui.language' "
                f"value='{ui['language']}' path='{self.path}' success=true",
            )
            return PreferenceSaveResult(True, self.path)
        except OSError as exc:
            self._log_warning(
                "preferences",
                "preference_save_completed: "
                f"request_id='{request_id}' key='ui.language' "
                f"value='{ui['language']}' path='{self.path}' "
                f"success=false reason='{type(exc).__name__}'",
            )
            return PreferenceSaveResult(False, self.path, type(exc).__name__)
        finally:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
