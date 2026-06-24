import sys
import re
import ctypes
from typing import List, Optional

from PyQt6.QtCore import Qt, QTimer, QSize, QEvent, QStringListModel, QUrl
from PyQt6.QtGui import QFont, QPalette, QDesktopServices
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QSlider, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QComboBox,
    QMessageBox, QSpinBox, QSizePolicy, QFrame, QCompleter, QScrollArea
)

from app.core.constants import APP_TITLE, MIX_MODES, TOTAL_WEIGHT
from app.version import APP_VERSION
from app.services.update_check_service import check_for_update
from app.core.models import AnimeSearchResult, DimState
from app.core.runtime import load_app_icon
from app.core.formatters import format_score
from app.config.ui_config import load_ui_config
from app.config.profiles_config import load_profiles_config
from app.logger import init_logger, log_debug, log_info, log_warning, log_error
from app.services.scoring_pipeline import build_result_payload, build_export_text
from app.services.clipboard_service import (
    copy_text_to_clipboard,
    copy_widget_as_pixmap,
)
from app.services.profile_mix_service import (
    get_selected_profiles_and_ratios,
    force_total_weight,
)
from app.services.cover_image_service import load_cover_pixmap_from_url
from app.widgets.tier_board_widget import TierBoardWidget
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
        top_label_w = 140
        top_button_w = 80

        top_grid = QGridLayout()
        top_grid.setHorizontalSpacing(10)
        top_grid.setVerticalSpacing(8)
        top_grid.setColumnMinimumWidth(0, top_label_w)
        top_grid.setColumnStretch(1, 1)
        top_grid.setColumnMinimumWidth(2, top_button_w)

        title_lbl = QLabel("Anime / szezon cím:")
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText(self.title_placeholder_offline)
        self.title_edit.setMaxLength(self.title_max_length)
        self.title_edit.textChanged.connect(self.recompute)
        self.title_edit.textEdited.connect(self.on_title_search_text_changed)
        self._setup_title_autocomplete()

        self.title_mode_btn = QPushButton()
        self.title_mode_btn.setMinimumWidth(80)
        self.title_mode_btn.setMaximumWidth(80)
        self.title_mode_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.title_mode_btn.clicked.connect(self.toggle_title_input_mode)

        self._sync_title_mode_ui(log_change=False)
        self.title_mode_btn.setVisible(self.anilist_integration_enabled)

        top_grid.addWidget(title_lbl, 0, 0)
        top_grid.addWidget(self.title_edit, 0, 1, 1, 2)
        top_grid.addWidget(self.title_mode_btn, 0, 3, 2, 1)

        mix_lbl = QLabel("Profil-mix mód:")
        self.mix_combo = QComboBox()
        self.mix_combo.addItems(list(MIX_MODES.keys()))
        self.mix_combo.currentIndexChanged.connect(self.on_mix_changed)

        top_grid.addWidget(mix_lbl, 1, 0)
        top_grid.addWidget(self.mix_combo, 1, 1, 1, 2)

        self.left_layout.addLayout(top_grid)

    def _get_window_config(self) -> dict:
        window_cfg = self.ui_cfg.get("window")
        if not isinstance(window_cfg, dict):
            return {}

        return window_cfg

    def _get_window_int_setting(self, key: str, default: int) -> int:
        value = self._get_window_config().get(key, default)
        if isinstance(value, bool):
            return default

        try:
            parsed_value = int(value)
        except (TypeError, ValueError):
            return default

        if parsed_value <= 0:
            return default

        return parsed_value

    def get_default_window_size(self) -> tuple[int, int]:
        return (
            self._get_window_int_setting(
                "default_width",
                self.DEFAULT_WINDOW_WIDTH,
            ),
            self._get_window_int_setting(
                "default_height",
                self.DEFAULT_WINDOW_HEIGHT,
            ),
        )

    def get_minimum_window_size(self) -> tuple[int, int]:
        return (
            self._get_window_int_setting(
                "minimum_width",
                self.DEFAULT_MINIMUM_WINDOW_WIDTH,
            ),
            self._get_window_int_setting(
                "minimum_height",
                self.DEFAULT_MINIMUM_WINDOW_HEIGHT,
            ),
        )

    def _get_window_size(self) -> tuple[int, int]:
        return self.get_default_window_size()

    def _get_minimum_window_size(self) -> tuple[int, int]:
        return self.get_minimum_window_size()

    def _is_anilist_integration_enabled(self) -> bool:
        features = self.ui_cfg.get("features")
        if not isinstance(features, dict):
            return True

        return bool(features.get("anilist_enabled", True))

    def _get_anilist_config(self) -> dict:
        anilist_cfg = self.ui_cfg.get("anilist")
        if not isinstance(anilist_cfg, dict):
            return {}

        return anilist_cfg

    def _get_anilist_text_setting(self, key: str, default: str) -> str:
        value = self._get_anilist_config().get(key, default)
        if not isinstance(value, str) or not value.strip():
            return default

        return value

    def _get_anilist_int_setting(self, key: str, default: int) -> int:
        value = self._get_anilist_config().get(key, default)
        if isinstance(value, bool):
            return default

        try:
            parsed_value = int(value)
        except (TypeError, ValueError):
            return default

        if parsed_value <= 0:
            return default

        return parsed_value

    def toggle_title_input_mode(self):
        if not self.anilist_integration_enabled:
            return

        if self.title_input_mode == self.TITLE_INPUT_MODE_OFFLINE:
            self.title_input_mode = self.TITLE_INPUT_MODE_ONLINE
        else:
            self.title_input_mode = self.TITLE_INPUT_MODE_OFFLINE

        self._sync_title_mode_ui(log_change=True)

    def _sync_title_mode_ui(self, log_change: bool = False):
        if self.title_input_mode == self.TITLE_INPUT_MODE_ONLINE:
            self.title_edit.setPlaceholderText(self.title_placeholder_online)
            self.title_mode_btn.setText("🌐 Online")
            self._enable_title_autocomplete()
        else:
            self.title_input_mode = self.TITLE_INPUT_MODE_OFFLINE
            self.title_edit.setPlaceholderText(self.title_placeholder_offline)
            self.title_mode_btn.setText("✏ Offline")
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
        profiles_group = QGroupBox("Profil konfiguráció")
        profiles_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        prof_row = QGridLayout(profiles_group)
        prof_row.setColumnMinimumWidth(0, 130)
        prof_row.setColumnMinimumWidth(1, 220)
        prof_row.setColumnMinimumWidth(3, 80)
        prof_row.setColumnStretch(1, 1)
        prof_row.setHorizontalSpacing(10)
        prof_row.setVerticalSpacing(6)

        hdr_profile = QLabel("Profil")
        hdr_weight = QLabel("Súly (0-100)")
        hdr_profile.setStyleSheet("font-weight: 600;")
        hdr_weight.setStyleSheet("font-weight: 600;")

        prof_row.addWidget(QLabel(""), 0, 0)
        prof_row.addWidget(hdr_profile, 0, 1, 1, 2)
        prof_row.addWidget(hdr_weight, 0, 3)

        for i in range(3):
            lbl = QLabel(f"Profil {i + 1}:")
            combo = QComboBox()
            combo.addItems(self.profile_names)
            combo.currentIndexChanged.connect(self.on_profile_changed)

            wspin = QSpinBox()
            wspin.setMinimum(0)
            wspin.setMaximum(TOTAL_WEIGHT)
            wspin.setSingleStep(1)
            wspin.setValue(0)
            wspin.valueChanged.connect(lambda v, idx=i: self.on_weight_changed(idx, v))

            self.profile_combos.append(combo)
            self.weight_spins.append(wspin)

            prof_row.addWidget(lbl, i + 1, 0)
            prof_row.addWidget(combo, i + 1, 1, 1, 2)
            prof_row.addWidget(wspin, i + 1, 3)

        for r in range(0, 4):
            prof_row.setRowStretch(r, 0)

        self.left_layout.addWidget(profiles_group)

    def _build_dimensions_group(self):
        grid = QGridLayout()
        grid.setColumnMinimumWidth(0, 130)
        grid.setColumnMinimumWidth(2, 80)
        grid.setColumnStretch(1, 1)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        header_name = QLabel("Dimenzió")
        header_val = QLabel("Pont (1-10)")
        header_name.setStyleSheet("font-weight: 600;")
        header_val.setStyleSheet("font-weight: 600;")

        grid.addWidget(header_name, 0, 0)
        grid.addWidget(QLabel(""), 0, 1)
        grid.addWidget(header_val, 0, 2)

        for i, st in enumerate(self.states):
            row = i + 1
            name = QLabel(st.name)
            name.setWordWrap(True)

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(10)
            slider.setMaximum(100)
            slider.setValue(int(st.value * 10))
            slider.valueChanged.connect(lambda v, idx=i: self.on_slider_changed(idx, v))

            spin = QDoubleSpinBox()
            spin.setMinimum(1.0)
            spin.setMaximum(10.0)
            spin.setSingleStep(0.1)
            spin.setDecimals(1)
            spin.setValue(st.value)
            spin.valueChanged.connect(lambda v, idx=i: self.on_spin_changed(idx, v))

            self.slider_widgets.append(slider)
            self.spin_widgets.append(spin)

            grid.addWidget(name, row, 0)
            grid.addWidget(slider, row, 1)
            grid.addWidget(spin, row, 2)

        dims_group = QGroupBox("Dimenziók")
        dims_layout = QVBoxLayout(dims_group)
        dims_layout.setContentsMargins(12, 10, 12, 10)
        dims_layout.setSpacing(10)
        dims_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        grid.setVerticalSpacing(10)

        dims_layout.addLayout(grid)
        dims_layout.addStretch(1)

        self.left_layout.addWidget(dims_group, 1)

    def _build_action_buttons(self):
        btn_row = QHBoxLayout()

        self.version_btn = QPushButton(self._build_version_button_text())
        self.version_btn.clicked.connect(self.open_releases_page)
        self.version_btn.setFixedHeight(30)
        btn_row.addWidget(self.version_btn)

        self.reset_btn = QPushButton("Alaphelyzet (5,0)")
        self.reset_btn.clicked.connect(self.reset_values)
        self.reset_btn.setFixedHeight(30)
        btn_row.addWidget(self.reset_btn)

        self.add_tier_btn = QPushButton("Hozzáadás Tier listához")
        self.add_tier_btn.clicked.connect(self.add_current_to_tier_board)
        self.add_tier_btn.setFixedHeight(30)
        btn_row.addWidget(self.add_tier_btn)

        self.left_layout.addLayout(btn_row)

    def _build_version_button_text(self) -> str:
        version = APP_VERSION.strip()
        if not version.startswith("v"):
            version = f"v{version}"

        return f"Verzió: {version}"

    def open_releases_page(self):
        log_info("ui", "button_click: open_releases_page")
        QDesktopServices.openUrl(QUrl(self.GITHUB_RELEASES_URL))

    def check_for_updates(self):
        result = check_for_update(APP_VERSION)

        if not result.ok:
            log_warning("update_check", f"update_check_failed: {result.error}")
            return

        if not result.update_available:
            log_info(
                "update_check",
                f"no_update_available: local='{result.local_version}' latest='{result.latest_version}'",
            )
            self.version_btn.setText(self._build_version_button_text())
            self.version_btn.setStyleSheet("")
            return

        log_info(
            "update_check",
            f"update_available: local='{result.local_version}' latest='{result.latest_version}'",
        )
        self.version_btn.setText(f"Frissítés elérhető: {result.latest_version}")
        self.version_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-weight: bold;
            }
        """)

    def _build_right_panel(self):
        self.right_box = QGroupBox("Eredmény")
        right_layout = QVBoxLayout(self.right_box)
        right_layout.setSpacing(10)

        self._build_result_card(right_layout)
        self._build_result_copy_button(right_layout)
        self._build_results_table(right_layout)
        self._build_details_copy_button(right_layout)

    def _build_result_card(self, parent_layout: QVBoxLayout):
        self.score_label = QLabel("— / 10")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_font = QFont()
        score_font.setPointSize(28)
        score_font.setBold(True)
        self.score_label.setFont(score_font)

        self.tier_label = QLabel("—")
        self.tier_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tier_font = QFont()
        tier_font.setPointSize(28)
        tier_font.setBold(True)
        self.tier_label.setFont(tier_font)

        self.summary_label = QLabel("")
        self.summary_label.setWordWrap(True)
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.summary_label.setTextFormat(Qt.TextFormat.RichText)
        summary_font = QFont()
        summary_font.setPointSize(10)  # vagy ami passzol
        summary_font.setBold(True)
        self.summary_label.setFont(summary_font)
        self._apply_summary_theme_style()

        self.result_card = QWidget()
        card_layout = QVBoxLayout(self.result_card)
        self.result_card.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Maximum,
        )
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(10)
        card_layout.setContentsMargins(0, 0, 0, 0)

        card_layout.addWidget(self.score_label)
        card_layout.addWidget(self.tier_label)
        card_layout.addWidget(self.summary_label)

        parent_layout.addWidget(self.result_card, alignment=Qt.AlignmentFlag.AlignCenter)

    def _build_result_copy_button(self, parent_layout: QVBoxLayout):
        self.copy_img_btn = QPushButton("Eredmény képként másolása")
        self.copy_img_btn.setFixedHeight(32)
        self.copy_img_btn.clicked.connect(self.copy_result_image_to_clipboard)

        style = self.style()
        self.copy_img_btn.setIcon(
            style.standardIcon(style.StandardPixmap.SP_FileDialogListView)
        )
        self.copy_img_btn.setIconSize(QSize(16, 16))

        parent_layout.addWidget(self.copy_img_btn)

    def _build_results_table(self, parent_layout: QVBoxLayout):
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Dimenzió", "Pont", "Relevancia", "Hozzájárulás"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        for c in (1, 2, 3):
            self.table.horizontalHeader().setSectionResizeMode(
                c, QHeaderView.ResizeMode.ResizeToContents
            )
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        parent_layout.addWidget(self.table, 1)

    def _build_details_copy_button(self, parent_layout: QVBoxLayout):
        self.copy_btn = QPushButton("Részletes adatok másolása vágólapra")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setFixedHeight(32)

        style = self.style()
        self.copy_btn.setIcon(style.standardIcon(style.StandardPixmap.SP_FileIcon))
        self.copy_btn.setIconSize(QSize(16, 16))

        parent_layout.addWidget(self.copy_btn)

    def _build_tier_panel(self):
        self.tier_box = QGroupBox("Tier lista")
        self.tier_box.setMinimumWidth(320)

        tier_layout = QVBoxLayout(self.tier_box)
        tier_layout.setContentsMargins(8, 10, 8, 10)
        tier_layout.setSpacing(8)

        self.tier_board = TierBoardWidget()
        self.tier_board.entries_changed.connect(self.update_tier_buttons_state)

        self.tier_scroll_area = QScrollArea()
        self.tier_scroll_area.setWidgetResizable(True)
        self.tier_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.tier_scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.tier_scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.tier_scroll_area.setWidget(self.tier_board)

        tier_layout.addWidget(self.tier_scroll_area, 1)

        tier_button_row = QHBoxLayout()
        tier_button_row.setSpacing(8)

        self.flip_all_tier_cards_btn = QPushButton("Összes kártya megfordítása")
        self.flip_all_tier_cards_btn.setFixedHeight(32)
        self.flip_all_tier_cards_btn.clicked.connect(self.flip_all_tier_cards)
        self.flip_all_tier_cards_btn.setEnabled(False)
        tier_button_row.addWidget(self.flip_all_tier_cards_btn)

        self.clear_all_tier_cards_btn = QPushButton("Minden kártya törlése")
        self.clear_all_tier_cards_btn.setFixedHeight(32)
        self.clear_all_tier_cards_btn.clicked.connect(self.clear_all_tier_cards)
        self.clear_all_tier_cards_btn.setEnabled(False)
        tier_button_row.addWidget(self.clear_all_tier_cards_btn)

        self.copy_tier_btn = QPushButton("Tier lista képként másolása")
        self.copy_tier_btn.setFixedHeight(32)
        self.copy_tier_btn.clicked.connect(self.copy_tier_image_to_clipboard)
        self.copy_tier_btn.setEnabled(False)

        style = self.style()
        self.copy_tier_btn.setIcon(
            style.standardIcon(style.StandardPixmap.SP_FileDialogListView)
        )
        self.copy_tier_btn.setIconSize(QSize(16, 16))
        tier_button_row.addWidget(self.copy_tier_btn)

        tier_layout.addLayout(tier_button_row)

    def update_tier_buttons_state(self):
        has_saved_entries = self.tier_board.saved_entry_count() > 0
        self.flip_all_tier_cards_btn.setEnabled(has_saved_entries)
        self.clear_all_tier_cards_btn.setEnabled(has_saved_entries)
        self.copy_tier_btn.setEnabled(has_saved_entries)

    def flip_all_tier_cards(self):
        log_info("ui", "button_click: flip_all_tier_cards")
        self.tier_board.toggle_all_saved_cards()

    def clear_all_tier_cards(self):
        log_info("ui", "button_click: clear_all_tier_cards")

        if self.tier_board.saved_entry_count() <= 0:
            log_info("tier_board", "clear_all_entries_skipped: count=0")
            self.update_tier_buttons_state()
            return

        answer = QMessageBox.question(
            self,
            "Tier lista törlése",
            "Biztosan törlöd az összes mentett kártyát a Tier listáról?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
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
        text_color = self.summary_label.palette().color(
            QPalette.ColorRole.WindowText
        ).name()
        self.summary_label.setStyleSheet(f"QLabel {{ color: {text_color}; }}")

    @staticmethod
    def _sanitize_summary_html(html: str) -> str:
        if not html:
            return ""

        sanitized = html
        sanitized = re.sub(
            r'\sstyle\s*=\s*(["\'])(.*?)\1',
            lambda m: MainWindow._strip_color_from_style_attr(m.group(2)),
            sanitized,
            flags=re.IGNORECASE | re.DOTALL,
        )
        sanitized = re.sub(
            r'<\s*font\b([^>]*?)\scolor\s*=\s*(["\']).*?\2([^>]*)>',
            r"<font\1\3>",
            sanitized,
            flags=re.IGNORECASE | re.DOTALL,
        )
        sanitized = re.sub(
            r"<\s*font\b([^>]*?)\scolor\s*=\s*[^\s>]+([^>]*)>",
            r"<font\1\2>",
            sanitized,
            flags=re.IGNORECASE | re.DOTALL,
        )
        return sanitized

    @staticmethod
    def _strip_color_from_style_attr(style_value: str) -> str:
        parts = [part.strip() for part in style_value.split(";") if part.strip()]
        filtered = [
            part for part in parts
            if not re.match(r"^(color|background-color)\s*:", part, flags=re.IGNORECASE)
        ]

        if not filtered:
            return ""

        return ' style="' + "; ".join(filtered) + '"'

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
            QMessageBox.warning(self, "Konfigurációs hiba", err)

        if ui_err:
            QMessageBox.warning(self, "Felületkonfigurációs hiba", ui_err)

    def _apply_initial_weights(self):
        self._building = True
        self.weight_spins[0].setValue(TOTAL_WEIGHT)
        self.weight_spins[1].setValue(0)
        self.weight_spins[2].setValue(0)
        self._building = False

    def _default_profile_selection_memory(self) -> List[Optional[str]]:
        all_profiles = list(self.profiles.keys())
        if not all_profiles:
            return [None, None, None]

        remembered: List[Optional[str]] = []
        for i in range(3):
            remembered.append(all_profiles[i] if i < len(all_profiles) else all_profiles[0])

        return remembered

    def _remember_active_profile_selections(self, needed: int | None = None):
        if not self.profile_combos:
            return

        all_profiles = set(self.profiles.keys())
        if not all_profiles:
            return

        if needed is None:
            needed = MIX_MODES.get(self.mix_combo.currentText(), 1)

        for i in range(min(needed, len(self.profile_combos), len(self.profile_selection_memory))):
            current_profile = self.profile_combos[i].currentText()
            if current_profile in all_profiles:
                self.profile_selection_memory[i] = current_profile

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

        current = [cb.currentText() for cb in self.profile_combos]

        used = set()
        chosen: List[Optional[str]] = [None, None, None]

        for i in range(needed):
            cur = current[i]
            if cur in all_profiles and cur not in used:
                chosen[i] = cur
                used.add(cur)
            else:
                for p in all_profiles:
                    if p not in used:
                        chosen[i] = p
                        used.add(p)
                        break
                if chosen[i] is None:
                    chosen[i] = all_profiles[0]

        for i in range(needed, 3):
            chosen[i] = all_profiles[0]

        for i, combo in enumerate(self.profile_combos):
            if i >= needed:
                continue

            other_used = set(chosen[:needed])
            other_used.discard(chosen[i])

            allowed = []
            for p in all_profiles:
                if p == chosen[i] or p not in other_used:
                    allowed.append(p)

            combo.blockSignals(True)
            combo.clear()
            combo.addItems(allowed)
            combo.setCurrentText(chosen[i] or all_profiles[0])
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
        value = v / 10.0
        self.states[idx].value = value
        self.spin_widgets[idx].setValue(value)
        self._building = False
        self.recompute()

    def on_spin_changed(self, idx: int, v: float):
        if self._building:
            return

        self._building = True
        self.states[idx].value = float(v)
        self.slider_widgets[idx].setValue(int(round(v * 10)))
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

            self.mix_combo.blockSignals(True)
            self.mix_combo.setCurrentIndex(0)
            self.mix_combo.blockSignals(False)

            for i in range(len(self.states)):
                self.states[i].value = 5.0
                self.slider_widgets[i].setValue(50)
                self.spin_widgets[i].setValue(5.0)

            self._apply_initial_weights()
            self.profile_selection_memory = self._default_profile_selection_memory()
            self.current_mix_needed = 1

            if self.profile_combos:
                self.profile_combos[0].blockSignals(True)
                self.profile_combos[0].setCurrentIndex(0)
                self.profile_combos[0].blockSignals(False)

                for combo in self.profile_combos[1:]:
                    combo.blockSignals(True)
                    combo.setCurrentIndex(0)
                    combo.blockSignals(False)

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

        self.score_label.setText(f"{format_score(result['display_score'])} / 10")
        self.tier_label.setText(f"Tier: {result['tier']}")
        self.summary_label.setText(self._sanitize_summary_html(result["summary_html"]))
        self._apply_summary_theme_style()

        self.summary_label.setMinimumHeight(self.summary_label.sizeHint().height())
        self.summary_label.updateGeometry()
        self.result_card.layout().activate()
        self.update_table(result["relevances"], result["contributions"])
        self.update_tier_preview(result)


    def update_tier_preview(self, result: dict):
        title = self.title_edit.text().strip() or "(nincs cím)"
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

        if result is None:
            log_warning("tier_board", "add_entry_aborted: missing latest_result")
            return

        title = self.title_edit.text().strip()
        if not title:
            log_warning("tier_board", "add_entry_rejected: empty_title")
            QMessageBox.warning(
                self,
                "Hiányzó cím",
                "Tier listához csak megadott címmel lehet elemet hozzáadni.",
            )
            return

        was_added = self.tier_board.add_saved_entry(
            title=title,
            score=result["display_score"],
            tier=result["tier"],
            cover_pixmap=self.selected_cover_pixmap,
        )

        if not was_added:
            log_warning("tier_board", f"add_entry_rejected: duplicate_or_invalid title='{title}'")
            QMessageBox.information(
                self,
                "Már szerepel",
                "Ez a cím már szerepel a Tier listában.",
            )

    def update_table(self, rel: List[float], contrib: List[float]):
        self.table.setRowCount(8)
        for r in range(8):
            name = self.states[r].name
            val = self.states[r].value
            w = rel[r]
            c = contrib[r]

            items = [
                QTableWidgetItem(name),
                QTableWidgetItem(format_score(val)),
                QTableWidgetItem(f"{w:.2f}"),
                QTableWidgetItem(f"{c:.2f}"),
            ]
            items[0].setToolTip(name)

            for cidx, it in enumerate(items):
                if cidx in (1, 2, 3):
                    it.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                else:
                    it.setTextAlignment(
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                    )
                self.table.setItem(r, cidx, it)

    def copy_to_clipboard(self):
        log_info("ui", "button_click: copy_to_clipboard")

        selected, ratios = get_selected_profiles_and_ratios(
            self.profile_combos,
            self.weight_spins,
            self.mix_combo.currentText(),
            MIX_MODES,
        )

        text = build_export_text(
            profiles=self.profiles,
            selected=selected,
            ratios=ratios,
            states=self.states,
            tier_thresholds=self.tier_thresholds,
            title=self.title_edit.text().strip(),
        )

        copy_text_to_clipboard(text)

        self.copy_btn.setText("✔ Részletes adatok másolva!")
        QTimer.singleShot(
            1500,
            lambda: self.copy_btn.setText("Részletes adatok másolása vágólapra"),
        )

    def copy_result_image_to_clipboard(self):
        copy_widget_as_pixmap(self.result_card)

        self.copy_img_btn.setText("✔ Másolva!")
        QTimer.singleShot(
            1500,
            lambda: self.copy_img_btn.setText("Eredmény képként másolása"),
        )

    def copy_tier_image_to_clipboard(self):
        log_info("ui", "button_click: copy_tier_image_to_clipboard")

        if self.tier_board.saved_entry_count() <= 0:
            log_info("tier_board", "export_skipped: count=0")
            self.update_tier_buttons_state()
            return

        log_info("tier_board", "export_started: copy_tier_board_as_image")

        self.tier_board.prepare_export_mode(True)
        QApplication.processEvents()

        try:
            QApplication.clipboard().setPixmap(self.tier_board.grab())
            log_info("tier_board", "export_completed: copied_tier_board_to_clipboard")
        except Exception as exc:
            log_error("tier_board", f"export_failed: {exc}")
            QMessageBox.critical(
                self,
                "Másolási hiba",
                "Nem sikerült a Tier listát képként vágólapra másolni.",
            )
            return
        finally:
            self.tier_board.prepare_export_mode(False)

        self.copy_tier_btn.setText("✔ Másolva!")
        QTimer.singleShot(
            1500,
            lambda: self.copy_tier_btn.setText("Tier lista képként másolása"),
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