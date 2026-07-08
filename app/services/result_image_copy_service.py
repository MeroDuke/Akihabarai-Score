from app.services.result_image_export_service import copy_result_card_image_to_clipboard
from app.widgets.copy_button_feedback import (
    COPY_RESULT_IMAGE_DEFAULT_TEXT,
    COPY_SUCCESS_TEXT,
    show_temporary_copy_feedback,
)


def copy_result_image_with_feedback(result_card, copy_img_btn) -> None:
    copy_result_card_image_to_clipboard(result_card)

    show_temporary_copy_feedback(
        copy_img_btn,
        COPY_SUCCESS_TEXT,
        COPY_RESULT_IMAGE_DEFAULT_TEXT,
    )
