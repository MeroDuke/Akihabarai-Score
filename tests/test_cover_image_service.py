import pytest
import requests
from PyQt6.QtGui import QImage

import app.services.cover_image_service as cover_service


def _png_bytes() -> bytes:
    image = QImage(2, 2, QImage.Format.Format_RGB32)
    image.fill(0xFF0000)

    from PyQt6.QtCore import QByteArray, QBuffer, QIODevice

    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    buffer.close()
    return bytes(data)


class DummyResponse:
    def __init__(self, *, content=b"", headers=None, raise_error=None, status_code=200):
        self.content = content
        self.headers = headers or {}
        self._raise_error = raise_error
        self.status_code = status_code

    def raise_for_status(self):
        if self._raise_error is not None:
            raise self._raise_error


def assert_anilist_user_agent(headers):
    assert headers["User-Agent"].startswith("AkihabaraiScore/")


@pytest.fixture
def log_messages(monkeypatch):
    messages = []
    monkeypatch.setattr(
        cover_service,
        "log_debug",
        lambda component, message: messages.append((component, message)),
    )
    monkeypatch.setattr(
        cover_service,
        "log_warning",
        lambda component, message: messages.append((component, message)),
    )
    return messages


def test_load_cover_pixmap_from_url_returns_pixmap_without_persistence(monkeypatch, log_messages):
    monkeypatch.setattr(
        cover_service.requests,
        "get",
        lambda url, headers, timeout: (
            assert_anilist_user_agent(headers)
            or DummyResponse(
                content=_png_bytes(),
                headers={"Content-Type": "image/png"},
            )
        ),
    )

    response = cover_service.load_cover_pixmap_from_url("https://example.test/cover.png")

    assert response.ok is True
    assert response.error is None
    assert response.pixmap is not None
    assert response.pixmap.width() == 2
    assert response.pixmap.height() == 2
    assert any("cover_download_started" in message for _, message in log_messages)
    assert any("cover_download_completed" in message for _, message in log_messages)


def test_load_cover_pixmap_from_url_rejects_empty_url(log_messages):
    response = cover_service.load_cover_pixmap_from_url("   ")

    assert response.ok is False
    assert response.pixmap is None
    assert response.error == "cover_url_missing"
    assert any("cover_url_missing" in message for _, message in log_messages)


def test_load_cover_pixmap_from_url_reports_timeout(monkeypatch, log_messages):
    def raise_timeout(url, headers, timeout):
        assert_anilist_user_agent(headers)
        raise requests.Timeout("simulated timeout")

    monkeypatch.setattr(cover_service.requests, "get", raise_timeout)

    response = cover_service.load_cover_pixmap_from_url("https://example.test/cover.png")

    assert response.ok is False
    assert response.pixmap is None
    assert response.error == "cover_request_timeout"
    assert "simulated timeout" in response.error_detail
    assert any("cover_request_timeout" in message for _, message in log_messages)


def test_load_cover_pixmap_from_url_reports_request_failure(monkeypatch, log_messages):
    def raise_request_error(url, headers, timeout):
        assert_anilist_user_agent(headers)
        raise requests.RequestException("simulated network error")

    monkeypatch.setattr(cover_service.requests, "get", raise_request_error)

    response = cover_service.load_cover_pixmap_from_url("https://example.test/cover.png")

    assert response.ok is False
    assert response.pixmap is None
    assert response.error == "cover_request_failed"
    assert "simulated network error" in response.error_detail


def test_load_cover_pixmap_from_url_reports_rate_limit(monkeypatch, log_messages):
    monkeypatch.setattr(
        cover_service.requests,
        "get",
        lambda url, headers, timeout: (
            assert_anilist_user_agent(headers)
            or DummyResponse(
                status_code=429,
                headers={"Retry-After": "60"},
            )
        ),
    )

    response = cover_service.load_cover_pixmap_from_url("https://example.test/cover.png")

    assert response.ok is False
    assert response.pixmap is None
    assert response.error == "cover_rate_limited"
    assert "retry_after=60" in response.error_detail
    assert any("cover_rate_limited" in message for _, message in log_messages)


def test_load_cover_pixmap_from_url_rejects_non_image_content_type(monkeypatch, log_messages):
    monkeypatch.setattr(
        cover_service.requests,
        "get",
        lambda url, headers, timeout: (
            assert_anilist_user_agent(headers)
            or DummyResponse(
                content=b"not an image",
                headers={"Content-Type": "text/html"},
            )
        ),
    )

    response = cover_service.load_cover_pixmap_from_url("https://example.test/cover")

    assert response.ok is False
    assert response.pixmap is None
    assert response.error == "cover_response_not_image"


def test_load_cover_pixmap_from_url_reports_decode_failure(monkeypatch, log_messages):
    monkeypatch.setattr(
        cover_service.requests,
        "get",
        lambda url, headers, timeout: (
            assert_anilist_user_agent(headers)
            or DummyResponse(
                content=b"not an image",
                headers={"Content-Type": "image/png"},
            )
        ),
    )

    response = cover_service.load_cover_pixmap_from_url("https://example.test/broken.png")

    assert response.ok is False
    assert response.pixmap is None
    assert response.error == "cover_pixmap_decode_failed"
