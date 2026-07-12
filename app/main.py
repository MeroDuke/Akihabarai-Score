from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QMainWindow

from app.core.constants import APP_TITLE, MIX_MODES, TOTAL_WEIGHT
from app.version import APP_VERSION
from app.services.update_check_service import check_for_update
from app.core.models import AnimeSearchResult, DimState
from app.config.ui_config import load_ui_config
from app.config.profiles_config import load_profiles_config
from app.logger import log_debug, log_info, log_warning
from app.services.app_bootstrap_service import run_qt_application
from app.services.scoring_pipeline import build_result_payload
from app.services.main_window_config_service import load_main_window_config
from app.services.main_window_layout_service import build_main_window_layout
from app.services.main_window_lifecycle_service import (
    apply_main_window_config_to_window,
    bind_main_window_layout_widgets,
    finish_main_window_startup,
    initialize_main_window_after_layout,
    initialize_main_window_runtime_state,
    post_init_config_messages_for_window,
)
from app.services.main_window_input_workflow_service import (
    apply_initial_profile_weights_for_window,
    handle_dimension_slider_change_for_window,
    handle_dimension_spin_change_for_window,
    handle_mix_change_for_window,
    handle_profile_change_for_window,
    handle_profile_weight_change_for_window,
    reset_score_inputs_for_window,
    update_profile_combo_options_for_window,
)
from app.services.main_window_output_workflow_service import (
    add_current_result_to_tier_board_for_window,
    ask_clear_all_tier_cards_confirmation_for_window,
    check_for_updates_for_window,
    clear_all_tier_cards_for_window,
    copy_details_to_clipboard_for_window,
    copy_result_image_to_clipboard_for_window,
    copy_tier_image_to_clipboard_for_window,
    flip_all_tier_cards_for_window,
    open_releases_page_for_window,
    recompute_for_window,
    update_add_tier_button_state_for_window,
    update_tier_buttons_state_for_window,
)
from app.services.main_window_title_workflow_service import (
    disable_title_autocomplete_for_window,
    enable_title_autocomplete_for_window,
    find_anime_result_by_title_for_window,
    get_pending_title_search_query,
    get_title_search_timer,
    handle_title_autocomplete_selected_for_window,
    handle_title_search_text_changed_for_window,
    load_selected_cover_pixmap_for_window,
    refresh_title_autocomplete_results_for_window,
    run_debounced_title_search_for_window,
    schedule_online_title_search_for_window,
    set_selected_title_state_for_window,
    setup_title_autocomplete_for_window,
    sync_title_input_mode_for_window,
    toggle_title_input_mode_for_window,
)
from app.widgets.tier_clear_confirmation_dialog import ask_tier_clear_all_confirmation
from app.widgets.version_button_presenter import (
    build_version_button_text,
)
class MainWindow(QMainWindow):
    GITHUB_RELEASES_URL = "https://github.com/MeroDuke/Akihabarai-Score/releases"
    TITLE_INPUT_MODE_OFFLINE = "offline"
    TITLE_INPUT_MODE_ONLINE = "online"
    DEFAULT_TITLE_PLACEHOLDER_OFFLINE = "pl. Re:Zero S3"
    DEFAULT_TITLE_PLACEHOLDER_ONLINE = "AniList keresés..."
    DEFAULT_TITLE_SEARCH_DEBOUNCE_MS = 1000
    DEFAULT_TITLE_MAX_LENGTH = 80
    DEFAULT_WINDOW_WIDTH = 1600
    DEFAULT_WINDOW_HEIGHT = 720
    DEFAULT_MINIMUM_WINDOW_WIDTH = 1600
    DEFAULT_MINIMUM_WINDOW_HEIGHT = 720

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)

        config = load_main_window_config(
            load_profiles_config_func=load_profiles_config,
            load_ui_config_func=load_ui_config,
            default_title_placeholder_offline=self.DEFAULT_TITLE_PLACEHOLDER_OFFLINE,
            default_title_placeholder_online=self.DEFAULT_TITLE_PLACEHOLDER_ONLINE,
            default_title_search_debounce_ms=self.DEFAULT_TITLE_SEARCH_DEBOUNCE_MS,
            default_title_max_length=self.DEFAULT_TITLE_MAX_LENGTH,
            default_window_width=self.DEFAULT_WINDOW_WIDTH,
            default_window_height=self.DEFAULT_WINDOW_HEIGHT,
            default_minimum_window_width=self.DEFAULT_MINIMUM_WINDOW_WIDTH,
            default_minimum_window_height=self.DEFAULT_MINIMUM_WINDOW_HEIGHT,
        )
        apply_main_window_config_to_window(self, config)

        if not config.profiles_config_loaded:
            raise RuntimeError(
                config.profiles_error or "Nem sikerült betölteni a profilkonfigurációt"
            )

        initialize_main_window_runtime_state(self, DimState)

        self._build_layout()

        finish_main_window_startup(
            self,
            profiles_error=config.profiles_error,
            ui_error=config.ui_error,
            schedule_update_check=self._schedule_update_check,
            log_info_func=log_info,
            log_warning_func=log_warning,
        )

    def _build_layout(self):
        layout = build_main_window_layout(
            window=self,
            title_placeholder=self.title_placeholder_offline,
            title_max_length=self.title_max_length,
            mix_mode_names=list(MIX_MODES.keys()),
            show_title_mode_button=self.anilist_integration_enabled,
            profile_names=self.profile_names,
            total_weight=TOTAL_WEIGHT,
            states=self.states,
            version_button_text=self._build_version_button_text(),
            on_recompute=self.recompute,
            on_title_search_text_changed=self.on_title_search_text_changed,
            on_toggle_title_input_mode=self.toggle_title_input_mode,
            on_mix_changed=self.on_mix_changed,
            on_profile_changed=self.on_profile_changed,
            on_weight_changed=self.on_weight_changed,
            on_slider_changed=self.on_slider_changed,
            on_spin_changed=self.on_spin_changed,
            on_open_releases_page=self.open_releases_page,
            on_reset_values=self.reset_values,
            on_add_current_to_tier_board=self.add_current_to_tier_board,
            on_update_add_tier_button_state=self.update_add_tier_button_state,
            on_copy_result_image_to_clipboard=self.copy_result_image_to_clipboard,
            on_copy_to_clipboard=self.copy_to_clipboard,
            on_update_tier_buttons_state=self.update_tier_buttons_state,
            on_flip_all_tier_cards=self.flip_all_tier_cards,
            on_clear_all_tier_cards=self.clear_all_tier_cards,
            on_copy_tier_image_to_clipboard=self.copy_tier_image_to_clipboard,
        )

        bind_main_window_layout_widgets(self, layout)
        initialize_main_window_after_layout(self)

    def get_default_window_size(self) -> tuple[int, int]:
        return self.default_window_size

    def get_minimum_window_size(self) -> tuple[int, int]:
        return self.minimum_window_size

    @staticmethod
    def _schedule_update_check(delay_ms: int, callback):
        QTimer.singleShot(delay_ms, callback)

    def toggle_title_input_mode(self):
        toggle_title_input_mode_for_window(
            self,
            log_change=True,
            log_info_func=log_info,
        )

    def _sync_title_mode_ui(self, log_change: bool = False):
        sync_title_input_mode_for_window(
            self,
            log_change=log_change,
            log_info_func=log_info,
        )

    @property
    def pending_title_search_query(self) -> str:
        return get_pending_title_search_query(self)

    @property
    def title_search_timer(self):
        return get_title_search_timer(self)

    def _setup_title_autocomplete(self):
        setup_title_autocomplete_for_window(self)

    def _enable_title_autocomplete(self):
        enable_title_autocomplete_for_window(self)

    def _disable_title_autocomplete(self):
        disable_title_autocomplete_for_window(self)

    def _refresh_title_autocomplete_results(self, query: str = ""):
        refresh_title_autocomplete_results_for_window(self, query)

    def on_title_search_text_changed(self, text: str):
        handle_title_search_text_changed_for_window(self, text)

    def _schedule_online_title_search(self, query: str):
        schedule_online_title_search_for_window(self, query)

    def _run_debounced_title_search(self):
        run_debounced_title_search_for_window(self)

    def _find_anime_result_by_title(self, title: str) -> AnimeSearchResult | None:
        return find_anime_result_by_title_for_window(self, title)

    def on_title_autocomplete_selected(self, title: str):
        handle_title_autocomplete_selected_for_window(self, title)

    def _load_selected_cover_pixmap(self):
        return load_selected_cover_pixmap_for_window(self)

    def _set_selected_title_state(self, selected_anime_result, selected_cover_pixmap):
        set_selected_title_state_for_window(
            self,
            selected_anime_result,
            selected_cover_pixmap,
        )

    def update_add_tier_button_state(self, title: str):
        update_add_tier_button_state_for_window(self, title)

    def _build_version_button_text(self) -> str:
        return build_version_button_text(APP_VERSION)

    def open_releases_page(self):
        open_releases_page_for_window(
            self,
            log_info_func=log_info,
            open_url_func=QDesktopServices.openUrl,
        )

    def check_for_updates(self):
        check_for_updates_for_window(
            self,
            app_version=APP_VERSION,
            default_button_text=self._build_version_button_text(),
            check_for_update_func=check_for_update,
        )

    def update_tier_buttons_state(self):
        update_tier_buttons_state_for_window(self)

    def flip_all_tier_cards(self):
        flip_all_tier_cards_for_window(self, log_info_func=log_info)

    def _ask_clear_all_tier_cards_confirmation(self) -> bool:
        return ask_clear_all_tier_cards_confirmation_for_window(
            self,
            ask_confirmation_func=ask_tier_clear_all_confirmation,
            log_info_func=log_info,
        )

    def clear_all_tier_cards(self):
        clear_all_tier_cards_for_window(self, log_info_func=log_info)

    def _post_init_config_messages(self, err, ui_err):
        post_init_config_messages_for_window(
            self,
            profiles_error=err,
            ui_error=ui_err,
            log_info_func=log_info,
            log_warning_func=log_warning,
        )

    def _apply_initial_weights(self):
        apply_initial_profile_weights_for_window(self, total_weight=TOTAL_WEIGHT)

    def on_mix_changed(self):
        handle_mix_change_for_window(
            self,
            mix_modes=MIX_MODES,
            total_weight=TOTAL_WEIGHT,
        )

    def on_profile_changed(self):
        handle_profile_change_for_window(
            self,
            mix_modes=MIX_MODES,
        )

    def _update_profile_combo_options_internal(self):
        update_profile_combo_options_for_window(
            self,
            mix_modes=MIX_MODES,
        )

    def on_weight_changed(self, changed_idx: int, new_value: int):
        handle_profile_weight_change_for_window(
            self,
            changed_idx=changed_idx,
            new_value=new_value,
            mix_modes=MIX_MODES,
        )

    def on_slider_changed(self, idx: int, v: int):
        handle_dimension_slider_change_for_window(self, index=idx, slider_value=v)

    def on_spin_changed(self, idx: int, v: float):
        handle_dimension_spin_change_for_window(self, index=idx, spin_value=v)

    def reset_values(self):
        log_info("ui", "button_click: reset_values")

        reset_score_inputs_for_window(
            self,
            total_weight=TOTAL_WEIGHT,
        )

    def recompute(self):
        recompute_for_window(
            self,
            mix_modes=MIX_MODES,
            build_result_payload_func=build_result_payload,
        )

    def add_current_to_tier_board(self):
        add_current_result_to_tier_board_for_window(self, log_info_func=log_info)

    def copy_to_clipboard(self):
        copy_details_to_clipboard_for_window(
            self,
            mix_modes=MIX_MODES,
            log_info_func=log_info,
        )

    def copy_result_image_to_clipboard(self):
        copy_result_image_to_clipboard_for_window(self)

    def copy_tier_image_to_clipboard(self):
        copy_tier_image_to_clipboard_for_window(
            self,
            log_info_func=log_info,
        )


def main():
    run_qt_application(window_factory=MainWindow)

if __name__ == "__main__":
    main()
