from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtWidgets import QCompleter

from app.controllers.anilist_title_search_controller import (
    AniListTitleSearchController,
)
from app.logger import log_info
from app.services.cover_image_service import load_selected_cover_preview_pixmap
from app.services.title_selection_service import (
    TitleSelectionState,
    clear_title_selection_if_text_changed,
)
from app.widgets.title_input_mode_presenter import (
    build_title_input_mode_presentation,
)


@dataclass
class TitleAutocompleteSetup:
    completer_model: QStringListModel
    completer: QCompleter
    controller: AniListTitleSearchController


@dataclass
class TitleAutocompleteSelectionState:
    selected_anime_result: object | None
    selected_cover_pixmap: object | None


def get_next_title_input_mode(
    *,
    integration_enabled: bool,
    current_mode: str,
    offline_mode: str,
    online_mode: str,
) -> str:
    if not integration_enabled:
        return offline_mode

    if current_mode == offline_mode:
        return online_mode

    return offline_mode


def setup_title_autocomplete(
    *,
    parent,
    title_edit,
    debounce_ms: int,
    is_online_mode: Callable[[], bool],
    is_integration_enabled: Callable[[], bool],
    on_title_selected: Callable[[str], None],
) -> TitleAutocompleteSetup:
    completer_model = QStringListModel([], parent)
    completer = QCompleter(completer_model, parent)
    completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    completer.setFilterMode(Qt.MatchFlag.MatchContains)
    completer.activated[str].connect(on_title_selected)

    controller = AniListTitleSearchController(
        parent=parent,
        completer_model=completer_model,
        completer=completer,
        debounce_ms=debounce_ms,
        is_online_mode=is_online_mode,
        is_integration_enabled=is_integration_enabled,
    )

    controller.refresh_title_autocomplete_results()
    disable_title_autocomplete(title_edit=title_edit, controller=controller)

    return TitleAutocompleteSetup(
        completer_model=completer_model,
        completer=completer,
        controller=controller,
    )


def sync_title_input_mode_ui(
    *,
    title_input_mode: str,
    title_placeholder_offline: str,
    title_placeholder_online: str,
    title_edit,
    title_mode_btn,
    integration_enabled: bool,
    controller: AniListTitleSearchController | None,
    completer: QCompleter | None,
) -> str:
    presentation = build_title_input_mode_presentation(
        title_input_mode,
        title_placeholder_offline,
        title_placeholder_online,
    )

    title_edit.setPlaceholderText(presentation.placeholder)
    title_mode_btn.setText(presentation.button_text)

    if presentation.autocomplete_enabled and integration_enabled:
        enable_title_autocomplete(
            title_edit=title_edit,
            controller=controller,
            completer=completer,
        )
    else:
        disable_title_autocomplete(
            title_edit=title_edit,
            controller=controller,
        )

    return presentation.mode


def enable_title_autocomplete(
    *,
    title_edit,
    controller: AniListTitleSearchController | None,
    completer: QCompleter | None,
):
    if controller is None or completer is None:
        disable_title_autocomplete(title_edit=title_edit, controller=controller)
        return

    controller.refresh_title_autocomplete_results(title_edit.text())

    title_edit.setCompleter(None)
    title_edit.setCompleter(completer)


def disable_title_autocomplete(
    *,
    title_edit,
    controller: AniListTitleSearchController | None,
):
    if controller is not None:
        controller.title_search_timer.stop()
    title_edit.setCompleter(None)


def refresh_title_autocomplete_results(
    *,
    controller: AniListTitleSearchController | None,
    query: str = "",
):
    if controller is None:
        return

    controller.refresh_title_autocomplete_results(query)


def handle_title_search_text_changed(
    *,
    text: str,
    selected_anime_result,
    selected_cover_pixmap,
    controller: AniListTitleSearchController | None,
) -> TitleSelectionState:
    title_selection_state = clear_title_selection_if_text_changed(
        text,
        selected_anime_result,
        selected_cover_pixmap,
    )

    if controller is not None:
        controller.handle_title_text_edited(text)

    return title_selection_state


def handle_title_autocomplete_selected(
    *,
    title: str,
    title_edit,
    controller: AniListTitleSearchController | None,
    recompute: Callable[[], None],
    apply_selection: Callable[[object | None, object | None], None] | None = None,
    load_cover_pixmap: Callable[[object | None], object | None] = (
        load_selected_cover_preview_pixmap
    ),
) -> TitleAutocompleteSelectionState:
    selected_anime_result = None
    if controller is not None:
        selected_anime_result = controller.find_anime_result_by_title(title)

    selected_cover_pixmap = load_cover_pixmap(selected_anime_result)
    if apply_selection is not None:
        apply_selection(selected_anime_result, selected_cover_pixmap)

    title_edit.setText(title)
    recompute()

    if controller is not None:
        controller.handle_title_selected(title)

    if selected_anime_result is None:
        log_info("ui", f"title_autocomplete_selected: title='{title}' anilist_id=None")
    else:
        log_info(
            "ui",
            "title_autocomplete_selected: "
            f"title='{title}' anilist_id={selected_anime_result.anilist_id}",
        )

    return TitleAutocompleteSelectionState(
        selected_anime_result=selected_anime_result,
        selected_cover_pixmap=selected_cover_pixmap,
    )
