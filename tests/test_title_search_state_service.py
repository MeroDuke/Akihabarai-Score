from app.services.title_search_state_service import (
    TitleSearchState,
    finish_active_query,
    queue_or_activate_query,
    reset_title_search_state,
    should_apply_search_result,
    with_manual_query,
    with_pending_query,
)


def test_state_is_runtime_value_data_without_qt_objects():
    state = TitleSearchState(pending_query="86", active_query="86")
    assert state.pending_query == "86"
    assert not hasattr(state, "timer")
    assert not hasattr(state, "thread")


def test_query_transitions_are_immutable_and_normalized():
    initial = reset_title_search_state()
    pending = with_pending_query(initial, "  Frieren ")
    manual = with_manual_query(pending, "  Fri ")
    active, should_start = queue_or_activate_query(
        manual, " Frieren ", search_running=False
    )

    assert initial == TitleSearchState()
    assert pending.pending_query == "Frieren"
    assert manual.last_manual_online_query == "Fri"
    assert active.active_query == "Frieren"
    assert should_start is True


def test_running_search_queues_latest_query_and_finish_releases_it():
    state, should_start = queue_or_activate_query(
        TitleSearchState(active_query="86"),
        "86 Eighty-Six",
        search_running=True,
    )
    finished, queued = finish_active_query(state)
    assert should_start is False
    assert queued == "86 Eighty-Six"
    assert finished.active_query == ""
    assert finished.queued_query is None


def test_stale_result_comparison_is_case_and_whitespace_insensitive():
    state = TitleSearchState(active_query="Frieren")
    assert should_apply_search_result(state, " frieren ")
    assert not should_apply_search_result(state, "86")
