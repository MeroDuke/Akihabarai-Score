import app.services.clipboard_service as clipboard_service
import app.services.result_render_service as render_service
import app.services.tier_image_export_service as tier_export_service
import app.services.release_page_service as release_page_service
from app.adapters import qt_desktop_adapter


def test_compatibility_services_delegate_to_desktop_adapter():
    assert (
        clipboard_service.copy_text_to_clipboard
        is qt_desktop_adapter.set_clipboard_text
    )
    assert (
        clipboard_service.copy_widget_as_pixmap
        is qt_desktop_adapter.render_widget_to_clipboard_pixmap
    )
    assert render_service.trim_pixmap is qt_desktop_adapter.trim_pixmap_background


def test_tier_export_service_has_no_direct_pyqt_dependency():
    assert "QApplication" not in tier_export_service.__dict__
    assert "PyQt6" not in tier_export_service.__dict__
    assert "QUrl" not in release_page_service.__dict__
