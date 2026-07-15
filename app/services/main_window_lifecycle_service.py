from __future__ import annotations

from collections.abc import Callable

from app.controllers.anilist_title_search_controller import AniListTitleSearchController
from app.core.models import AnimeSearchResult
from app.services.main_window_config_service import MainWindowConfig
from app.services.main_window_layout_service import MainWindowLayout
from app.services.main_window_mode_service import DEFAULT_APP_MODE
from app.services.main_window_score_workflow_service import (
    build_default_profile_selection_memory,
)
from app.widgets.config_messages import (
    show_profiles_config_error,
    show_ui_config_error,
)


def apply_main_window_config_to_window(window, config: MainWindowConfig):
    window.dimensions = config.dimensions
    window.profiles = config.profiles
    window.tier_thresholds = config.tier_thresholds
    window.ui_cfg = config.ui_cfg
    window.anilist_integration_enabled = config.anilist_integration_enabled
    window.title_placeholder_offline = config.title_placeholder_offline
    window.title_placeholder_online = config.title_placeholder_online
    window.title_search_debounce_ms = config.title_search_debounce_ms
    window.title_max_length = config.title_max_length
    window.default_window_size = config.default_window_size
    window.minimum_window_size = config.minimum_window_size
    window.title_input_mode = window.TITLE_INPUT_MODE_OFFLINE
    window.selected_anime_result: AnimeSearchResult | None = None
    window.selected_cover_pixmap = None
    window.title_search_controller: AniListTitleSearchController | None = None


def initialize_main_window_runtime_state(window, dim_state_factory: Callable[[str], object]):
    window.states = [dim_state_factory(name) for name in window.dimensions]
    window._building = True

    window.profile_combos = []
    window.weight_spins = []
    window.slider_widgets = []
    window.spin_widgets = []
    window.profile_names = list(window.profiles.keys()) or ["(nincs profil betöltve)"]
    window.profile_selection_memory = build_default_profile_selection_memory(
        window.profiles
    )
    window.current_mix_needed = 1
    window.current_mode = DEFAULT_APP_MODE


def bind_main_window_layout_widgets(window, layout: MainWindowLayout):
    window.main_layout = layout.main_layout
    window.left_box = layout.left_box
    window.left_layout = layout.left_layout
    window.top_inputs_panel = layout.top_inputs_panel
    window.profile_mix_panel = layout.profile_mix_panel
    window.dimensions_panel = layout.dimensions_panel
    window.action_buttons_panel = layout.action_buttons_panel
    window.result_panel = layout.result_panel
    window.right_box = layout.right_box
    window.tier_panel = layout.tier_panel
    window.tier_box = layout.tier_box

    window.title_edit = window.top_inputs_panel.title_edit
    window.title_mode_btn = window.top_inputs_panel.title_mode_btn
    window.mix_combo = window.top_inputs_panel.mix_combo
    window.profile_combos = window.profile_mix_panel.profile_combos
    window.weight_spins = window.profile_mix_panel.weight_spins
    window.slider_widgets = window.dimensions_panel.slider_widgets
    window.spin_widgets = window.dimensions_panel.spin_widgets
    window.version_btn = window.action_buttons_panel.version_btn
    window.mode_btn = window.action_buttons_panel.mode_btn
    window.reset_btn = window.action_buttons_panel.reset_btn
    window.add_tier_btn = window.action_buttons_panel.add_tier_btn
    window.score_label = window.result_panel.score_label
    window.tier_label = window.result_panel.tier_label
    window.summary_label = window.result_panel.summary_label
    window.result_card = window.result_panel.result_card
    window.copy_img_btn = window.result_panel.copy_img_btn
    window.table = window.result_panel.table
    window.copy_btn = window.result_panel.copy_btn
    window.tier_board = window.tier_panel.tier_board
    window.tier_scroll_area = window.tier_panel.tier_scroll_area
    window.flip_all_tier_cards_btn = window.tier_panel.flip_all_tier_cards_btn
    window.clear_all_tier_cards_btn = window.tier_panel.clear_all_tier_cards_btn
    window.copy_tier_btn = window.tier_panel.copy_tier_btn


def initialize_main_window_after_layout(window):
    window._setup_title_autocomplete()
    window._sync_title_mode_ui(log_change=False)
    window.update_add_tier_button_state(window.title_edit.text())
    window.apply_app_mode()


def finish_main_window_startup(
    window,
    *,
    profiles_error,
    ui_error,
    schedule_update_check: Callable[[int, Callable[[], None]], None],
    log_info_func: Callable[[str, str], None],
    log_warning_func: Callable[[str, str], None],
    show_profiles_config_error_func: Callable = show_profiles_config_error,
    show_ui_config_error_func: Callable = show_ui_config_error,
):
    window._building = False
    post_init_config_messages_for_window(
        window,
        profiles_error=profiles_error,
        ui_error=ui_error,
        log_info_func=log_info_func,
        log_warning_func=log_warning_func,
        show_profiles_config_error_func=show_profiles_config_error_func,
        show_ui_config_error_func=show_ui_config_error_func,
    )
    window._apply_initial_weights()
    window.on_mix_changed()
    schedule_update_check(250, window.check_for_updates)


def post_init_config_messages_for_window(
    window,
    *,
    profiles_error,
    ui_error,
    log_info_func: Callable[[str, str], None],
    log_warning_func: Callable[[str, str], None],
    show_profiles_config_error_func: Callable = show_profiles_config_error,
    show_ui_config_error_func: Callable = show_ui_config_error,
):
    log_info_func(
        "config",
        f"Loaded profiles: dims={len(window.dimensions)}, profiles={len(window.profiles)}",
    )
    if profiles_error:
        log_warning_func("config", f"profiles.json issue: {profiles_error}")

    log_info_func("config", "Loaded UI config")
    if ui_error:
        log_warning_func("config", f"ui.json issue: {ui_error}")

    if profiles_error:
        show_profiles_config_error_func(window, profiles_error)

    if ui_error:
        show_ui_config_error_func(window, ui_error)
