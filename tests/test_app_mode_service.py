import pytest

from app.services.app_mode_service import (
    APP_MODE_FREEHAND,
    APP_MODE_SCORED,
    AppModeState,
    ScoredEditorSnapshot,
    build_app_mode_capabilities,
    set_app_mode,
    toggle_app_mode,
)


def _editor_snapshot():
    return ScoredEditorSnapshot(
        title="Cowboy Bebop",
        title_input_mode="online",
        selected_anime_result="anime",
        selected_cover_image="cover",
    )


def test_scored_capabilities_enable_scoring_and_use_scored_layout():
    capabilities = build_app_mode_capabilities(APP_MODE_SCORED)

    assert capabilities.scoring_enabled is True
    assert capabilities.drag_enabled is False
    assert capabilities.layout_stretches == (4, 2, 3)


def test_freehand_capabilities_enable_drag_and_use_freehand_layout():
    capabilities = build_app_mode_capabilities(APP_MODE_FREEHAND)

    assert capabilities.scoring_enabled is False
    assert capabilities.drag_enabled is True
    assert capabilities.layout_stretches == (4, 0, 5)


def test_leaving_scored_mode_preserves_editor_snapshot():
    snapshot = _editor_snapshot()

    transition = toggle_app_mode(
        AppModeState(mode=APP_MODE_SCORED),
        current_editor=snapshot,
    )

    assert transition.state.mode == APP_MODE_FREEHAND
    assert transition.state.scored_editor_snapshot is snapshot
    assert transition.editor_to_restore is None


def test_returning_to_scored_mode_exposes_preserved_editor_for_restore():
    snapshot = _editor_snapshot()
    state = AppModeState(
        mode=APP_MODE_FREEHAND,
        scored_editor_snapshot=snapshot,
    )

    transition = toggle_app_mode(state)

    assert transition.state.mode == APP_MODE_SCORED
    assert transition.state.scored_editor_snapshot is snapshot
    assert transition.editor_to_restore is snapshot


def test_mode_transition_does_not_mutate_previous_state():
    state = AppModeState(mode=APP_MODE_SCORED)

    transition = toggle_app_mode(
        state,
        current_editor=_editor_snapshot(),
    )

    assert state == AppModeState(mode=APP_MODE_SCORED)
    assert transition.state is not state


def test_set_app_mode_preserves_snapshot_and_rejects_unknown_mode():
    snapshot = _editor_snapshot()
    state = AppModeState(scored_editor_snapshot=snapshot)

    updated = set_app_mode(state, APP_MODE_FREEHAND)

    assert updated == AppModeState(
        mode=APP_MODE_FREEHAND,
        scored_editor_snapshot=snapshot,
    )
    with pytest.raises(ValueError, match="Unknown app mode"):
        set_app_mode(state, "invalid")
