from app.services.details_export_service import copy_export_text


def test_copy_export_text_is_separate_from_content_generation():
    copied = []
    copy_export_text("already rendered", copy_text_func=copied.append)
    assert copied == ["already rendered"]
