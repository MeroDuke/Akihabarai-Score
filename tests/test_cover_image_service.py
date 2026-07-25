import pytest
import requests
from PyQt6.QtCore import QByteArray, QBuffer, QIODevice
from PyQt6.QtGui import QImage

import app.services.cover_image_data_service as data_service
import app.services.cover_image_qt_adapter as qt_adapter
from app.core.models import AnimeSearchResult

pytestmark = pytest.mark.usefixtures("qapp")


class DummyResponse:
    def __init__(self, *, content=b"", headers=None, status_code=200, error=None):
        self.content = content
        self.headers = headers or {}
        self.status_code = status_code
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise self.error


def _png_bytes() -> bytes:
    image = QImage(2, 2, QImage.Format.Format_RGB32)
    image.fill(0xFF0000)
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    buffer.close()
    return bytes(data)


def _result(cover_url="https://example.test/cover.png"):
    return AnimeSearchResult(1, "86 Eighty-Six", None, None, cover_url, 2021)


def test_download_returns_bytes_and_explicit_user_agent(monkeypatch):
    observed = {}

    def get(url, headers, timeout):
        observed.update(url=url, headers=headers, timeout=timeout)
        return DummyResponse(content=_png_bytes(), headers={"Content-Type": "image/png"})

    monkeypatch.setattr(data_service.requests, "get", get)
    response = data_service.download_cover_image_data("https://example.test/cover.png")

    assert response.ok
    assert response.image_bytes == _png_bytes()
    assert observed["headers"]["User-Agent"].startswith("AkihabaraiScore/")
    assert "PyQt" not in data_service.__dict__


@pytest.mark.parametrize(
    ("url", "response", "error"),
    [
        (" ", None, "cover_url_missing"),
        (
            "https://example.test/cover",
            DummyResponse(content=b"x", headers={"Content-Type": "text/html"}),
            "cover_response_not_image",
        ),
        (
            "https://example.test/cover",
            DummyResponse(status_code=429, headers={"Retry-After": "60"}),
            "cover_rate_limited",
        ),
        ("https://example.test/cover", DummyResponse(), "cover_response_empty"),
    ],
)
def test_download_rejects_invalid_responses(monkeypatch, url, response, error):
    if response is not None:
        monkeypatch.setattr(data_service.requests, "get", lambda *args, **kwargs: response)
    result = data_service.download_cover_image_data(url)
    assert not result.ok
    assert result.image_bytes is None
    assert result.error == error
    if error == "cover_rate_limited":
        assert "retry_after=60" in result.error_detail


@pytest.mark.parametrize(
    ("exception", "error"),
    [
        (requests.Timeout("timeout"), "cover_request_timeout"),
        (requests.RequestException("network"), "cover_request_failed"),
    ],
)
def test_download_reports_network_errors(monkeypatch, exception, error):
    def fail(*args, **kwargs):
        raise exception

    monkeypatch.setattr(data_service.requests, "get", fail)
    result = data_service.download_cover_image_data("https://example.test/cover.png")
    assert result.error == error


def test_qt_adapter_decodes_bytes_without_owning_network_policy():
    response = qt_adapter.decode_cover_pixmap(
        data_service.CoverImageDataResponse(_png_bytes(), "image/png")
    )
    assert response.ok
    assert response.pixmap.width() == 2
    assert response.pixmap.height() == 2


def test_qt_adapter_reports_decode_failure():
    response = qt_adapter.decode_cover_pixmap(
        data_service.CoverImageDataResponse(b"broken", "image/png")
    )
    assert response.error == "cover_pixmap_decode_failed"


def test_selected_preview_stays_empty_without_selection_or_cover(monkeypatch):
    assert qt_adapter.load_selected_cover_preview_pixmap(None) is None
    assert qt_adapter.load_selected_cover_preview_pixmap(_result(None)) is None


def test_selected_preview_uses_runtime_pixmap(monkeypatch):
    expected = object()
    monkeypatch.setattr(
        qt_adapter,
        "load_cover_pixmap_from_url",
        lambda url: qt_adapter.CoverPixmapResponse(expected),
    )
    assert qt_adapter.load_selected_cover_preview_pixmap(_result()) is expected
