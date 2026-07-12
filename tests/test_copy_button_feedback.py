from PyQt6.QtWidgets import QPushButton

from app.widgets import copy_button_feedback as feedback


def test_copy_button_feedback_uses_hungarian_labels():
    assert feedback.COPY_SUCCESS_TEXT == "✔ Másolva!"
    assert feedback.COPY_DETAILS_SUCCESS_TEXT == "✔ Részletes adatok másolva!"
    assert feedback.COPY_DETAILS_DEFAULT_TEXT == "Részletes adatok másolása vágólapra"
    assert feedback.COPY_RESULT_IMAGE_DEFAULT_TEXT == "Eredmény képként másolása"
    assert feedback.COPY_TIER_IMAGE_DEFAULT_TEXT == "Tier lista képként másolása"


def test_show_temporary_copy_feedback_sets_success_text_and_schedules_restore(
    monkeypatch,
    qtbot,
):
    button = QPushButton("Eredmény képként másolása")
    qtbot.addWidget(button)
    scheduled = []

    def fake_single_shot(delay_ms, callback):
        scheduled.append((delay_ms, callback))

    monkeypatch.setattr(feedback.QTimer, "singleShot", fake_single_shot)

    feedback.show_temporary_copy_feedback(
        button,
        feedback.COPY_SUCCESS_TEXT,
        feedback.COPY_RESULT_IMAGE_DEFAULT_TEXT,
    )

    assert button.text() == "✔ Másolva!"
    assert len(scheduled) == 1
    assert scheduled[0][0] == feedback.COPY_FEEDBACK_DELAY_MS

    scheduled[0][1]()

    assert button.text() == "Eredmény képként másolása"
