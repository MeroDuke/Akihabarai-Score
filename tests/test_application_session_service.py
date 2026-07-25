import app.services.application_session_service as application_session_service
from app.services.app_mode_service import APP_MODE_SCORED
from app.services.application_session_service import ApplicationSessionState


def test_application_session_service_has_no_qt_dependency():
    assert "PyQt6" not in application_session_service.__dict__


def test_application_session_state_owns_ui_independent_runtime_defaults():
    state = ApplicationSessionState(title_input_mode="offline")

    assert state.title_input_mode == "offline"
    assert state.dimension_states == []
    assert state.profile_selection_memory == []
    assert state.current_mix_needed == 1
    assert state.app_mode.mode == APP_MODE_SCORED
    assert state.selected_anime_result is None
    assert state.latest_result is None
    assert state.tier_card_edit.is_active is False


def test_application_session_state_mutable_collections_are_not_shared():
    first = ApplicationSessionState(title_input_mode="offline")
    second = ApplicationSessionState(title_input_mode="offline")

    first.dimension_states.append("story")
    first.profile_selection_memory.append("Balanced")

    assert second.dimension_states == []
    assert second.profile_selection_memory == []
