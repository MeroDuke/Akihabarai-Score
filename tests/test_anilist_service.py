from app.services.anilist_service import search_anime_titles


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


def test_search_anime_titles_strips_query_whitespace():
    results = search_anime_titles("  frieren  ")

    assert results == ["Sousou no Frieren"]
