from app.services.result_image_export_service import copy_result_card_image_to_clipboard
from app.widgets.copy_button_feedback import (
    show_localized_copy_feedback,
)


def copy_result_image_with_feedback(result_card, copy_img_btn) -> None:
    log_info("clipboard", "copy_result_image_started")
    try:
        copy_result_card_image_to_clipboard(result_card)
    except Exception as exc:
        log_error("clipboard", f"copy_result_image_failed: {type(exc).__name__}")
        raise

    show_localized_copy_feedback(
        copy_img_btn,
        "copy.success",
        "copy.result_image.action",
    )
    log_info("clipboard", "copy_result_image_completed")
from app.logger import log_error, log_info
