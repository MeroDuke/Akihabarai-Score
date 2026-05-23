from app.core.models import AnimeSearchResult
from app.services import anilist_service
from app.services.anilist_service import (
    search_anime,
    search_anime_online,
    search_anime_titles,
    search_anime_titles_online,
)


def test_search_anime_titles_returns_all_mock_titles_without_query():
    results = search_anime_titles()

    assert "Re:Zero kara Hajimeru Isekai Seikatsu" in results
    assert "Sousou no Frieren" in results
    assert "Fullmetal Alchemist: Brotherhood" in results


def test_search_anime_titles_filters_case_insensitive_contains_matches():
    results = search_anime_titles("zero")

    assert "Re:Zero kara Hajimeru Isekai Seikatsu" in results
    assert "Re:Zero kara Hajimeru Isekai Seikatsu 2nd Season" in results
    assert "Re:Zero kara Hajimeru Isekai Seikatsu 3rd Season" in results
    assert "Sousou no Frieren" not in results


def test_search_anime_titles_returns_empty_list_when_no_match():
    assert search_anime_titles("not existing anime title") == []


def test_search_anime_returns_structured_results():
    results = search_anime("frieren")

    assert len(results) == 1
    result = results[0]

    assert isinstance(result, AnimeSearchResult)
    assert result.anilist_id == 154587
    assert result.title_romaji == "Sousou no Frieren"
    assert result.title_english == "Frieren: Beyond Journey’s End"
    assert result.title_native == "葬送のフリーレン"
    assert result.cover_url
    assert result.season_year == 2023


def test_search_anime_matches_english_title():
    results = search_anime("brotherhood")

    assert [result.title_romaji for result in results] == [
        "Fullmetal Alchemist: Brotherhood"
    ]


def test_search_anime_matches_native_title():
    results = search_anime("葬送")

    assert [result.title_romaji for result in results] == ["Sousou no Frieren"]


def test_search_anime_matches_season_year():
    results = search_anime("2024")

    assert [result.title_romaji for result in results] == [
        "Re:Zero kara Hajimeru Isekai Seikatsu 3rd Season"
    ]


def test_search_anime_titles_returns_romaji_titles_from_structured_results():
    assert search_anime_titles("frieren") == ["Sousou no Frieren"]


def test_search_anime_online_delegates_to_api_provider(monkeypatch):
    expected = [
        AnimeSearchResult(
            anilist_id=1,
            title_romaji="Online Anime",
            title_english=None,
            title_native=None,
            cover_url=None,
            season_year=2026,
        )
    ]

    def fake_search_anime_api(query):
        assert query == "online"
        return expected

    monkeypatch.setattr(anilist_service, "search_anime_api", fake_search_anime_api)

    assert search_anime_online("online") == expected


def test_search_anime_titles_online_returns_titles_from_api_provider(monkeypatch):
    online_results = [
        AnimeSearchResult(
            anilist_id=1,
            title_romaji="First Online Anime",
            title_english=None,
            title_native=None,
            cover_url=None,
            season_year=None,
        ),
        AnimeSearchResult(
            anilist_id=2,
            title_romaji="Second Online Anime",
            title_english=None,
            title_native=None,
            cover_url=None,
            season_year=None,
        ),
    ]

    monkeypatch.setattr(
        anilist_service,
        "search_anime_api",
        lambda query: online_results,
    )

    assert search_anime_titles_online("online") == [
        "First Online Anime",
        "Second Online Anime",
    ]
