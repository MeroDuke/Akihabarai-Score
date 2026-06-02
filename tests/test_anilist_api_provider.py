import requests

from app.services.anilist_api_provider import search_anime_api


class DummyResponse:
    def __init__(self, payload, status_error=None):
        self._payload = payload
        self._status_error = status_error

    def raise_for_status(self):
        if self._status_error:
            raise self._status_error

    def json(self):
        return self._payload


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
