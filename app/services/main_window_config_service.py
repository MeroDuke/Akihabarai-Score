from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.config.ui_settings import (
    get_anilist_int_setting,
    get_anilist_text_setting,
    get_window_size,
    is_anilist_integration_enabled,
)


@dataclass
class MainWindowConfig:
    dimensions: list[str] | None
    profiles: dict | None
    tier_thresholds: dict | None
    profiles_error: str | None
    ui_cfg: dict
    ui_error: str | None
    anilist_integration_enabled: bool
    title_placeholder_offline: str
    title_placeholder_online: str
    title_search_debounce_ms: int
    title_max_length: int
    default_window_size: tuple[int, int]
    minimum_window_size: tuple[int, int]

    @property
    def profiles_config_loaded(self) -> bool:
        return (
            self.dimensions is not None
            and self.profiles is not None
            and self.tier_thresholds is not None
        )


def load_main_window_config(
    *,
    load_profiles_config_func: Callable[[], tuple],
    load_ui_config_func: Callable[[], tuple],
    default_title_placeholder_offline: str,
    default_title_placeholder_online: str,
    default_title_search_debounce_ms: int,
    default_title_max_length: int,
    default_window_width: int,
    default_window_height: int,
    default_minimum_window_width: int,
    default_minimum_window_height: int,
) -> MainWindowConfig:
    dimensions, profiles, tier_thresholds, profiles_error = load_profiles_config_func()
    ui_cfg, ui_error = load_ui_config_func()

    return MainWindowConfig(
        dimensions=dimensions,
        profiles=profiles,
        tier_thresholds=tier_thresholds,
        profiles_error=profiles_error,
        ui_cfg=ui_cfg,
        ui_error=ui_error,
        anilist_integration_enabled=is_anilist_integration_enabled(ui_cfg),
        title_placeholder_offline=get_anilist_text_setting(
            ui_cfg,
            "title_placeholder_offline",
            default_title_placeholder_offline,
        ),
        title_placeholder_online=get_anilist_text_setting(
            ui_cfg,
            "title_placeholder_online",
            default_title_placeholder_online,
        ),
        title_search_debounce_ms=get_anilist_int_setting(
            ui_cfg,
            "title_search_debounce_ms",
            default_title_search_debounce_ms,
        ),
        title_max_length=get_anilist_int_setting(
            ui_cfg,
            "title_max_length",
            default_title_max_length,
        ),
        default_window_size=get_window_size(
            ui_cfg,
            width_key="default_width",
            height_key="default_height",
            default_width=default_window_width,
            default_height=default_window_height,
        ),
        minimum_window_size=get_window_size(
            ui_cfg,
            width_key="minimum_width",
            height_key="minimum_height",
            default_width=default_minimum_window_width,
            default_height=default_minimum_window_height,
        ),
    )
