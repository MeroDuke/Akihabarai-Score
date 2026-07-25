"""UI-independent translation catalog with Hungarian fallback."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

DEFAULT_LANGUAGE = "hu"
FALLBACK_LANGUAGE = "hu"

HUNGARIAN_MESSAGES = MappingProxyType(
    {
        "app_mode.scored.label": "Adatvezérelt",
        "app_mode.freehand.label": "Szabadkezes",
        "app_mode.scored.switch_tooltip": "Váltás Szabadkezes módra",
        "app_mode.freehand.switch_tooltip": "Váltás Adatvezérelt módra",
        "title_mode.offline.button": "✏ Offline",
        "title_mode.online.button": "🌐 Online",
        "result.strengths": "Erősségek",
        "result.weakness": "Gyengeség",
        "result.profile": "Profil",
        "result.tier": "Tier",
        "result.missing_title": "(nincs cím)",
        "result.empty_value": "—",
        "copy.success": "✔ Másolva!",
        "copy.details.success": "✔ Részletes adatok másolva!",
        "copy.details.action": "Részletes adatok másolása vágólapra",
        "copy.result_image.action": "Eredmény képként másolása",
        "copy.tier_image.action": "Tier lista képként másolása",
        "dialog.config_profiles.title": "Konfigurációs hiba",
        "dialog.config_ui.title": "Felületkonfigurációs hiba",
        "dialog.tier_missing.title": "Hiányzó cím",
        "dialog.tier_missing.message": (
            "Tier listához csak megadott címmel lehet elemet hozzáadni."
        ),
        "dialog.tier_duplicate.title": "Már szerepel",
        "dialog.tier_duplicate.message": "Ez a cím már szerepel a Tier listában.",
        "dialog.tier_copy_error.title": "Másolási hiba",
        "dialog.tier_copy_error.message": (
            "Nem sikerült a Tier listát képként vágólapra másolni."
        ),
        "dialog.tier_clear.title": "Tier lista törlése",
        "dialog.tier_clear.message": (
            "Biztosan törlöd az összes mentett kártyát a Tier listáról?"
        ),
        "dialog.yes": "Igen",
        "dialog.no": "Nem",
    }
)


@dataclass(frozen=True)
class TranslationCatalog:
    language: str
    messages: Mapping[str, str]
    fallback_messages: Mapping[str, str] = HUNGARIAN_MESSAGES

    def translate(self, key: str, **values) -> str:
        template = self.messages.get(key)
        if template is None:
            template = self.fallback_messages.get(key, key)
        try:
            return template.format(**values)
        except (KeyError, ValueError):
            return template


def build_translator(
    language: str = DEFAULT_LANGUAGE,
    messages: Mapping[str, str] | None = None,
) -> TranslationCatalog:
    selected = HUNGARIAN_MESSAGES if language == FALLBACK_LANGUAGE else {}
    if messages is not None:
        selected = dict(messages)
    return TranslationCatalog(language, MappingProxyType(dict(selected)))


def load_translation_catalog(
    path: str | Path,
    *,
    requested_language: str = DEFAULT_LANGUAGE,
) -> TranslationCatalog:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        language = str(payload.get("language") or requested_language)
        messages = payload.get("messages")
        if not isinstance(messages, dict):
            raise ValueError("messages must be an object")
        valid_messages = {
            str(key): str(value)
            for key, value in messages.items()
            if isinstance(key, str) and isinstance(value, str)
        }
        return build_translator(language, valid_messages)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return build_translator(FALLBACK_LANGUAGE)


DEFAULT_TRANSLATOR = build_translator()


def translate(key: str, **values) -> str:
    return DEFAULT_TRANSLATOR.translate(key, **values)
