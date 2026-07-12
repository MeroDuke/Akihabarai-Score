import app.services.result_image_copy_service as copy_service


def test_copy_result_image_with_feedback_copies_card_and_updates_button(
    monkeypatch,
):
    result_card = object()
    copy_img_btn = object()
    copy_calls = []
    feedback_calls = []

    monkeypatch.setattr(
        copy_service,
        "copy_result_card_image_to_clipboard",
        lambda widget: copy_calls.append(widget),
    )
    monkeypatch.setattr(
        copy_service,
        "show_temporary_copy_feedback",
        lambda button, success_text, default_text: feedback_calls.append(
            (button, success_text, default_text)
        ),
    )

    copy_service.copy_result_image_with_feedback(result_card, copy_img_btn)

    assert copy_calls == [result_card]
    assert feedback_calls == [
        (
            copy_img_btn,
            copy_service.COPY_SUCCESS_TEXT,
            copy_service.COPY_RESULT_IMAGE_DEFAULT_TEXT,
        ),
    ]
