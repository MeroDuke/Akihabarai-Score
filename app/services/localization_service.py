"""UI-independent translation catalog with Hungarian fallback."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Callable, Mapping

from app.logger import log_info, log_warning

DEFAULT_LANGUAGE = "hu"
FALLBACK_LANGUAGE = "hu"

HUNGARIAN_MESSAGES = MappingProxyType(
    {
        "panel.input.title": "Bevitel",
        "panel.result.title": "Eredmény",
        "panel.tier.title": "Tier lista",
        "input.title.label": "Anime / szezon cím:",
        "input.profile_mix.label": "Profil-mix mód:",
        "input.title.placeholder.offline": "pl. Re:Zero S3",
        "input.title.placeholder.online": "AniList keresés...",
        "profile_mix.single.label": "1 profil",
        "profile_mix.double.label": "2 profil",
        "profile_mix.triple.label": "3 profil",
        "profile_config.title": "Profil konfiguráció",
        "profile_config.profile.header": "Profil",
        "profile_config.weight.header": "Súly (0-100)",
        "profile_config.row.label": "Profil {index}:",
        "profile.inactive": "—",
        "profile.fantasy": "Fantasy",
        "profile.mystery": "Rejtély",
        "profile.romance": "Romantika",
        "profile.drama": "Dráma",
        "profile.action": "Akció",
        "profile.adventure": "Kaland",
        "profile.comedy": "Humor",
        "profile.slice_of_life": "Mindennapi Élet",
        "profile.sci_fi": "Sci-fi",
        "profile.horror": "Horror",
        "dimensions.title": "Dimenziók",
        "dimensions.name.header": "Dimenzió",
        "dimensions.score.header": "Pont (1-10)",
        "dimension.story_plot": "Történet / plot",
        "dimension.characters": "Karakterek",
        "dimension.pacing": "Tempó / epizódritmus",
        "dimension.direction_visual_storytelling": (
            "Rendezés & vizuális történetmesélés"
        ),
        "dimension.animation_choreography": "Animáció & koreográfia",
        "dimension.visual_design": "Vizuális dizájn",
        "dimension.sound": "Hang",
        "dimension.impact_enjoyment": "Hatás / élmény",
        "action.reset": "Alaphelyzet (5,0)",
        "action.add_to_tier": "Hozzáadás Tier listához",
        "action.save_edit": "Szerkesztés mentése",
        "action.cancel_edit": "Szerkesztés megszakítása",
        "version.current": "Verzió: {version}",
        "version.update_available": "Frissítés elérhető: {version}",
        "language.switch.to_en": "🌐 HU → EN",
        "language.switch.to_hu": "🌐 EN → HU",
        "language.switch.tooltip.to_en": "Váltás angol nyelvre",
        "language.switch.tooltip.to_hu": "Switch to Hungarian",
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
        "result.tier_value": "Tier: {tier}",
        "result.missing_title": "(nincs cím)",
        "result.empty_value": "—",
        "result.table.dimension": "Dimenzió",
        "result.table.score": "Pont",
        "result.table.relevance": "Relevancia",
        "result.table.contribution": "Hozzájárulás",
        "copy.success": "✔ Másolva!",
        "copy.details.success": "✔ Részletes adatok másolva!",
        "copy.details.action": "Részletes adatok másolása vágólapra",
        "copy.result_image.action": "Eredmény képként másolása",
        "copy.tier_image.action": "Tier lista képként másolása",
        "tier.flip_all.action": "Összes kártya megfordítása",
        "tier.clear_all.action": "Minden kártya törlése",
        "tier.card.edit_badge": "SZERK.",
        "tier.card.no_image": "NINCS\nKÉP",
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
    fallback_messages: Mapping[str, str] = field(
        default_factory=lambda: HUNGARIAN_MESSAGES
    )

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
_ACTIVE_LOCALIZATION_SERVICE = None


@dataclass(frozen=True)
class LanguageChangeResult:
    requested_language: str
    active_language: str
    previous_language: str
    success: bool
    fallback: bool
    catalog_path: Path
    message_count: int = 0
    reason: str | None = None


class LocalizationService:
    """Runtime catalog owner shared by desktop and future frontends."""

    def __init__(
        self,
        catalog_dir: str | Path,
        *,
        log_info_func: Callable[[str, str], None] = log_info,
        log_warning_func: Callable[[str, str], None] = log_warning,
    ):
        self.catalog_dir = Path(catalog_dir)
        self._log_info = log_info_func
        self._log_warning = log_warning_func
        self._missing_key_logs: set[tuple[str, str]] = set()
        self._catalog = build_translator(FALLBACK_LANGUAGE)
        self._fallback_catalog = self._load_catalog(FALLBACK_LANGUAGE)
        if self._fallback_catalog is not None:
            self._catalog = self._fallback_catalog

    @property
    def active_language(self) -> str:
        return self._catalog.language

    def catalog_path(self, language: str) -> Path:
        return self.catalog_dir / f"{language}.json"

    def _load_catalog(self, language: str) -> TranslationCatalog | None:
        path = self.catalog_path(language)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            declared_language = payload.get("language")
            messages = payload.get("messages")
            if declared_language != language:
                raise ValueError(
                    f"catalog language is {declared_language!r}, expected {language!r}"
                )
            if not isinstance(messages, dict):
                raise ValueError("messages must be an object")
            if not all(
                isinstance(key, str) and isinstance(value, str)
                for key, value in messages.items()
            ):
                raise ValueError("catalog messages must contain string pairs")
            fallback_messages = (
                self._fallback_catalog.messages
                if language != FALLBACK_LANGUAGE
                and getattr(self, "_fallback_catalog", None) is not None
                else HUNGARIAN_MESSAGES
            )
            return TranslationCatalog(
                language,
                MappingProxyType(dict(messages)),
                fallback_messages,
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return None

    def switch_language(
        self,
        requested_language: str,
        *,
        request_id: str,
        source: str,
    ) -> LanguageChangeResult:
        previous_language = self.active_language
        requested = requested_language.strip().lower()
        path = self.catalog_path(requested)
        self._log_info(
            "localization",
            "language_change_received: "
            f"request_id='{request_id}' source='{source}' "
            f"previous_language='{previous_language}' "
            f"requested_language='{requested}'",
        )
        exists = path.is_file()
        self._log_info(
            "localization",
            "catalog_lookup: "
            f"request_id='{request_id}' language='{requested}' "
            f"path='{path}' exists={str(exists).lower()}",
        )

        catalog = self._load_catalog(requested) if exists else None
        if catalog is not None:
            self._catalog = catalog
            self._log_info(
                "localization",
                "catalog_load_completed: "
                f"request_id='{request_id}' language='{requested}' "
                f"path='{path}' success=true "
                f"message_count={len(catalog.messages)} fallback=false",
            )
            result = LanguageChangeResult(
                requested,
                catalog.language,
                previous_language,
                True,
                False,
                path,
                len(catalog.messages),
            )
        else:
            reason = "catalog_invalid" if exists else "catalog_missing"
            self._log_warning(
                "localization",
                "catalog_load_failed: "
                f"request_id='{request_id}' language='{requested}' "
                f"path='{path}' success=false reason='{reason}'",
            )
            fallback_catalog = self._fallback_catalog or build_translator(
                FALLBACK_LANGUAGE
            )
            self._catalog = fallback_catalog
            result = LanguageChangeResult(
                requested,
                FALLBACK_LANGUAGE,
                previous_language,
                False,
                True,
                path,
                len(fallback_catalog.messages),
                reason,
            )

        self._log_info(
            "localization",
            "language_change_completed: "
            f"request_id='{request_id}' "
            f"previous_language='{previous_language}' "
            f"requested_language='{requested}' "
            f"active_language='{result.active_language}' "
            f"success={str(result.success).lower()} "
            f"fallback={str(result.fallback).lower()}",
        )
        return result

    def translate(self, key: str, **values) -> str:
        if key not in self._catalog.messages:
            marker = (self.active_language, key)
            if marker not in self._missing_key_logs:
                self._missing_key_logs.add(marker)
                self._log_warning(
                    "localization",
                    "translation_key_fallback: "
                    f"language='{self.active_language}' key='{key}' "
                    f"fallback_language='{FALLBACK_LANGUAGE}'",
                )
        return self._catalog.translate(key, **values)


def set_active_localization_service(service: LocalizationService | None) -> None:
    global _ACTIVE_LOCALIZATION_SERVICE
    _ACTIVE_LOCALIZATION_SERVICE = service


def translate(key: str, **values) -> str:
    if _ACTIVE_LOCALIZATION_SERVICE is not None:
        return _ACTIVE_LOCALIZATION_SERVICE.translate(key, **values)
    return DEFAULT_TRANSLATOR.translate(key, **values)
