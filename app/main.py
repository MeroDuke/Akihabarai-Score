import sys
import ctypes
from typing import List, Optional

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSlider, QDoubleSpinBox, QComboBox, QSpinBox
)

from app.core.constants import APP_TITLE, MIX_MODES, TOTAL_WEIGHT
from app.version import APP_VERSION
from app.services.update_check_service import check_for_update
from app.core.models import AnimeSearchResult, DimState
from app.core.runtime import load_app_icon
from app.config.ui_config import load_ui_config
from app.config.profiles_config import load_profiles_config
from app.logger import init_logger, log_debug, log_info, log_warning
from app.services.scoring_pipeline import build_result_payload
from app.services.profile_mix_service import (
    default_profile_selection_memory,
)
from app.services.main_window_config_service import load_main_window_config
from app.services.main_window_layout_service import build_main_window_layout
from app.services.cover_image_service import load_selected_cover_preview_pixmap
from app.services.dimension_input_workflow_service import (
    apply_dimension_slider_change,
    apply_dimension_spin_change,
)
from app.services.tier_add_workflow_service import add_current_result_to_tier_board
from app.services.details_copy_service import copy_details_with_feedback
from app.services.tier_image_copy_service import copy_tier_image_with_feedback
from app.services.tier_flip_service import flip_all_tier_cards_if_available
from app.services.tier_clear_service import clear_all_tier_cards_if_confirmed
from app.services.result_image_copy_service import copy_result_image_with_feedback
from app.services.profile_weight_reset_service import (
    apply_initial_profile_weights,
)
from app.services.version_update_workflow_service import (
    apply_update_check_to_version_button,
)
from app.services.release_page_service import open_release_page
from app.services.result_recompute_service import recompute_result_and_update_views
from app.services.reset_workflow_service import reset_score_inputs_to_initial_state
from app.services.profile_mix_workflow_service import (
    apply_mix_mode_change_workflow,
    apply_profile_selection_change_workflow,
    apply_profile_weight_change_workflow,
    remember_active_profile_selections,
    restore_profile_combo_selection,
    update_profile_combo_options,
)
from app.services.title_search_workflow_service import (
    disable_title_autocomplete,
    enable_title_autocomplete,
    get_next_title_input_mode,
    handle_title_autocomplete_selected,
    handle_title_search_text_changed,
    refresh_title_autocomplete_results,
    setup_title_autocomplete,
    sync_title_input_mode_ui,
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
from app.controllers.anilist_title_search_controller import (
    AniListTitleSearchController,
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
        self.dimensions = config.dimensions
        self.profiles = config.profiles
        self.tier_thresholds = config.tier_thresholds
        self.ui_cfg = config.ui_cfg
        self.anilist_integration_enabled = config.anilist_integration_enabled
        self.title_placeholder_offline = config.title_placeholder_offline
        self.title_placeholder_online = config.title_placeholder_online
        self.title_search_debounce_ms = config.title_search_debounce_ms
        self.title_max_length = config.title_max_length
        self.default_window_size = config.default_window_size
        self.minimum_window_size = config.minimum_window_size
        self.title_input_mode = self.TITLE_INPUT_MODE_OFFLINE
        self.selected_anime_result: AnimeSearchResult | None = None
        self.selected_cover_pixmap = None
        self.title_search_controller: AniListTitleSearchController | None = None

        if not config.profiles_config_loaded:
            raise RuntimeError(
                config.profiles_error or "Nem sikerült betölteni a profilkonfigurációt"
            )

        self.states: List[DimState] = [DimState(n) for n in self.dimensions]
        self._building = True

        self.profile_combos: List[QComboBox] = []
        self.weight_spins: List[QSpinBox] = []
        self.slider_widgets: List[QSlider] = []
        self.spin_widgets: List[QDoubleSpinBox] = []
        self.profile_names: List[str] = list(self.profiles.keys()) or ["(nincs profil betöltve)"]
        self.profile_selection_memory: List[Optional[str]] = self._default_profile_selection_memory()
        self.current_mix_needed = 1

        self._build_layout()

        self._building = False
        self._post_init_config_messages(config.profiles_error, config.ui_error)
        self._apply_initial_weights()
        self.on_mix_changed()
        QTimer.singleShot(250, self.check_for_updates)

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

        self.main_layout = layout.main_layout
        self.left_box = layout.left_box
        self.left_layout = layout.left_layout
        self.top_inputs_panel = layout.top_inputs_panel
        self.profile_mix_panel = layout.profile_mix_panel
        self.dimensions_panel = layout.dimensions_panel
        self.action_buttons_panel = layout.action_buttons_panel
        self.result_panel = layout.result_panel
        self.right_box = layout.right_box
        self.tier_panel = layout.tier_panel
        self.tier_box = layout.tier_box

        self.title_edit = self.top_inputs_panel.title_edit
        self.title_mode_btn = self.top_inputs_panel.title_mode_btn
        self.mix_combo = self.top_inputs_panel.mix_combo
        self.profile_combos = self.profile_mix_panel.profile_combos
        self.weight_spins = self.profile_mix_panel.weight_spins
        self.slider_widgets = self.dimensions_panel.slider_widgets
        self.spin_widgets = self.dimensions_panel.spin_widgets
        self.version_btn = self.action_buttons_panel.version_btn
        self.reset_btn = self.action_buttons_panel.reset_btn
        self.add_tier_btn = self.action_buttons_panel.add_tier_btn
        self.score_label = self.result_panel.score_label
        self.tier_label = self.result_panel.tier_label
        self.summary_label = self.result_panel.summary_label
        self.result_card = self.result_panel.result_card
        self.copy_img_btn = self.result_panel.copy_img_btn
        self.table = self.result_panel.table
        self.copy_btn = self.result_panel.copy_btn
        self.tier_board = self.tier_panel.tier_board
        self.tier_scroll_area = self.tier_panel.tier_scroll_area
        self.flip_all_tier_cards_btn = self.tier_panel.flip_all_tier_cards_btn
        self.clear_all_tier_cards_btn = self.tier_panel.clear_all_tier_cards_btn
        self.copy_tier_btn = self.tier_panel.copy_tier_btn

        self._setup_title_autocomplete()
        self._sync_title_mode_ui(log_change=False)
        self.update_add_tier_button_state(self.title_edit.text())

    def get_default_window_size(self) -> tuple[int, int]:
        return self.default_window_size

    def get_minimum_window_size(self) -> tuple[int, int]:
        return self.minimum_window_size

    def _get_window_size(self) -> tuple[int, int]:
        return self.get_default_window_size()

    def _get_minimum_window_size(self) -> tuple[int, int]:
        return self.get_minimum_window_size()

    def toggle_title_input_mode(self):
        self.title_input_mode = get_next_title_input_mode(
            integration_enabled=self.anilist_integration_enabled,
            current_mode=self.title_input_mode,
            offline_mode=self.TITLE_INPUT_MODE_OFFLINE,
            online_mode=self.TITLE_INPUT_MODE_ONLINE,
        )

        self._sync_title_mode_ui(log_change=True)

    def _sync_title_mode_ui(self, log_change: bool = False):
        self.title_input_mode = sync_title_input_mode_ui(
            title_input_mode=self.title_input_mode,
            title_placeholder_offline=self.title_placeholder_offline,
            title_placeholder_online=self.title_placeholder_online,
            title_edit=self.title_edit,
            title_mode_btn=self.title_mode_btn,
            integration_enabled=self.anilist_integration_enabled,
            controller=self.title_search_controller,
            completer=getattr(self, "title_completer", None),
        )

        if log_change:
            log_info("ui", f"title_input_mode_changed: mode='{self.title_input_mode}'")

    @property
    def pending_title_search_query(self) -> str:
        if getattr(self, "title_search_controller", None) is None:
            return ""

        return self.title_search_controller.pending_title_search_query

    @property
    def title_search_timer(self):
        if getattr(self, "title_search_controller", None) is None:
            return None

        return self.title_search_controller.title_search_timer

    def _setup_title_autocomplete(self):
        setup = setup_title_autocomplete(
            parent=self,
            title_edit=self.title_edit,
            debounce_ms=self.title_search_debounce_ms,
            is_online_mode=lambda: self.title_input_mode == self.TITLE_INPUT_MODE_ONLINE,
            is_integration_enabled=lambda: self.anilist_integration_enabled,
            on_title_selected=self.on_title_autocomplete_selected,
        )
        self.title_completer_model = setup.completer_model
        self.title_completer = setup.completer
        self.title_search_controller = setup.controller

    def _enable_title_autocomplete(self):
        enable_title_autocomplete(
            title_edit=self.title_edit,
            controller=self.title_search_controller,
            completer=getattr(self, "title_completer", None),
        )

    def _disable_title_autocomplete(self):
        disable_title_autocomplete(
            title_edit=self.title_edit,
            controller=self.title_search_controller,
        )

    def _refresh_title_autocomplete_results(self, query: str = ""):
        refresh_title_autocomplete_results(
            controller=getattr(self, "title_search_controller", None),
            query=query,
        )

    def on_title_search_text_changed(self, text: str):
        title_selection_state = handle_title_search_text_changed(
            text=text,
            selected_anime_result=self.selected_anime_result,
            selected_cover_pixmap=self.selected_cover_pixmap,
            controller=getattr(self, "title_search_controller", None),
        )
        self.selected_anime_result = title_selection_state.selected_anime_result
        self.selected_cover_pixmap = title_selection_state.selected_cover_pixmap

    def _schedule_online_title_search(self, query: str):
        if getattr(self, "title_search_controller", None) is None:
            return

        self.title_search_controller.schedule_online_title_search(query)

    def _run_debounced_title_search(self):
        if getattr(self, "title_search_controller", None) is None:
            return

        self.title_search_controller.run_debounced_title_search()

    def _find_anime_result_by_title(self, title: str) -> AnimeSearchResult | None:
        if getattr(self, "title_search_controller", None) is None:
            return None

        return self.title_search_controller.find_anime_result_by_title(title)

    def on_title_autocomplete_selected(self, title: str):
        selection_state = handle_title_autocomplete_selected(
            title=title,
            title_edit=self.title_edit,
            controller=getattr(self, "title_search_controller", None),
            recompute=self.recompute,
            apply_selection=self._set_selected_title_state,
        )
        self.selected_anime_result = selection_state.selected_anime_result
        self.selected_cover_pixmap = selection_state.selected_cover_pixmap

    def _load_selected_cover_pixmap(self):
        return load_selected_cover_preview_pixmap(self.selected_anime_result)

    def _set_selected_title_state(self, selected_anime_result, selected_cover_pixmap):
        self.selected_anime_result = selected_anime_result
        self.selected_cover_pixmap = selected_cover_pixmap

    def update_add_tier_button_state(self, title: str):
        self.add_tier_btn.setEnabled(bool(title.strip()))

    def _build_version_button_text(self) -> str:
        return build_version_button_text(APP_VERSION)

    def open_releases_page(self):
        log_info("ui", "button_click: open_releases_page")
        open_release_page(
            self.GITHUB_RELEASES_URL,
            QDesktopServices.openUrl,
        )

    def check_for_updates(self):
        apply_update_check_to_version_button(
            version_btn=self.version_btn,
            app_version=APP_VERSION,
            default_button_text=self._build_version_button_text(),
            check_for_update_func=check_for_update,
        )

    def update_tier_buttons_state(self):
        self.tier_panel.update_buttons_state()

    def flip_all_tier_cards(self):
        log_info("ui", "button_click: flip_all_tier_cards")

        flip_all_tier_cards_if_available(
            self.tier_board,
            self.update_tier_buttons_state,
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

        clear_all_tier_cards_if_confirmed(
            self.tier_board,
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
        self._building = True
        apply_initial_profile_weights(self.weight_spins, TOTAL_WEIGHT)
        self._building = False

    def _default_profile_selection_memory(self) -> List[Optional[str]]:
        return default_profile_selection_memory(list(self.profiles.keys()))

    def _remember_active_profile_selections(self, needed: int | None = None):
        self.profile_selection_memory = remember_active_profile_selections(
            profile_combos=self.profile_combos,
            profiles=self.profiles,
            selection_memory=self.profile_selection_memory,
            mix_mode=self.mix_combo.currentText(),
            mix_modes=MIX_MODES,
            needed=needed,
        )

    def _restore_profile_combo_selection(self, combo: QComboBox, index: int):
        restore_profile_combo_selection(
            combo=combo,
            index=index,
            selection_memory=self.profile_selection_memory,
            profiles=self.profiles,
        )

    def on_mix_changed(self):
        state = apply_mix_mode_change_workflow(
            profile_combos=self.profile_combos,
            weight_spins=self.weight_spins,
            profiles=self.profiles,
            selection_memory=self.profile_selection_memory,
            current_mix_needed=getattr(self, "current_mix_needed", 1),
            mix_mode=self.mix_combo.currentText(),
            mix_modes=MIX_MODES,
            total_weight=TOTAL_WEIGHT,
            set_building=lambda value: setattr(self, "_building", value),
        )
        self.profile_selection_memory = state.selection_memory
        self.current_mix_needed = state.current_mix_needed

        self.recompute()

    def on_profile_changed(self):
        if self._building:
            return

        state = apply_profile_selection_change_workflow(
            profile_combos=self.profile_combos,
            weight_spins=self.weight_spins,
            profiles=self.profiles,
            selection_memory=self.profile_selection_memory,
            mix_mode=self.mix_combo.currentText(),
            mix_modes=MIX_MODES,
            set_building=lambda value: setattr(self, "_building", value),
        )
        self.profile_selection_memory = state.selection_memory

        self.recompute()

    def _update_profile_combo_options_internal(self):
        update_profile_combo_options(
            profile_combos=self.profile_combos,
            profiles=self.profiles,
            mix_mode=self.mix_combo.currentText(),
            mix_modes=MIX_MODES,
        )

    def on_weight_changed(self, changed_idx: int, new_value: int):
        if self._building:
            return

        handled = apply_profile_weight_change_workflow(
            weight_spins=self.weight_spins,
            changed_idx=changed_idx,
            new_value=new_value,
            mix_mode=self.mix_combo.currentText(),
            mix_modes=MIX_MODES,
            set_building=lambda value: setattr(self, "_building", value),
        )

        if not handled:
            return

        self.recompute()

    def on_slider_changed(self, idx: int, v: int):
        handled = apply_dimension_slider_change(
            is_building=self._building,
            set_building=lambda value: setattr(self, "_building", value),
            state=self.states[idx],
            spin_widget=self.spin_widgets[idx],
            slider_value=v,
        )
        if not handled:
            return

        self.recompute()

    def on_spin_changed(self, idx: int, v: float):
        handled = apply_dimension_spin_change(
            is_building=self._building,
            set_building=lambda value: setattr(self, "_building", value),
            state=self.states[idx],
            slider_widget=self.slider_widgets[idx],
            spin_value=v,
        )
        if not handled:
            return

        self.recompute()

    def reset_values(self):
        log_info("ui", "button_click: reset_values")

        reset_state = reset_score_inputs_to_initial_state(
            set_building=lambda value: setattr(self, "_building", value),
            title_edit=self.title_edit,
            title_search_controller=self.title_search_controller,
            mix_combo=self.mix_combo,
            states=self.states,
            slider_widgets=self.slider_widgets,
            spin_widgets=self.spin_widgets,
            profile_combos=self.profile_combos,
            weight_spins=self.weight_spins,
            profile_names=list(self.profiles.keys()),
            total_weight=TOTAL_WEIGHT,
            update_profile_combo_options=self._update_profile_combo_options_internal,
        )
        self.selected_anime_result = reset_state.selected_anime_result
        self.selected_cover_pixmap = reset_state.selected_cover_pixmap
        self.profile_selection_memory = reset_state.profile_selection_memory
        self.current_mix_needed = reset_state.current_mix_needed

        self.on_mix_changed()

    def recompute(self):
        self.latest_result = recompute_result_and_update_views(
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

        add_current_result_to_tier_board(
            parent=self,
            tier_board=self.tier_board,
            title=self.title_edit.text(),
            latest_result=getattr(self, "latest_result", None),
            recompute=self.recompute,
            get_latest_result=lambda: getattr(self, "latest_result", None),
            cover_pixmap=self.selected_cover_pixmap,
        )

    def update_table(self, rel: List[float], contrib: List[float]):
        self.result_panel.update_table(self.states, rel, contrib)

    def copy_to_clipboard(self):
        log_info("ui", "button_click: copy_to_clipboard")

        copy_details_with_feedback(
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
        copy_result_image_with_feedback(
            self.result_card,
            self.copy_img_btn,
        )

    def copy_tier_image_to_clipboard(self):
        log_info("ui", "button_click: copy_tier_image_to_clipboard")

        copy_tier_image_with_feedback(
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
