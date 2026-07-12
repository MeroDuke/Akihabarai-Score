import sys
import ctypes
from typing import List, Optional

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox

from app.core.constants import APP_TITLE, MIX_MODES, TOTAL_WEIGHT
from app.version import APP_VERSION
from app.services.update_check_service import check_for_update
from app.core.models import AnimeSearchResult, DimState
from app.core.runtime import load_app_icon
from app.config.ui_config import load_ui_config
from app.config.profiles_config import load_profiles_config
from app.logger import init_logger, log_debug, log_info, log_warning
from app.services.scoring_pipeline import build_result_payload
from app.services.main_window_config_service import load_main_window_config
from app.services.main_window_layout_service import build_main_window_layout
from app.services.main_window_lifecycle_service import (
    apply_main_window_config_to_window,
    bind_main_window_layout_widgets,
    finish_main_window_startup,
    initialize_main_window_after_layout,
    initialize_main_window_runtime_state,
)
from app.services.main_window_input_workflow_service import (
    apply_initial_profile_weights_for_window,
    build_default_profile_selection_memory_for_window,
    handle_dimension_slider_change_for_window,
    handle_dimension_spin_change_for_window,
    handle_mix_change_for_window,
    handle_profile_change_for_window,
    handle_profile_weight_change_for_window,
    remember_active_profile_selections_for_window,
    reset_score_inputs_for_window,
    restore_profile_combo_selection_for_window,
    update_profile_combo_options_for_window,
)
from app.services.main_window_actions_service import (
    check_for_updates_from_button,
    clear_tier_cards_from_button,
    copy_details_from_button,
    copy_result_image_from_button,
    copy_tier_image_from_button,
    flip_tier_cards_from_button,
    open_releases_page_from_button,
    set_add_tier_button_enabled,
    update_result_table_from_main,
    update_tier_panel_buttons,
)
from app.services.main_window_score_workflow_service import (
    add_current_result_from_window,
    recompute_from_window,
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
from app.widgets.result_panel_widget import ResultPanelWidget
from app.widgets.tier_clear_confirmation_dialog import ask_tier_clear_all_confirmation
from app.widgets.version_button_presenter import (
    build_version_button_text,
)
from app.widgets.config_messages import (
    show_profiles_config_error,
    show_ui_config_error,
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

    def _get_window_size(self) -> tuple[int, int]:
        return self.get_default_window_size()

    def _get_minimum_window_size(self) -> tuple[int, int]:
        return self.get_minimum_window_size()

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
        set_add_tier_button_enabled(self.add_tier_btn, title)

    def _build_version_button_text(self) -> str:
        return build_version_button_text(APP_VERSION)

    def open_releases_page(self):
        log_info("ui", "button_click: open_releases_page")
        open_releases_page_from_button(
            releases_url=self.GITHUB_RELEASES_URL,
            open_url_func=QDesktopServices.openUrl,
        )

    def check_for_updates(self):
        check_for_updates_from_button(
            version_btn=self.version_btn,
            app_version=APP_VERSION,
            default_button_text=self._build_version_button_text(),
            check_for_update_func=check_for_update,
        )

    def update_tier_buttons_state(self):
        update_tier_panel_buttons(self.tier_panel)

    def flip_all_tier_cards(self):
        log_info("ui", "button_click: flip_all_tier_cards")

        flip_tier_cards_from_button(
            tier_board=self.tier_board,
            update_tier_buttons_state=self.update_tier_buttons_state,
        )

    def _ask_clear_all_tier_cards_confirmation(self) -> bool:
        confirmed = ask_tier_clear_all_confirmation(self)

        log_info(
            "tier_board",
            f"clear_all_entries_confirmation: decision='{'yes' if confirmed else 'no'}'",
        )

        return confirmed

    def clear_all_tier_cards(self):
        log_info("ui", "button_click: clear_all_tier_cards")

        clear_tier_cards_from_button(
            tier_board=self.tier_board,
            ask_confirmation=self._ask_clear_all_tier_cards_confirmation,
            update_tier_buttons_state=self.update_tier_buttons_state,
        )

    def _apply_summary_theme_style(self):
        self.result_panel.apply_summary_theme_style()

    @staticmethod
    def _sanitize_summary_html(html: str) -> str:
        return ResultPanelWidget.sanitize_summary_html(html)

    @staticmethod
    def _strip_color_from_style_attr(style_value: str) -> str:
        return ResultPanelWidget.strip_color_from_style_attr(style_value)

    def _post_init_config_messages(self, err, ui_err):
        log_info(
            "config",
            f"Loaded profiles: dims={len(self.dimensions)}, profiles={len(self.profiles)}",
        )
        if err:
            log_warning("config", f"profiles.json issue: {err}")

        log_info("config", "Loaded UI config")
        if ui_err:
            log_warning("config", f"ui.json issue: {ui_err}")

        if err:
            show_profiles_config_error(self, err)

        if ui_err:
            show_ui_config_error(self, ui_err)

    def _apply_initial_weights(self):
        apply_initial_profile_weights_for_window(self, total_weight=TOTAL_WEIGHT)

    def _default_profile_selection_memory(self) -> List[Optional[str]]:
        return build_default_profile_selection_memory_for_window(self)

    def _remember_active_profile_selections(self, needed: int | None = None):
        remember_active_profile_selections_for_window(
            self,
            mix_modes=MIX_MODES,
            needed=needed,
        )

    def _restore_profile_combo_selection(self, combo: QComboBox, index: int):
        restore_profile_combo_selection_for_window(self, combo, index)

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
        self.latest_result = recompute_from_window(
            profiles=self.profiles,
            profile_combos=self.profile_combos,
            weight_spins=self.weight_spins,
            mix_mode=self.mix_combo.currentText(),
            mix_modes=MIX_MODES,
            states=self.states,
            tier_thresholds=self.tier_thresholds,
            ui_cfg=self.ui_cfg,
            title=self.title_edit.text(),
            result_panel=self.result_panel,
            tier_board=self.tier_board,
            cover_pixmap=self.selected_cover_pixmap,
            build_result_payload_func=build_result_payload,
        )

    def add_current_to_tier_board(self):
        log_info("ui", "button_click: add_current_to_tier_board")

        add_current_result_from_window(
            parent=self,
            tier_board=self.tier_board,
            title=self.title_edit.text(),
            latest_result=getattr(self, "latest_result", None),
            recompute=self.recompute,
            get_latest_result=lambda: getattr(self, "latest_result", None),
            cover_pixmap=self.selected_cover_pixmap,
        )

    def update_table(self, rel: List[float], contrib: List[float]):
        update_result_table_from_main(
            result_panel=self.result_panel,
            states=self.states,
            relevances=rel,
            contributions=contrib,
        )

    def copy_to_clipboard(self):
        log_info("ui", "button_click: copy_to_clipboard")

        copy_details_from_button(
            profiles=self.profiles,
            profile_combos=self.profile_combos,
            weight_spins=self.weight_spins,
            mix_mode=self.mix_combo.currentText(),
            mix_modes=MIX_MODES,
            states=self.states,
            tier_thresholds=self.tier_thresholds,
            title=self.title_edit.text(),
            copy_btn=self.copy_btn,
        )

    def copy_result_image_to_clipboard(self):
        copy_result_image_from_button(
            result_card=self.result_card,
            copy_img_btn=self.copy_img_btn,
        )

    def copy_tier_image_to_clipboard(self):
        log_info("ui", "button_click: copy_tier_image_to_clipboard")

        copy_tier_image_from_button(
            parent=self,
            tier_board=self.tier_board,
            copy_tier_btn=self.copy_tier_btn,
            update_tier_buttons_state=self.update_tier_buttons_state,
        )


def main():
    init_logger()
    log_info("app", "Starting AkihabaraiScore")

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "akihabarai_konyvespolc.score"
    )

    app = QApplication(sys.argv)

    icon = load_app_icon()
    if icon is not None:
        app.setWindowIcon(icon)

    w = MainWindow()
    if icon is not None:
        w.setWindowIcon(icon)

    window_width, window_height = w.get_default_window_size()
    minimum_width, minimum_height = w.get_minimum_window_size()
    w.resize(window_width, window_height)
    w.setMinimumSize(minimum_width, minimum_height)
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
