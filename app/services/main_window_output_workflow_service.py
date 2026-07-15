from __future__ import annotations

from collections.abc import Callable

from app.logger import log_debug
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
from app.services.main_window_mode_service import APP_MODE_SCORED
from app.widgets.result_panel_widget import ResultPanelWidget


def update_add_tier_button_state_for_window(window, title: str):
    can_add_scored_result = window.current_mode == APP_MODE_SCORED
    set_add_tier_button_enabled(
        window.add_tier_btn,
        title if can_add_scored_result else "",
    )


def open_releases_page_for_window(
    window,
    *,
    log_info_func: Callable[[str, str], None],
    open_url_func: Callable,
):
    log_info_func("ui", "button_click: open_releases_page")
    open_releases_page_from_button(
        releases_url=window.GITHUB_RELEASES_URL,
        open_url_func=open_url_func,
    )


def check_for_updates_for_window(
    window,
    *,
    app_version: str,
    default_button_text: str,
    check_for_update_func: Callable,
):
    check_for_updates_from_button(
        version_btn=window.version_btn,
        app_version=app_version,
        default_button_text=default_button_text,
        check_for_update_func=check_for_update_func,
    )


def update_tier_buttons_state_for_window(window):
    update_tier_panel_buttons(window.tier_panel)


def flip_all_tier_cards_for_window(
    window,
    *,
    log_info_func: Callable[[str, str], None],
):
    log_info_func("ui", "button_click: flip_all_tier_cards")
    flip_tier_cards_from_button(
        tier_board=window.tier_board,
        update_tier_buttons_state=window.update_tier_buttons_state,
    )


def ask_clear_all_tier_cards_confirmation_for_window(
    window,
    *,
    ask_confirmation_func: Callable,
    log_info_func: Callable[[str, str], None],
) -> bool:
    confirmed = ask_confirmation_func(window)

    log_info_func(
        "tier_board",
        f"clear_all_entries_confirmation: decision='{'yes' if confirmed else 'no'}'",
    )

    return confirmed


def clear_all_tier_cards_for_window(
    window,
    *,
    log_info_func: Callable[[str, str], None],
):
    log_info_func("ui", "button_click: clear_all_tier_cards")
    clear_tier_cards_from_button(
        tier_board=window.tier_board,
        ask_confirmation=window._ask_clear_all_tier_cards_confirmation,
        update_tier_buttons_state=window.update_tier_buttons_state,
    )


def recompute_for_window(
    window,
    *,
    mix_modes,
    build_result_payload_func: Callable,
):
    if window.current_mode != APP_MODE_SCORED:
        log_debug("scoring", "recompute_skipped: app_mode='freehand'")
        return

    window.latest_result = recompute_from_window(
        profiles=window.profiles,
        profile_combos=window.profile_combos,
        weight_spins=window.weight_spins,
        mix_mode=window.mix_combo.currentText(),
        mix_modes=mix_modes,
        states=window.states,
        tier_thresholds=window.tier_thresholds,
        ui_cfg=window.ui_cfg,
        title=window.title_edit.text(),
        result_panel=window.result_panel,
        tier_board=window.tier_board,
        cover_pixmap=window.selected_cover_pixmap,
        build_result_payload_func=build_result_payload_func,
    )


def add_current_result_to_tier_board_for_window(
    window,
    *,
    log_info_func: Callable[[str, str], None],
):
    log_info_func("ui", "button_click: add_current_to_tier_board")
    add_current_result_from_window(
        parent=window,
        tier_board=window.tier_board,
        title=window.title_edit.text(),
        latest_result=getattr(window, "latest_result", None),
        recompute=window.recompute,
        get_latest_result=lambda: getattr(window, "latest_result", None),
        cover_pixmap=window.selected_cover_pixmap,
    )


def update_result_table_for_window(window, relevances, contributions):
    update_result_table_from_main(
        result_panel=window.result_panel,
        states=window.states,
        relevances=relevances,
        contributions=contributions,
    )


def copy_details_to_clipboard_for_window(
    window,
    *,
    mix_modes,
    log_info_func: Callable[[str, str], None],
):
    log_info_func("ui", "button_click: copy_to_clipboard")
    copy_details_from_button(
        profiles=window.profiles,
        profile_combos=window.profile_combos,
        weight_spins=window.weight_spins,
        mix_mode=window.mix_combo.currentText(),
        mix_modes=mix_modes,
        states=window.states,
        tier_thresholds=window.tier_thresholds,
        title=window.title_edit.text(),
        copy_btn=window.copy_btn,
    )


def copy_result_image_to_clipboard_for_window(window):
    copy_result_image_from_button(
        result_card=window.result_card,
        copy_img_btn=window.copy_img_btn,
    )


def copy_tier_image_to_clipboard_for_window(
    window,
    *,
    log_info_func: Callable[[str, str], None],
):
    log_info_func("ui", "button_click: copy_tier_image_to_clipboard")
    copy_tier_image_from_button(
        parent=window,
        tier_board=window.tier_board,
        copy_tier_btn=window.copy_tier_btn,
        update_tier_buttons_state=window.update_tier_buttons_state,
    )


def sanitize_result_summary_html(html: str) -> str:
    return ResultPanelWidget.sanitize_summary_html(html)


def strip_result_summary_style_color(style_value: str) -> str:
    return ResultPanelWidget.strip_color_from_style_attr(style_value)
