from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QPushButton


COPY_FEEDBACK_DELAY_MS = 1500
COPY_SUCCESS_TEXT = "✔ Másolva!"
COPY_DETAILS_SUCCESS_TEXT = "✔ Részletes adatok másolva!"
COPY_DETAILS_DEFAULT_TEXT = "Részletes adatok másolása vágólapra"
COPY_RESULT_IMAGE_DEFAULT_TEXT = "Eredmény képként másolása"
COPY_TIER_IMAGE_DEFAULT_TEXT = "Tier lista képként másolása"


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
