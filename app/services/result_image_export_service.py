from app.services.clipboard_service import copy_widget_as_pixmap


def copy_result_card_image_to_clipboard(result_card):
    return copy_widget_as_pixmap(result_card)
