from dataclasses import dataclass, replace


APP_MODE_SCORED = "scored"
APP_MODE_FREEHAND = "freehand"
DEFAULT_APP_MODE = APP_MODE_SCORED

SCORED_LAYOUT_STRETCHES = (4, 2, 3)
FREEHAND_LAYOUT_STRETCHES = (4, 0, 5)


@dataclass(frozen=True)
class ScoredEditorSnapshot:
    title: str
    title_input_mode: str
    selected_anime_result: object | None
    selected_cover_image: object | None


@dataclass(frozen=True)
class AppModeState:
    mode: str = DEFAULT_APP_MODE
    scored_editor_snapshot: ScoredEditorSnapshot | None = None


@dataclass(frozen=True)
class AppModeCapabilities:
    scoring_enabled: bool
    drag_enabled: bool
    layout_stretches: tuple[int, int, int]


@dataclass(frozen=True)
class AppModeTransition:
    state: AppModeState
    editor_to_restore: ScoredEditorSnapshot | None


def build_app_mode_capabilities(mode: str) -> AppModeCapabilities:
    scoring_enabled = mode == APP_MODE_SCORED
    return AppModeCapabilities(
        scoring_enabled=scoring_enabled,
        drag_enabled=not scoring_enabled,
        layout_stretches=(
            SCORED_LAYOUT_STRETCHES
            if scoring_enabled
            else FREEHAND_LAYOUT_STRETCHES
        ),
    )


def set_app_mode(state: AppModeState, mode: str) -> AppModeState:
    if mode not in (APP_MODE_SCORED, APP_MODE_FREEHAND):
        raise ValueError(f"Unknown app mode: {mode}")
    return replace(state, mode=mode)


def toggle_app_mode(
    state: AppModeState,
    *,
    current_editor: ScoredEditorSnapshot | None = None,
) -> AppModeTransition:
    if state.mode == APP_MODE_SCORED:
        return AppModeTransition(
            state=AppModeState(
                mode=APP_MODE_FREEHAND,
                scored_editor_snapshot=current_editor,
            ),
            editor_to_restore=None,
        )

    return AppModeTransition(
        state=AppModeState(
            mode=APP_MODE_SCORED,
            scored_editor_snapshot=state.scored_editor_snapshot,
        ),
        editor_to_restore=state.scored_editor_snapshot,
    )


def should_reuse_scored_result(
    state: AppModeState,
    *,
    title: str,
    result_title: str,
) -> bool:
    snapshot = state.scored_editor_snapshot
    cleaned_title = title.strip()
    return (
        state.mode == APP_MODE_FREEHAND
        and snapshot is not None
        and bool(cleaned_title)
        and cleaned_title == snapshot.title.strip()
        and cleaned_title == result_title.strip()
    )
