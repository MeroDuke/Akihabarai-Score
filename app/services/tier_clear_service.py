from collections.abc import Callable

from app.logger import log_info


def clear_all_tier_cards_if_confirmed(
    tier_board,
    ask_confirmation: Callable[[], bool],
    update_tier_buttons_state: Callable[[], None],
    finish_editing: Callable[[], None] | None = None,
) -> bool:
    if tier_board.saved_entry_count() <= 0:
        log_info("core", "clear_entries_skipped: count=0")
        update_tier_buttons_state()
        return False

    confirmed = ask_confirmation()
    decision = "yes" if confirmed else "no"
    log_info("core", f"clear_confirmation_received: decision='{decision}'")

    if not confirmed:
        log_info("core", "clear_entries_cancelled")
        return False

    if getattr(tier_board, "editing_entry", None) is not None:
        if finish_editing is not None:
            finish_editing()

    removed_count = tier_board.clear_all_saved_entries()
    log_info("core", f"clear_entries_completed: count={removed_count}")
    update_tier_buttons_state()
    return True
