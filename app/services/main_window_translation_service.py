"""Qt presentation adapter for applying the active language to static widgets."""

from __future__ import annotations

from app.services.app_mode_service import APP_MODE_FREEHAND, APP_MODE_SCORED
from app.services.selection_id_service import set_identifier_labels
from app.widgets.title_input_mode_presenter import (
    TITLE_INPUT_MODE_OFFLINE,
    TITLE_INPUT_MODE_ONLINE,
)


def _set_combo_item_labels(combo, label_for_identifier) -> None:
    previous_block_state = combo.blockSignals(True)
    try:
        for index in range(combo.count()):
            identifier = combo.itemData(index)
            if not isinstance(identifier, str) or not identifier:
                identifier = combo.itemText(index)
            combo.setItemText(index, label_for_identifier(identifier))
    finally:
        combo.blockSignals(previous_block_state)


def _translated_or_fallback(translate, key: str, fallback: str) -> str:
    translated = translate(key)
    return fallback if translated == key else translated


def apply_main_window_static_translations(window, translate) -> None:
    language = window.localization_service.active_language

    window.left_box.setTitle(translate("panel.input.title"))
    window.result_panel.setTitle(translate("panel.result.title"))
    window.tier_panel.setTitle(translate("panel.tier.title"))

    top = window.top_inputs_panel
    top.title_label.setText(translate("input.title.label"))
    top.mix_label.setText(translate("input.profile_mix.label"))
    placeholder_key = (
        "input.title.placeholder.online"
        if window.title_input_mode == TITLE_INPUT_MODE_ONLINE
        else "input.title.placeholder.offline"
    )
    top.title_edit.setPlaceholderText(translate(placeholder_key))
    title_mode_key = (
        "title_mode.online.button"
        if window.title_input_mode == TITLE_INPUT_MODE_ONLINE
        else "title_mode.offline.button"
    )
    top.title_mode_btn.setText(translate(title_mode_key))
    mix_labels = {
        identifier: translate(f"profile_mix.{identifier}.label")
        for identifier in window.MIX_MODES
    }
    set_identifier_labels(top.mix_combo, mix_labels)
    _set_combo_item_labels(top.mix_combo, mix_labels.__getitem__)

    profile_panel = window.profile_mix_panel
    profile_panel.setTitle(translate("profile_config.title"))
    profile_panel.header_profile.setText(translate("profile_config.profile.header"))
    profile_panel.header_weight.setText(translate("profile_config.weight.header"))
    for index, label in enumerate(profile_panel.profile_labels, start=1):
        label.setText(translate("profile_config.row.label", index=index))
    profile_labels = {
        identifier: _translated_or_fallback(
            translate,
            f"profile.{identifier}",
            window.profile_labels.get(identifier, identifier),
        )
        for identifier in window.profile_names
    }
    profile_labels["—"] = translate("profile.inactive")
    for combo in profile_panel.profile_combos:
        set_identifier_labels(combo, profile_labels)
        _set_combo_item_labels(combo, profile_labels.__getitem__)

    dimensions_panel = window.dimensions_panel
    dimensions_panel.setTitle(translate("dimensions.title"))
    dimensions_panel.header_name.setText(translate("dimensions.name.header"))
    dimensions_panel.header_value.setText(translate("dimensions.score.header"))
    for state, label in zip(window.states, dimensions_panel.dimension_labels):
        state.label = _translated_or_fallback(
            translate,
            f"dimension.{state.name}",
            window.dimension_labels.get(state.name, state.display_name),
        )
        label.setText(state.label)

    actions = window.action_buttons_panel
    available_version = actions.version_btn.property("availableVersion")
    if isinstance(available_version, str) and available_version:
        actions.version_btn.setText(
            translate("version.update_available", version=available_version)
        )
    else:
        actions.version_btn.setText(
            translate(
                "version.current",
                version=f"v{window.app_version.lstrip('v')}",
            )
        )
    actions.reset_btn.setText(translate("action.reset"))
    if window.editing_tier_entry is None:
        actions.add_tier_btn.setText(translate("action.add_to_tier"))
    else:
        actions.add_tier_btn.setText(translate("action.save_edit"))
    actions.cancel_edit_btn.setText(translate("action.cancel_edit"))

    mode = window.current_mode
    actions.mode_btn.setText(translate(f"app_mode.{mode}.label"))
    tooltip_key = (
        "app_mode.scored.switch_tooltip"
        if mode == APP_MODE_SCORED
        else "app_mode.freehand.switch_tooltip"
    )
    actions.mode_btn.setToolTip(translate(tooltip_key))

    if language == "hu":
        actions.language_btn.setText(translate("language.switch.to_en"))
        actions.language_btn.setToolTip(
            translate("language.switch.tooltip.to_en")
        )
    else:
        actions.language_btn.setText(translate("language.switch.to_hu"))
        actions.language_btn.setToolTip(
            translate("language.switch.tooltip.to_hu")
        )

    result_panel = window.result_panel
    result_panel.copy_img_btn.setText(translate("copy.result_image.action"))
    result_panel.copy_btn.setText(translate("copy.details.action"))
    for index, key in enumerate(
        (
            "result.table.dimension",
            "result.table.score",
            "result.table.relevance",
            "result.table.contribution",
        )
    ):
        header_item = result_panel.table.horizontalHeaderItem(index)
        if header_item is not None:
            header_item.setText(translate(key))
    for row, state in enumerate(window.states):
        item = result_panel.table.item(row, 0)
        if item is not None:
            item.setText(state.display_name)
            item.setToolTip(state.display_name)
    if window.latest_result is not None:
        result_panel.tier_label.setText(
            translate("result.tier_value", tier=window.latest_result.tier)
        )

    tier_panel = window.tier_panel
    tier_panel.flip_all_tier_cards_btn.setText(translate("tier.flip_all.action"))
    tier_panel.clear_all_tier_cards_btn.setText(translate("tier.clear_all.action"))
    tier_panel.copy_tier_btn.setText(translate("copy.tier_image.action"))
    window.tier_board.retranslate()
