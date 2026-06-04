import json
import urllib.error

import pytest

from app.services import update_check_service as service


def test_normalize_version_accepts_plain_semver():
    assert service.normalize_version("0.14.1") == "0.14.1"


def test_normalize_version_accepts_v_prefixed_semver():
    assert service.normalize_version("v0.14.1") == "0.14.1"


@pytest.mark.parametrize(
    "version",
    [
        "",
        "   ",
        "0.14",
        "0.14.1.2",
        "v0.14.x",
        "version-0.14.1",
    ],
)
def test_normalize_version_rejects_invalid_versions(version):
    with pytest.raises(ValueError):
        service.normalize_version(version)


def test_version_to_tuple_converts_version_to_integer_tuple():
    assert service.version_to_tuple("v0.14.1") == (0, 14, 1)


def test_version_to_tuple_compares_versions_numerically():
    assert service.version_to_tuple("v0.10.0") > service.version_to_tuple("v0.9.0")
    assert service.version_to_tuple("v1.0.0") > service.version_to_tuple("v0.99.99")


def test_format_version_returns_v_prefixed_version():
    assert service.format_version("0.14.1") == "v0.14.1"
    assert service.format_version("v0.14.1") == "v0.14.1"


def test_check_for_update_returns_update_available_when_latest_is_newer(monkeypatch):
    monkeypatch.setattr(
        service,
        "fetch_latest_release_version",
        lambda: "v0.15.0",
    )

    result = service.check_for_update("0.14.1")

    assert result.ok is True
    assert result.update_available is True
    assert result.local_version == "v0.14.1"
    assert result.latest_version == "v0.15.0"
    assert result.error == ""


def test_check_for_update_returns_no_update_when_versions_match(monkeypatch):
    monkeypatch.setattr(
        service,
        "fetch_latest_release_version",
        lambda: "v0.14.1",
    )

    result = service.check_for_update("0.14.1")

    assert result.ok is True
    assert result.update_available is False
    assert result.local_version == "v0.14.1"
    assert result.latest_version == "v0.14.1"
    assert result.error == ""


def test_check_for_update_returns_no_update_when_latest_is_older(monkeypatch):
    monkeypatch.setattr(
        service,
        "fetch_latest_release_version",
        lambda: "v0.13.9",
    )

    result = service.check_for_update("0.14.1")

    assert result.ok is True
    assert result.update_available is False
    assert result.local_version == "v0.14.1"
    assert result.latest_version == "v0.13.9"
    assert result.error == ""


def test_check_for_update_returns_error_for_invalid_local_version(monkeypatch):
    monkeypatch.setattr(
        service,
        "fetch_latest_release_version",
        lambda: "v0.15.0",
    )

    result = service.check_for_update("invalid")

    assert result.ok is False
    assert result.update_available is False
    assert result.local_version == ""
    assert result.latest_version == ""
    assert result.error


def test_check_for_update_returns_error_when_fetch_fails(monkeypatch):
    def raise_url_error():
        raise urllib.error.URLError("network unavailable")

    monkeypatch.setattr(service, "fetch_latest_release_version", raise_url_error)

    result = service.check_for_update("0.14.1")

    assert result.ok is False
    assert result.update_available is False
    assert result.error


def test_check_for_update_returns_error_when_latest_version_is_invalid(monkeypatch):
    monkeypatch.setattr(
        service,
        "fetch_latest_release_version",
        lambda: "not-a-version",
    )

    result = service.check_for_update("0.14.1")

    assert result.ok is False
    assert result.update_available is False
    assert result.error


def test_fetch_latest_release_version_uses_github_response_tag_name(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return json.dumps({"tag_name": "v0.15.0"}).encode("utf-8")

    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(service.urllib.request, "urlopen", fake_urlopen)

    latest_version = service.fetch_latest_release_version(timeout_seconds=3)

    assert latest_version == "v0.15.0"
    assert captured["timeout"] == 3
    assert captured["request"].full_url == service.GITHUB_LATEST_RELEASE_API_URL
    assert captured["request"].headers["Accept"] == "application/vnd.github+json"
    assert captured["request"].headers["User-agent"] == service.APP_USER_AGENT


def test_fetch_latest_release_version_returns_error_for_missing_tag_name(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def read(self):
            return json.dumps({}).encode("utf-8")

    monkeypatch.setattr(
        service.urllib.request,
        "urlopen",
        lambda request, timeout: FakeResponse(),
    )

    with pytest.raises(ValueError):
        service.fetch_latest_release_version()
