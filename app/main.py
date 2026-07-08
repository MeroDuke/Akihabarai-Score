import sys
import ctypes
from typing import List, Optional

from PyQt6.QtCore import Qt, QTimer, QEvent, QStringListModel, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QSlider, QDoubleSpinBox,
    QGroupBox, QComboBox,
    QSpinBox, QCompleter
)

from app.core.constants import APP_TITLE, MIX_MODES, TOTAL_WEIGHT
from app.version import APP_VERSION
from app.services.update_check_service import check_for_update
from app.core.models import AnimeSearchResult, DimState
from app.core.runtime import load_app_icon
from app.config.ui_config import load_ui_config
from app.config.ui_settings import (
    get_anilist_int_setting,
    get_anilist_text_setting,
    get_config_section,
    get_positive_int_setting,
    get_window_size,
    is_anilist_integration_enabled,
)
from app.config.profiles_config import load_profiles_config
from app.logger import init_logger, log_debug, log_info, log_warning, log_error
from app.services.scoring_pipeline import build_result_payload
from app.services.profile_mix_service import (
    build_profile_combo_options,
    default_profile_selection_memory,
    get_selected_profiles_and_ratios,
    force_total_weight,
    remember_profile_selections,
)
from app.services.cover_image_service import load_cover_pixmap_from_url
from app.services.dimension_controls_service import (
    apply_slider_value,
    apply_spin_value,
    reset_dimension_controls,
)
from app.services.tier_add_service import (
    TierAddStatus,
    add_result_to_tier_board,
)
from app.services.details_export_service import copy_details_to_clipboard
from app.services.tier_image_export_service import (
    TierImageExportStatus,
    copy_tier_board_image_to_clipboard,
)
from app.services.result_image_export_service import copy_result_card_image_to_clipboard
from app.services.reset_controls_service import (
    reset_combo_to_first_item,
)
from app.services.profile_weight_reset_service import (
    apply_initial_profile_weights,
    reset_profile_inputs_to_initial_state,
)
from app.widgets.action_buttons_panel_widget import ActionButtonsPanelWidget
from app.widgets.dimensions_panel_widget import DimensionsPanelWidget
from app.widgets.profile_mix_panel_widget import ProfileMixPanelWidget
from app.widgets.result_panel_widget import ResultPanelWidget
from app.widgets.tier_panel_widget import TierPanelWidget
from app.widgets.top_inputs_panel_widget import TopInputsPanelWidget
from app.widgets.tier_clear_confirmation_dialog import ask_tier_clear_all_confirmation
from app.widgets.version_button_presenter import (
    build_update_check_version_button_presentation,
    build_version_button_text,
)
from app.widgets.copy_button_feedback import (
    COPY_DETAILS_DEFAULT_TEXT,
    COPY_DETAILS_SUCCESS_TEXT,
    COPY_RESULT_IMAGE_DEFAULT_TEXT,
    COPY_SUCCESS_TEXT,
    COPY_TIER_IMAGE_DEFAULT_TEXT,
    show_temporary_copy_feedback,
)
from app.widgets.tier_messages import (
    show_duplicate_tier_title_information,
    show_missing_tier_title_warning,
    show_tier_image_copy_error,
)
from app.widgets.config_messages import (
    show_profiles_config_error,
    show_ui_config_error,
)
from app.widgets.title_input_mode_presenter import (
    build_title_input_mode_presentation,
)
from app.widgets.tier_preview_presenter import build_tier_preview_title
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

        self.dimensions, self.profiles, self.tier_thresholds, err = load_profiles_config()
        self.ui_cfg, ui_err = load_ui_config()
        self.anilist_integration_enabled = self._is_anilist_integration_enabled()
        self.title_placeholder_offline = self._get_anilist_text_setting(
            "title_placeholder_offline",
            self.DEFAULT_TITLE_PLACEHOLDER_OFFLINE,
        )
        self.title_placeholder_online = self._get_anilist_text_setting(
            "title_placeholder_online",
            self.DEFAULT_TITLE_PLACEHOLDER_ONLINE,
        )
        self.title_search_debounce_ms = self._get_anilist_int_setting(
            "title_search_debounce_ms",
            self.DEFAULT_TITLE_SEARCH_DEBOUNCE_MS,
        )
        self.title_max_length = self._get_anilist_int_setting(
            "title_max_length",
            self.DEFAULT_TITLE_MAX_LENGTH,
        )
        self.title_input_mode = self.TITLE_INPUT_MODE_OFFLINE
        self.selected_anime_result: AnimeSearchResult | None = None
        self.selected_cover_pixmap = None
        self.title_search_controller: AniListTitleSearchController | None = None

        if self.dimensions is None or self.profiles is None or self.tier_thresholds is None:
            raise RuntimeError(err or "Nem sikerült betölteni a profilkonfigurációt")

        self.states: List[DimState] = [DimState(n) for n in self.dimensions]
        self._building = True

        self.profile_combos: List[QComboBox] = []
        self.weight_spins: List[QSpinBox] = []
        self.slider_widgets: List[QSlider] = []
        self.spin_widgets: List[QDoubleSpinBox] = []
        self.profile_names: List[str] = list(self.profiles.keys()) or ["(nincs profil betöltve)"]
        self.profile_selection_memory: List[Optional[str]] = self._default_profile_selection_memory()
        self.current_mix_needed = 1

        self._build_root_layout()
        self._build_left_panel()
        self._build_right_panel()
        self._build_tier_panel()
        self._finalize_layout()

        self._building = False
        self._post_init_config_messages(err, ui_err)
        self._apply_initial_weights()
        self.on_mix_changed()
        QTimer.singleShot(250, self.check_for_updates)

    def _build_root_layout(self):
        root = QWidget()
        self.setCentralWidget(root)

        self.main_layout = QHBoxLayout(root)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(16)

    def _build_left_panel(self):
        self.left_box = QGroupBox("Bevitel")
        self.left_layout = QVBoxLayout(self.left_box)
        self.left_layout.setSpacing(10)

        self._build_top_inputs()
        self._build_profiles_group()
        self._build_dimensions_group()
        self._build_action_buttons()

    def _build_top_inputs(self):
        self.top_inputs_panel = TopInputsPanelWidget(
            title_placeholder=self.title_placeholder_offline,
            title_max_length=self.title_max_length,
            mix_mode_names=list(MIX_MODES.keys()),
            show_title_mode_button=self.anilist_integration_enabled,
        )
        self.title_edit = self.top_inputs_panel.title_edit
        self.title_mode_btn = self.top_inputs_panel.title_mode_btn
        self.mix_combo = self.top_inputs_panel.mix_combo

        self.title_edit.textChanged.connect(self.recompute)
        self.title_edit.textEdited.connect(self.on_title_search_text_changed)
        self._setup_title_autocomplete()

        self.title_mode_btn.clicked.connect(self.toggle_title_input_mode)
        self._sync_title_mode_ui(log_change=False)

        self.mix_combo.currentIndexChanged.connect(self.on_mix_changed)

        self.left_layout.addWidget(self.top_inputs_panel)

    def _get_window_config(self) -> dict:
        return get_config_section(self.ui_cfg, "window")

    def _get_window_int_setting(self, key: str, default: int) -> int:
        return get_positive_int_setting(self._get_window_config(), key, default)

    def get_default_window_size(self) -> tuple[int, int]:
        return get_window_size(
            self.ui_cfg,
            width_key="default_width",
            height_key="default_height",
            default_width=self.DEFAULT_WINDOW_WIDTH,
            default_height=self.DEFAULT_WINDOW_HEIGHT,
        )

    def get_minimum_window_size(self) -> tuple[int, int]:
        return get_window_size(
            self.ui_cfg,
            width_key="minimum_width",
            height_key="minimum_height",
            default_width=self.DEFAULT_MINIMUM_WINDOW_WIDTH,
            default_height=self.DEFAULT_MINIMUM_WINDOW_HEIGHT,
        )

    def _get_window_size(self) -> tuple[int, int]:
        return self.get_default_window_size()

    def _get_minimum_window_size(self) -> tuple[int, int]:
        return self.get_minimum_window_size()

    def _is_anilist_integration_enabled(self) -> bool:
        return is_anilist_integration_enabled(self.ui_cfg)

    def _get_anilist_config(self) -> dict:
        return get_config_section(self.ui_cfg, "anilist")

    def _get_anilist_text_setting(self, key: str, default: str) -> str:
        return get_anilist_text_setting(self.ui_cfg, key, default)

    def _get_anilist_int_setting(self, key: str, default: int) -> int:
        return get_anilist_int_setting(self.ui_cfg, key, default)

    def toggle_title_input_mode(self):
        if not self.anilist_integration_enabled:
            return

        if self.title_input_mode == self.TITLE_INPUT_MODE_OFFLINE:
            self.title_input_mode = self.TITLE_INPUT_MODE_ONLINE
        else:
            self.title_input_mode = self.TITLE_INPUT_MODE_OFFLINE

        self._sync_title_mode_ui(log_change=True)

    def _sync_title_mode_ui(self, log_change: bool = False):
        presentation = build_title_input_mode_presentation(
            self.title_input_mode,
            self.title_placeholder_offline,
            self.title_placeholder_online,
        )

        self.title_input_mode = presentation.mode
        self.title_edit.setPlaceholderText(presentation.placeholder)
        self.title_mode_btn.setText(presentation.button_text)

        if presentation.autocomplete_enabled:
            self._enable_title_autocomplete()
        else:
            self._disable_title_autocomplete()

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
        self.title_completer_model = QStringListModel([], self)
        self.title_completer = QCompleter(self.title_completer_model, self)
        self.title_completer.setCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )
        self.title_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.title_completer.activated[str].connect(
            self.on_title_autocomplete_selected
        )

        self.title_search_controller = AniListTitleSearchController(
            parent=self,
            completer_model=self.title_completer_model,
            completer=self.title_completer,
            debounce_ms=self.title_search_debounce_ms,
            is_online_mode=lambda: self.title_input_mode == self.TITLE_INPUT_MODE_ONLINE,
            is_integration_enabled=lambda: self.anilist_integration_enabled,
        )
        self._refresh_title_autocomplete_results()
        self._disable_title_autocomplete()

    def _enable_title_autocomplete(self):
        if not self.anilist_integration_enabled:
            self._disable_title_autocomplete()
            return

        self._refresh_title_autocomplete_results(self.title_edit.text())

        # Rebind the completer explicitly. After the controller refactor, Qt can
        # keep a stale completer binding when switching modes, which prevents the
        # online popup from opening even though the model is refreshed correctly.
        self.title_edit.setCompleter(None)
        self.title_edit.setCompleter(self.title_completer)

    def _disable_title_autocomplete(self):
        if self.title_search_controller is not None:
            self.title_search_controller.title_search_timer.stop()
        self.title_edit.setCompleter(None)

    def _refresh_title_autocomplete_results(self, query: str = ""):
        if getattr(self, "title_search_controller", None) is None:
            return

        self.title_search_controller.refresh_title_autocomplete_results(query)

    def on_title_search_text_changed(self, text: str):
        if (
            self.selected_anime_result is not None
            and text != self.selected_anime_result.title_romaji
        ):
            self.selected_anime_result = None
            self.selected_cover_pixmap = None

        if getattr(self, "title_search_controller", None) is None:
            return

        self.title_search_controller.handle_title_text_edited(text)

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
        self.selected_anime_result = self._find_anime_result_by_title(title)
        self.selected_cover_pixmap = self._load_selected_cover_pixmap()
        self.title_edit.setText(title)

        # setText() does not always trigger a visible preview refresh when the
        # selected title text is already present in the input. Force a recompute
        # after the selected runtime cover pixmap has been updated so the Tier
        # preview immediately uses the newly selected AniList cover.
        self.recompute()

        if self.title_search_controller is not None:
            self.title_search_controller.handle_title_selected(title)

        if self.selected_anime_result is None:
            log_info("ui", f"title_autocomplete_selected: title='{title}' anilist_id=None")
            return

        log_info(
            "ui",
            "title_autocomplete_selected: "
            f"title='{title}' anilist_id={self.selected_anime_result.anilist_id}",
        )

    def _load_selected_cover_pixmap(self):
        if self.selected_anime_result is None:
            return None

        if not self.selected_anime_result.cover_url:
            log_debug(
                "cover_image",
                "cover_preview_skipped: reason='missing_cover_url' "
                f"title='{self.selected_anime_result.title_romaji}'",
            )
            return None

        response = load_cover_pixmap_from_url(self.selected_anime_result.cover_url)
        if response.ok:
            log_debug(
                "cover_image",
                "cover_preview_loaded: "
                f"title='{self.selected_anime_result.title_romaji}' "
                f"anilist_id={self.selected_anime_result.anilist_id}",
            )
            return response.pixmap

        log_warning(
            "cover_image",
            "cover_preview_fallback_to_text: "
            f"title='{self.selected_anime_result.title_romaji}' "
            f"reason='{response.error}' detail='{response.error_detail}'",
        )
        return None

    def _build_profiles_group(self):
        self.profile_mix_panel = ProfileMixPanelWidget(
            self.profile_names,
            TOTAL_WEIGHT,
        )
        self.profile_combos = self.profile_mix_panel.profile_combos
        self.weight_spins = self.profile_mix_panel.weight_spins

        for combo in self.profile_combos:
            combo.currentIndexChanged.connect(self.on_profile_changed)

        for index, weight_spin in enumerate(self.weight_spins):
            weight_spin.valueChanged.connect(
                lambda value, idx=index: self.on_weight_changed(idx, value)
            )

        self.left_layout.addWidget(self.profile_mix_panel)

    def _build_dimensions_group(self):
        self.dimensions_panel = DimensionsPanelWidget(self.states)
        self.slider_widgets = self.dimensions_panel.slider_widgets
        self.spin_widgets = self.dimensions_panel.spin_widgets

        for index, slider in enumerate(self.slider_widgets):
            slider.valueChanged.connect(
                lambda value, idx=index: self.on_slider_changed(idx, value)
            )

        for index, spin in enumerate(self.spin_widgets):
            spin.valueChanged.connect(
                lambda value, idx=index: self.on_spin_changed(idx, value)
            )

        self.left_layout.addWidget(self.dimensions_panel, 1)

    def _build_action_buttons(self):
        self.action_buttons_panel = ActionButtonsPanelWidget(
            self._build_version_button_text()
        )
        self.version_btn = self.action_buttons_panel.version_btn
        self.reset_btn = self.action_buttons_panel.reset_btn
        self.add_tier_btn = self.action_buttons_panel.add_tier_btn

        self.version_btn.clicked.connect(self.open_releases_page)
        self.reset_btn.clicked.connect(self.reset_values)
        self.add_tier_btn.clicked.connect(self.add_current_to_tier_board)
        self.title_edit.textChanged.connect(self.update_add_tier_button_state)
        self.update_add_tier_button_state(self.title_edit.text())

        self.left_layout.addWidget(self.action_buttons_panel)

    def update_add_tier_button_state(self, title: str):
        self.add_tier_btn.setEnabled(bool(title.strip()))

    def _build_version_button_text(self) -> str:
        return build_version_button_text(APP_VERSION)

    def open_releases_page(self):
        log_info("ui", "button_click: open_releases_page")
        QDesktopServices.openUrl(QUrl(self.GITHUB_RELEASES_URL))

    def check_for_updates(self):
        result = check_for_update(APP_VERSION)

        if not result.ok:
            log_warning("update_check", f"update_check_failed: {result.error}")
            return

        presentation = build_update_check_version_button_presentation(
            result,
            self._build_version_button_text(),
        )
        if presentation is not None:
            self.version_btn.setText(presentation.text)
            self.version_btn.setStyleSheet(presentation.style_sheet)

        if not result.update_available:
            log_info(
                "update_check",
                f"no_update_available: local='{result.local_version}' latest='{result.latest_version}'",
            )
            return

        log_info(
            "update_check",
            f"update_available: local='{result.local_version}' latest='{result.latest_version}'",
        )

    def _build_right_panel(self):
        self.result_panel = ResultPanelWidget()
        self.result_panel.copy_result_image_requested.connect(
            self.copy_result_image_to_clipboard
        )
        self.result_panel.copy_details_requested.connect(self.copy_to_clipboard)
        self.right_box = self.result_panel

        self.score_label = self.result_panel.score_label
        self.tier_label = self.result_panel.tier_label
        self.summary_label = self.result_panel.summary_label
        self.result_card = self.result_panel.result_card
        self.copy_img_btn = self.result_panel.copy_img_btn
        self.table = self.result_panel.table
        self.copy_btn = self.result_panel.copy_btn

    def _build_tier_panel(self):
        self.tier_panel = TierPanelWidget()
        self.tier_box = self.tier_panel
        self.tier_board = self.tier_panel.tier_board
        self.tier_scroll_area = self.tier_panel.tier_scroll_area
        self.flip_all_tier_cards_btn = self.tier_panel.flip_all_tier_cards_btn
        self.clear_all_tier_cards_btn = self.tier_panel.clear_all_tier_cards_btn
        self.copy_tier_btn = self.tier_panel.copy_tier_btn

        self.tier_board.entries_changed.connect(self.update_tier_buttons_state)
        self.flip_all_tier_cards_btn.clicked.connect(self.flip_all_tier_cards)
        self.clear_all_tier_cards_btn.clicked.connect(self.clear_all_tier_cards)
        self.copy_tier_btn.clicked.connect(self.copy_tier_image_to_clipboard)

    def update_tier_buttons_state(self):
        self.tier_panel.update_buttons_state()

    def flip_all_tier_cards(self):
        log_info("ui", "button_click: flip_all_tier_cards")

        if not self.tier_board.has_flippable_entries():
            log_info("tier_board", "flip_all_cards_skipped: flippable_count=0")
            self.update_tier_buttons_state()
            return

        self.tier_board.toggle_all_saved_cards()

    def _ask_clear_all_tier_cards_confirmation(self) -> bool:
        confirmed = ask_tier_clear_all_confirmation(self)

        log_info(
            "tier_board",
            f"clear_all_entries_confirmation: decision='{'yes' if confirmed else 'no'}'",
        )

        return confirmed
    
    def clear_all_tier_cards(self):
        log_info("ui", "button_click: clear_all_tier_cards")

        if self.tier_board.saved_entry_count() <= 0:
            log_info("tier_board", "clear_all_entries_skipped: count=0")
            self.update_tier_buttons_state()
            return

        confirmed = self._ask_clear_all_tier_cards_confirmation()
        decision = "yes" if confirmed else "no"
        log_info("tier_board", f"clear_all_entries_confirmation: decision='{decision}'")

        if not confirmed:
            log_info("tier_board", "clear_all_entries_cancelled")
            return

        removed_count = self.tier_board.clear_all_saved_entries()
        log_info("tier_board", f"clear_all_entries_completed: count={removed_count}")
        self.update_tier_buttons_state()

    def _finalize_layout(self):
        self.main_layout.addWidget(self.left_box, 4)
        self.main_layout.addWidget(self.right_box, 2)
        self.main_layout.addWidget(self.tier_box, 3)

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
        if not self.profile_combos:
            return

        all_profiles = list(self.profiles.keys())
        if not all_profiles:
            return

        if needed is None:
            needed = MIX_MODES.get(self.mix_combo.currentText(), 1)

        self.profile_selection_memory = remember_profile_selections(
            memory=self.profile_selection_memory,
            current_profiles=[combo.currentText() for combo in self.profile_combos],
            all_profiles=all_profiles,
            needed=needed,
        )

    def _restore_profile_combo_selection(self, combo: QComboBox, index: int):
        remembered_profile = None
        if index < len(self.profile_selection_memory):
            remembered_profile = self.profile_selection_memory[index]

        if remembered_profile in self.profiles:
            combo.setCurrentText(remembered_profile)

    def on_mix_changed(self):
        previous_needed = getattr(self, "current_mix_needed", 1)
        self._remember_active_profile_selections(previous_needed)

        mode = self.mix_combo.currentText()
        log_info("ui", f"mix_mode_changed: mode='{mode}'")
        needed = MIX_MODES.get(mode, 1)

        self._building = True
        try:
            for i in range(3):
                enabled = i < needed
                self.profile_combos[i].setEnabled(enabled)
                self.weight_spins[i].setEnabled(enabled)

                cb = self.profile_combos[i]
                cb.blockSignals(True)
                cb.clear()

                if not enabled:
                    self.weight_spins[i].setValue(0)
                    cb.addItem("—")
                    cb.setCurrentIndex(0)
                else:
                    cb.addItems(list(self.profiles.keys()))
                    self._restore_profile_combo_selection(cb, i)

                cb.blockSignals(False)

            active_sum = sum(self.weight_spins[i].value() for i in range(needed))
            if active_sum <= 0:
                self.weight_spins[0].setValue(TOTAL_WEIGHT)
                for i in range(1, needed):
                    self.weight_spins[i].setValue(0)
            else:
                force_total_weight(self.weight_spins, needed, 0)

            self._update_profile_combo_options_internal()
            self._remember_active_profile_selections(needed)
            self.current_mix_needed = needed
        finally:
            self._building = False

        self.recompute()

    def on_profile_changed(self):
        if self._building:
            return

        self._building = True
        selected, ratios = get_selected_profiles_and_ratios(
            self.profile_combos,
            self.weight_spins,
            self.mix_combo.currentText(),
            MIX_MODES,
        )
        log_info("ui", f"profile_changed: selected={selected} ratios={ratios}")
        try:
            self._update_profile_combo_options_internal()
            self._remember_active_profile_selections()
        finally:
            self._building = False

        self.recompute()

    def _update_profile_combo_options_internal(self):
        if not self.profiles:
            return

        all_profiles = list(self.profiles.keys())
        if not all_profiles:
            return

        mode = self.mix_combo.currentText()
        needed = MIX_MODES.get(mode, 1)

        combo_options = build_profile_combo_options(
            all_profiles=all_profiles,
            current_profiles=[combo.currentText() for combo in self.profile_combos],
            needed=needed,
            slots=len(self.profile_combos),
        )

        for i, combo in enumerate(self.profile_combos):
            if i >= needed:
                continue

            allowed, selected_profile = combo_options[i]

            combo.blockSignals(True)
            combo.clear()
            combo.addItems(allowed)
            combo.setCurrentText(selected_profile or all_profiles[0])
            combo.blockSignals(False)

    def on_weight_changed(self, changed_idx: int, new_value: int):
        if self._building:
            return

        log_info("ui", f"weight_changed: idx={changed_idx} value={new_value}")

        mode = self.mix_combo.currentText()
        needed = MIX_MODES.get(mode, 1)

        if changed_idx >= needed:
            return

        self._building = True
        try:
            force_total_weight(self.weight_spins, needed, changed_idx)
        finally:
            self._building = False

        self.recompute()

    def on_slider_changed(self, idx: int, v: int):
        if self._building:
            return

        self._building = True
        apply_slider_value(self.states[idx], self.spin_widgets[idx], v)
        self._building = False
        self.recompute()

    def on_spin_changed(self, idx: int, v: float):
        if self._building:
            return

        self._building = True
        apply_spin_value(self.states[idx], self.slider_widgets[idx], v)
        self._building = False
        self.recompute()

    def reset_values(self):
        log_info("ui", "button_click: reset_values")

        self._building = True
        try:
            self.title_edit.clear()
            self.selected_anime_result = None
            self.selected_cover_pixmap = None
            if self.title_search_controller is not None:
                self.title_search_controller.reset_online_state()

            reset_combo_to_first_item(self.mix_combo)

            reset_dimension_controls(
                self.states,
                self.slider_widgets,
                self.spin_widgets,
            )

            reset_state = reset_profile_inputs_to_initial_state(
                profile_combos=self.profile_combos,
                weight_spins=self.weight_spins,
                profile_names=list(self.profiles.keys()),
                total_weight=TOTAL_WEIGHT,
            )
            self.profile_selection_memory = reset_state.selection_memory
            self.current_mix_needed = reset_state.current_mix_needed

            self._update_profile_combo_options_internal()
        finally:
            self._building = False

        self.on_mix_changed()

    def recompute(self):
        selected, ratios = get_selected_profiles_and_ratios(
            self.profile_combos,
            self.weight_spins,
            self.mix_combo.currentText(),
            MIX_MODES,
        )

        title = self.title_edit.text().strip()

        result = build_result_payload(
            profiles=self.profiles,
            selected=selected,
            ratios=ratios,
            states=self.states,
            tier_thresholds=self.tier_thresholds,
            ui_cfg=self.ui_cfg,
            title=title,
        )

        log_debug(
            "recompute",
            f"title='{title}' selected={result['selected']} ratios={result['ratios']} "
            f"vals={result['values']} score={result['score']:.4f} "
            f"tier={result['tier']} display={result['display_score']:.2f}",
        )

        self.latest_result = result

        self.result_panel.update_result(result, self.states)
        self.update_tier_preview(result)


    def update_tier_preview(self, result: dict):
        title = build_tier_preview_title(self.title_edit.text())
        self.tier_board.update_current_entry(
            title=title,
            score=result["display_score"],
            tier=result["tier"],
            cover_pixmap=self.selected_cover_pixmap,
        )

    def add_current_to_tier_board(self):
        log_info("ui", "button_click: add_current_to_tier_board")

        result = getattr(self, "latest_result", None)
        if result is None:
            self.recompute()
            result = getattr(self, "latest_result", None)

        outcome = add_result_to_tier_board(
            tier_board=self.tier_board,
            title=self.title_edit.text(),
            result=result,
            cover_pixmap=self.selected_cover_pixmap,
        )

        if outcome.status == TierAddStatus.MISSING_RESULT:
            log_warning("tier_board", "add_entry_aborted: missing latest_result")
            return

        if outcome.status == TierAddStatus.EMPTY_TITLE:
            log_warning("tier_board", "add_entry_rejected: empty_title")
            show_missing_tier_title_warning(self)
            return

        if outcome.status == TierAddStatus.REJECTED:
            log_warning(
                "tier_board",
                f"add_entry_rejected: duplicate_or_invalid title='{outcome.title}'",
            )
            show_duplicate_tier_title_information(self)

    def update_table(self, rel: List[float], contrib: List[float]):
        self.result_panel.update_table(self.states, rel, contrib)

    def copy_to_clipboard(self):
        log_info("ui", "button_click: copy_to_clipboard")

        copy_details_to_clipboard(
            profiles=self.profiles,
            profile_combos=self.profile_combos,
            weight_spins=self.weight_spins,
            mix_mode=self.mix_combo.currentText(),
            mix_modes=MIX_MODES,
            states=self.states,
            tier_thresholds=self.tier_thresholds,
            title=self.title_edit.text(),
        )

        show_temporary_copy_feedback(
            self.copy_btn,
            COPY_DETAILS_SUCCESS_TEXT,
            COPY_DETAILS_DEFAULT_TEXT,
        )

    def copy_result_image_to_clipboard(self):
        copy_result_card_image_to_clipboard(self.result_card)

        show_temporary_copy_feedback(
            self.copy_img_btn,
            COPY_SUCCESS_TEXT,
            COPY_RESULT_IMAGE_DEFAULT_TEXT,
        )

    def copy_tier_image_to_clipboard(self):
        log_info("ui", "button_click: copy_tier_image_to_clipboard")

        if self.tier_board.saved_entry_count() <= 0:
            log_info("tier_board", "export_skipped: count=0")
            self.update_tier_buttons_state()
            return

        log_info("tier_board", "export_started: copy_tier_board_as_image")

        outcome = copy_tier_board_image_to_clipboard(self.tier_board)

        if outcome.status == TierImageExportStatus.EMPTY:
            log_info("tier_board", "export_skipped: count=0")
            self.update_tier_buttons_state()
            return

        if outcome.status == TierImageExportStatus.FAILED:
            log_error("tier_board", f"export_failed: {outcome.error}")
            show_tier_image_copy_error(self)
            return

        log_info("tier_board", "export_completed: copied_tier_board_to_clipboard")

        show_temporary_copy_feedback(
            self.copy_tier_btn,
            COPY_SUCCESS_TEXT,
            COPY_TIER_IMAGE_DEFAULT_TEXT,
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
