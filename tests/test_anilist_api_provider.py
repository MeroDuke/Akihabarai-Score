import json

import pytest
import requests

from app.services.anilist_api_provider import search_anime_api, search_anime_api_response


class DummyResponse:
    def __init__(self, payload, status_error=None, status_code=200, headers=None):
        self._payload = payload
        self._status_error = status_error
        self.status_code = status_code
        self.headers = headers or {}

    def raise_for_status(self):
        if self._status_error:
            raise self._status_error

    def json(self):
        return self._payload


@pytest.mark.parametrize("status", [403, 500, 503])
def test_http_error_preserves_anilist_explanation_in_result_and_log(monkeypatch, status):
    message = "The AniList API has been temporarily disabled due to severe stability issues."
    response = requests.Response()
    response.status_code = status
    response.url = "https://graphql.anilist.co/"
    response._content = json.dumps({"errors": [{"message": message}], "data": None}).encode()
    logs = []
    monkeypatch.setattr("app.services.anilist_api_provider.requests.post", lambda *a, **k: response)
    monkeypatch.setattr("app.services.anilist_api_provider.log_warning", lambda *args: logs.append(args))

    result = search_anime_api_response("grand blue")

    assert not result.ok
    assert result.results == []
    assert result.error == "api_request_failed"
    assert str(status) in result.error_detail
    assert message in result.error_detail
    assert logs == [("anilist", f"api_request_failed: {result.error_detail}")]


@pytest.mark.parametrize("body", [
    b"<html>Forbidden</html>", b"", b"null", b"[]",
    b'{"errors": "unexpected"}',
    b'{"errors": [null, {}, {"message": 42}]}',
])
def test_http_error_without_graphql_message_keeps_http_diagnostic(monkeypatch, body):
    response = requests.Response()
    response.status_code = 403
    response.reason = "Forbidden"
    response.url = "https://graphql.anilist.co/"
    response._content = body
    monkeypatch.setattr("app.services.anilist_api_provider.requests.post", lambda *a, **k: response)

    result = search_anime_api_response("grand blue")

    assert result.error == "api_request_failed"
    assert result.error_detail == "403 Client Error: Forbidden for url: https://graphql.anilist.co/"


def test_http_error_messages_are_bounded_and_single_line(monkeypatch):
    response = requests.Response()
    response.status_code = 403
    response._content = json.dumps({"errors": [
        {"message": "first\nsecond"}, {"message": "x" * 1000},
        {"message": "third"}, {"message": "fourth"}, {"message": "fifth"},
        {"message": "sixth"},
    ]}).encode()
    monkeypatch.setattr("app.services.anilist_api_provider.requests.post", lambda *a, **k: response)

    result = search_anime_api_response("grand blue")

    assert "first second" in result.error_detail
    assert "\n" not in result.error_detail
    assert "x" * 500 in result.error_detail
    assert "x" * 501 not in result.error_detail
    assert "sixth" not in result.error_detail


def test_search_anime_api_maps_anilist_response(monkeypatch):
    payload = {
        "data": {
            "Page": {
                "media": [
                    {
                        "id": 21355,
                        "title": {
                            "romaji": "Re:Zero kara Hajimeru Isekai Seikatsu",
                            "english": "Re:ZERO -Starting Life in Another World-",
                            "native": "Re:ゼロから始める異世界生活",
                        },
                        "coverImage": {
                            "large": "https://example.test/large.jpg",
                            "extraLarge": "https://example.test/extra-large.jpg",
                        },
                        "seasonYear": 2016,
                    }
                ]
            }
        }
    }

    def fake_post(url, json, headers, timeout):
        assert url == "https://graphql.anilist.co"
        assert json["variables"]["search"] == "Re:Zero"
        assert json["variables"]["perPage"] == 10
        assert headers["User-Agent"].startswith("AkihabaraiScore/")
        assert timeout == 8
        return DummyResponse(payload)

    monkeypatch.setattr("app.services.anilist_api_provider.requests.post", fake_post)

    results = search_anime_api("Re:Zero")

    assert len(results) == 1
    assert results[0].anilist_id == 21355
    assert results[0].title_romaji == "Re:Zero kara Hajimeru Isekai Seikatsu"
    assert results[0].title_english == "Re:ZERO -Starting Life in Another World-"
    assert results[0].title_native == "Re:ゼロから始める異世界生活"
    assert results[0].cover_url == "https://example.test/extra-large.jpg"
    assert results[0].season_year == 2016


def test_search_anime_api_returns_empty_list_for_blank_query(monkeypatch):
    def fake_post(*args, **kwargs):
        raise AssertionError("requests.post should not be called for blank queries")

    monkeypatch.setattr("app.services.anilist_api_provider.requests.post", fake_post)

    assert search_anime_api("   ") == []


def test_search_anime_api_returns_empty_list_on_request_error(monkeypatch):
    monkeypatch.setattr(
        "app.services.anilist_api_provider.log_warning",
        lambda *args, **kwargs: None,
    )

    def fake_post(*args, **kwargs):
        raise requests.RequestException("network down")

    monkeypatch.setattr("app.services.anilist_api_provider.requests.post", fake_post)

    assert search_anime_api("Re:Zero") == []


def test_search_anime_api_skips_invalid_media_items(monkeypatch):
    payload = {
        "data": {
            "Page": {
                "media": [
                    {"id": "bad", "title": {"romaji": "Invalid"}},
                    {"id": 1, "title": {"english": "No romaji title"}},
                    {
                        "id": 2,
                        "title": {"romaji": "Valid Anime"},
                        "coverImage": {},
                        "seasonYear": None,
                    },
                ]
            }
        }
    }

    monkeypatch.setattr(
        "app.services.anilist_api_provider.requests.post",
        lambda *args, **kwargs: DummyResponse(payload),
    )

    results = search_anime_api("valid")

    assert len(results) == 1
    assert results[0].anilist_id == 2
    assert results[0].title_romaji == "Valid Anime"


def test_search_anime_api_response_reports_rate_limit(monkeypatch):
    monkeypatch.setattr(
        "app.services.anilist_api_provider.log_warning",
        lambda *args, **kwargs: None,
    )

    def fake_post(*args, **kwargs):
        return DummyResponse(
            {},
            status_code=429,
            headers={"Retry-After": "60"},
        )

    monkeypatch.setattr("app.services.anilist_api_provider.requests.post", fake_post)

    response = search_anime_api_response("Re:Zero")

    assert response.ok is False
    assert response.results == []
    assert response.error == "api_rate_limited"
    assert "retry_after=60" in response.error_detail




def test_search_anime_api_logs_rate_limit_headers(monkeypatch):
    log_messages = []

    monkeypatch.setattr(
        "app.services.anilist_api_provider.log_debug",
        lambda component, message: log_messages.append((component, message)),
    )

    payload = {
        "data": {
            "Page": {
                "media": []
            }
        }
    }

    def fake_post(*args, **kwargs):
        return DummyResponse(
            payload,
            headers={
                "X-RateLimit-Limit": "90",
                "X-RateLimit-Remaining": "42",
            },
        )

    monkeypatch.setattr(
        "app.services.anilist_api_provider.requests.post",
        fake_post,
    )

    response = search_anime_api_response("Re:Zero")

    assert response.ok is True
    assert response.results == []
    assert any(
        component == "anilist" and "X-RateLimit-Limit=90" in message
        for component, message in log_messages
    )
    assert any(
        component == "anilist" and "X-RateLimit-Remaining=42" in message
        for component, message in log_messages
    )
