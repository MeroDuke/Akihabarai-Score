from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QPushButton
from app.services.localization_service import translate


COPY_FEEDBACK_DELAY_MS = 1500
COPY_SUCCESS_TEXT = translate("copy.success")
COPY_DETAILS_SUCCESS_TEXT = translate("copy.details.success")
COPY_DETAILS_DEFAULT_TEXT = translate("copy.details.action")
COPY_RESULT_IMAGE_DEFAULT_TEXT = translate("copy.result_image.action")
COPY_TIER_IMAGE_DEFAULT_TEXT = translate("copy.tier_image.action")


def show_temporary_copy_feedback(
    button: QPushButton,
    success_text: str,
    default_text: str,
) -> None:
    button.setText(success_text)
    QTimer.singleShot(
        COPY_FEEDBACK_DELAY_MS,
        lambda: button.setText(default_text),
    )


def show_localized_copy_feedback(
    button: QPushButton,
    success_key: str,
    default_key: str,
    *,
    translate_func=translate,
) -> None:
    button.setText(translate_func(success_key))
    QTimer.singleShot(
        COPY_FEEDBACK_DELAY_MS,
        lambda: button.setText(translate_func(default_key)),
    )
