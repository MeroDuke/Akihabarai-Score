from __future__ import annotations

from collections.abc import Callable

from app.services.cover_image_service import load_selected_cover_preview_pixmap
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


def setup_title_autocomplete_for_window(window):
    if not window.anilist_integration_enabled:
        window.title_completer_model = None
        window.title_completer = None
        window.title_search_controller = None
        disable_title_autocomplete(
            title_edit=window.title_edit,
            controller=None,
        )
        return

    setup = setup_title_autocomplete(
        parent=window,
        title_edit=window.title_edit,
        debounce_ms=window.title_search_debounce_ms,
        is_online_mode=lambda: window.title_input_mode == window.TITLE_INPUT_MODE_ONLINE,
        is_integration_enabled=lambda: window.anilist_integration_enabled,
        on_title_selected=window.on_title_autocomplete_selected,
    )
    window.title_completer_model = setup.completer_model
    window.title_completer = setup.completer
    window.title_search_controller = setup.controller


def toggle_title_input_mode_for_window(
    window,
    *,
    log_change: bool,
    log_info_func: Callable[[str, str], None],
):
    window.title_input_mode = get_next_title_input_mode(
        integration_enabled=window.anilist_integration_enabled,
        current_mode=window.title_input_mode,
        offline_mode=window.TITLE_INPUT_MODE_OFFLINE,
        online_mode=window.TITLE_INPUT_MODE_ONLINE,
    )
    sync_title_input_mode_for_window(
        window,
        log_change=log_change,
        log_info_func=log_info_func,
    )


def sync_title_input_mode_for_window(
    window,
    *,
    log_change: bool,
    log_info_func: Callable[[str, str], None],
):
    window.title_input_mode = sync_title_input_mode_ui(
        title_input_mode=window.title_input_mode,
        title_placeholder_offline=window.title_placeholder_offline,
        title_placeholder_online=window.title_placeholder_online,
        title_edit=window.title_edit,
        title_mode_btn=window.title_mode_btn,
        integration_enabled=window.anilist_integration_enabled,
        controller=window.title_search_controller,
        completer=getattr(window, "title_completer", None),
    )

    if log_change:
        log_info_func("ui", f"title_input_mode_changed: mode='{window.title_input_mode}'")


def get_pending_title_search_query(window) -> str:
    if getattr(window, "title_search_controller", None) is None:
        return ""

    return window.title_search_controller.pending_title_search_query


def get_title_search_timer(window):
    if getattr(window, "title_search_controller", None) is None:
        return None

    return window.title_search_controller.title_search_timer


def enable_title_autocomplete_for_window(window):
    if not window.anilist_integration_enabled:
        disable_title_autocomplete_for_window(window)
        return

    enable_title_autocomplete(
        title_edit=window.title_edit,
        controller=window.title_search_controller,
        completer=getattr(window, "title_completer", None),
    )


def disable_title_autocomplete_for_window(window):
    disable_title_autocomplete(
        title_edit=window.title_edit,
        controller=window.title_search_controller,
    )


def refresh_title_autocomplete_results_for_window(window, query: str = ""):
    if not window.anilist_integration_enabled:
        return

    refresh_title_autocomplete_results(
        controller=getattr(window, "title_search_controller", None),
        query=query,
    )


def handle_title_search_text_changed_for_window(window, text: str):
    controller = (
        getattr(window, "title_search_controller", None)
        if window.anilist_integration_enabled
        else None
    )
    title_selection_state = handle_title_search_text_changed(
        text=text,
        selected_anime_result=window.selected_anime_result,
        selected_cover_pixmap=window.selected_cover_pixmap,
        controller=controller,
    )
    window.selected_anime_result = title_selection_state.selected_anime_result
    window.selected_cover_pixmap = title_selection_state.selected_cover_pixmap


def schedule_online_title_search_for_window(window, query: str):
    if not window.anilist_integration_enabled:
        return

    if getattr(window, "title_search_controller", None) is None:
        return

    window.title_search_controller.schedule_online_title_search(query)


def run_debounced_title_search_for_window(window):
    if not window.anilist_integration_enabled:
        return

    if getattr(window, "title_search_controller", None) is None:
        return

    window.title_search_controller.run_debounced_title_search()


def find_anime_result_by_title_for_window(window, title: str):
    if not window.anilist_integration_enabled:
        return None

    if getattr(window, "title_search_controller", None) is None:
        return None

    return window.title_search_controller.find_anime_result_by_title(title)


def handle_title_autocomplete_selected_for_window(window, title: str):
    controller = (
        getattr(window, "title_search_controller", None)
        if window.anilist_integration_enabled
        else None
    )
    selection_state = handle_title_autocomplete_selected(
        title=title,
        title_edit=window.title_edit,
        controller=controller,
        recompute=window.recompute,
        apply_selection=window._set_selected_title_state,
    )
    window.selected_anime_result = selection_state.selected_anime_result
    window.selected_cover_pixmap = selection_state.selected_cover_pixmap


def load_selected_cover_pixmap_for_window(window):
    if not window.anilist_integration_enabled:
        return None

    return load_selected_cover_preview_pixmap(window.selected_anime_result)


def set_selected_title_state_for_window(
    window,
    selected_anime_result,
    selected_cover_pixmap,
):
    window.selected_anime_result = selected_anime_result
    window.selected_cover_pixmap = selected_cover_pixmap
