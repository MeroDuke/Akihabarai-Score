from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

from app.widgets.action_buttons_panel_widget import ActionButtonsPanelWidget
from app.widgets.dimensions_panel_widget import DimensionsPanelWidget
from app.widgets.profile_mix_panel_widget import ProfileMixPanelWidget
from app.widgets.result_panel_widget import ResultPanelWidget
from app.widgets.tier_panel_widget import TierPanelWidget
from app.widgets.top_inputs_panel_widget import TopInputsPanelWidget


@dataclass
class MainWindowLayout:
    main_layout: QHBoxLayout
    left_box: QGroupBox
    left_layout: QVBoxLayout
    top_inputs_panel: TopInputsPanelWidget
    profile_mix_panel: ProfileMixPanelWidget
    dimensions_panel: DimensionsPanelWidget
    action_buttons_panel: ActionButtonsPanelWidget
    result_panel: ResultPanelWidget
    right_box: ResultPanelWidget
    tier_panel: TierPanelWidget
    tier_box: TierPanelWidget


def build_main_window_layout(
    *,
    window: QMainWindow,
    title_placeholder: str,
    title_max_length: int,
    mix_mode_names: Sequence[str],
    show_title_mode_button: bool,
    profile_names: Sequence[str],
    total_weight: int,
    states: Sequence,
    version_button_text: str,
    on_recompute: Callable[[], None],
    on_title_search_text_changed: Callable[[str], None],
    on_toggle_title_input_mode: Callable[[], None],
    on_mix_changed: Callable[[], None],
    on_profile_changed: Callable[[], None],
    on_weight_changed: Callable[[int, int], None],
    on_slider_changed: Callable[[int, int], None],
    on_spin_changed: Callable[[int, float], None],
    on_open_releases_page: Callable[[], None],
    on_toggle_app_mode: Callable[[], None],
    on_reset_values: Callable[[], None],
    on_add_current_to_tier_board: Callable[[], None],
    on_update_add_tier_button_state: Callable[[str], None],
    on_copy_result_image_to_clipboard: Callable[[], None],
    on_copy_to_clipboard: Callable[[], None],
    on_update_tier_buttons_state: Callable[[], None],
    on_flip_all_tier_cards: Callable[[], None],
    on_clear_all_tier_cards: Callable[[], None],
    on_copy_tier_image_to_clipboard: Callable[[], None],
) -> MainWindowLayout:
    root = QWidget()
    window.setCentralWidget(root)

    main_layout = QHBoxLayout(root)
    main_layout.setContentsMargins(16, 16, 16, 16)
    main_layout.setSpacing(16)

    left_box = QGroupBox("Bevitel")
    left_layout = QVBoxLayout(left_box)
    left_layout.setSpacing(10)

    top_inputs_panel = TopInputsPanelWidget(
        title_placeholder=title_placeholder,
        title_max_length=title_max_length,
        mix_mode_names=list(mix_mode_names),
        show_title_mode_button=show_title_mode_button,
    )
    title_edit = top_inputs_panel.title_edit
    title_mode_btn = top_inputs_panel.title_mode_btn
    mix_combo = top_inputs_panel.mix_combo

    title_edit.textChanged.connect(on_recompute)
    title_edit.textEdited.connect(on_title_search_text_changed)
    title_mode_btn.clicked.connect(on_toggle_title_input_mode)
    mix_combo.currentIndexChanged.connect(on_mix_changed)
    left_layout.addWidget(top_inputs_panel)

    profile_mix_panel = ProfileMixPanelWidget(profile_names, total_weight)
    for combo in profile_mix_panel.profile_combos:
        combo.currentIndexChanged.connect(on_profile_changed)

    for index, weight_spin in enumerate(profile_mix_panel.weight_spins):
        weight_spin.valueChanged.connect(
            lambda value, idx=index: on_weight_changed(idx, value)
        )
    left_layout.addWidget(profile_mix_panel)

    dimensions_panel = DimensionsPanelWidget(states)
    for index, slider in enumerate(dimensions_panel.slider_widgets):
        slider.valueChanged.connect(
            lambda value, idx=index: on_slider_changed(idx, value)
        )

    for index, spin in enumerate(dimensions_panel.spin_widgets):
        spin.valueChanged.connect(
            lambda value, idx=index: on_spin_changed(idx, value)
        )
    left_layout.addWidget(dimensions_panel, 1)

    action_buttons_panel = ActionButtonsPanelWidget(version_button_text)
    action_buttons_panel.version_btn.clicked.connect(on_open_releases_page)
    action_buttons_panel.mode_btn.clicked.connect(on_toggle_app_mode)
    action_buttons_panel.reset_btn.clicked.connect(on_reset_values)
    action_buttons_panel.add_tier_btn.clicked.connect(on_add_current_to_tier_board)
    title_edit.textChanged.connect(on_update_add_tier_button_state)
    left_layout.addWidget(action_buttons_panel)

    result_panel = ResultPanelWidget()
    result_panel.copy_result_image_requested.connect(on_copy_result_image_to_clipboard)
    result_panel.copy_details_requested.connect(on_copy_to_clipboard)

    tier_panel = TierPanelWidget()
    tier_panel.tier_board.entries_changed.connect(on_update_tier_buttons_state)
    tier_panel.flip_all_tier_cards_btn.clicked.connect(on_flip_all_tier_cards)
    tier_panel.clear_all_tier_cards_btn.clicked.connect(on_clear_all_tier_cards)
    tier_panel.copy_tier_btn.clicked.connect(on_copy_tier_image_to_clipboard)

    main_layout.addWidget(left_box, 4)
    main_layout.addWidget(result_panel, 2)
    main_layout.addWidget(tier_panel, 3)

    return MainWindowLayout(
        main_layout=main_layout,
        left_box=left_box,
        left_layout=left_layout,
        top_inputs_panel=top_inputs_panel,
        profile_mix_panel=profile_mix_panel,
        dimensions_panel=dimensions_panel,
        action_buttons_panel=action_buttons_panel,
        result_panel=result_panel,
        right_box=result_panel,
        tier_panel=tier_panel,
        tier_box=tier_panel,
    )
