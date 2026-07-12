from app.services import result_image_export_service


def test_copy_result_card_image_to_clipboard_copies_result_card(monkeypatch):
    result_card = object()
    pixmap = object()
    calls = []
    monkeypatch.setattr(
        result_image_export_service,
        "copy_widget_as_pixmap",
        lambda widget: calls.append(widget) or pixmap,
    )

    copied_pixmap = result_image_export_service.copy_result_card_image_to_clipboard(
        result_card
    )

    assert copied_pixmap is pixmap
    assert calls == [result_card]
