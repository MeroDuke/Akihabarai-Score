"""UI-independent state owned by one running application session."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.services.app_mode_service import AppModeState
from app.services.tier_card_edit_session_service import TierCardEditSessionState


@dataclass
class ApplicationSessionState:
    """Business state shared by desktop and future web presentation adapters."""

    title_input_mode: str
    dimension_states: list[object] = field(default_factory=list)
    profile_selection_memory: list[str | None] = field(default_factory=list)
    current_mix_needed: int = 1
    app_mode: AppModeState = field(default_factory=AppModeState)
    selected_anime_result: object | None = None
    latest_result: object | None = None
    tier_card_edit: TierCardEditSessionState = field(
        default_factory=TierCardEditSessionState
    )
