from __future__ import annotations

from collections.abc import Callable

from app.services.details_copy_service import copy_details_with_feedback
from app.services.release_page_service import open_release_page
from app.services.result_image_copy_service import copy_result_image_with_feedback
from app.services.tier_clear_service import clear_all_tier_cards_if_confirmed
from app.services.tier_flip_service import flip_all_tier_cards_if_available
from app.services.tier_image_copy_service import copy_tier_image_with_feedback
from app.services.version_update_workflow_service import (
    apply_update_check_to_version_button,
)


def set_add_tier_button_enabled(add_tier_btn, title: str):
    add_tier_btn.setEnabled(bool(title.strip()))


def open_releases_page_from_button(
    *,
    releases_url: str,
    open_url_func: Callable,
):
    open_release_page(releases_url, open_url_func)


def check_for_updates_from_button(
    *,
    version_btn,
    app_version: str,
    default_button_text: str,
    check_for_update_func: Callable,
):
    apply_update_check_to_version_button(
        version_btn=version_btn,
        app_version=app_version,
        default_button_text=default_button_text,
        check_for_update_func=check_for_update_func,
    )


def update_tier_panel_buttons(tier_panel):
    tier_panel.update_buttons_state()


def flip_tier_cards_from_button(
    *,
    tier_board,
    update_tier_buttons_state: Callable[[], None],
):
    flip_all_tier_cards_if_available(
        tier_board,
        update_tier_buttons_state,
    )


def clear_tier_cards_from_button(
    *,
    tier_board,
    ask_confirmation: Callable[[], bool],
    update_tier_buttons_state: Callable[[], None],
    finish_editing: Callable[[], None] | None = None,
):
    clear_kwargs = dict(
        ask_confirmation=ask_confirmation,
        update_tier_buttons_state=update_tier_buttons_state,
    )
    if finish_editing is not None:
        clear_kwargs["finish_editing"] = finish_editing
    clear_all_tier_cards_if_confirmed(tier_board, **clear_kwargs)


def update_result_table_from_main(
    *,
    result_panel,
    states,
    relevances,
    contributions,
):
    result_panel.update_table(states, relevances, contributions)


def copy_details_from_button(
    *,
    profiles,
    profile_combos,
    weight_spins,
    mix_mode,
    mix_modes,
    states,
    tier_thresholds,
    title,
    copy_btn,
):
    copy_details_with_feedback(
        profiles=profiles,
        profile_combos=profile_combos,
        weight_spins=weight_spins,
        mix_mode=mix_mode,
        mix_modes=mix_modes,
        states=states,
        tier_thresholds=tier_thresholds,
        title=title,
        copy_btn=copy_btn,
    )


def copy_result_image_from_button(
    *,
    result_card,
    copy_img_btn,
):
    copy_result_image_with_feedback(
        result_card,
        copy_img_btn,
    )


def copy_tier_image_from_button(
    *,
    parent,
    tier_board,
    copy_tier_btn,
    update_tier_buttons_state: Callable[[], None],
):
    copy_tier_image_with_feedback(
        parent=parent,
        tier_board=tier_board,
        copy_tier_btn=copy_tier_btn,
        update_tier_buttons_state=update_tier_buttons_state,
    )
