from app.core.models import AnimeSearchResult
from app.services.title_selection_service import clear_title_selection_if_text_changed


def _anime_result(title: str) -> AnimeSearchResult:
    return AnimeSearchResult(
        anilist_id=1,
        title_romaji=title,
        title_english=None,
        title_native=None,
        cover_url=None,
        season_year=None,
    )


def test_clear_title_selection_if_text_changed_clears_runtime_selection():
    selected_anime_result = _anime_result("Sousou no Frieren")
    selected_cover_pixmap = object()

    state = clear_title_selection_if_text_changed(
        "Manual title",
        selected_anime_result,
        selected_cover_pixmap,
    )

    assert state.selected_anime_result is None
    assert state.selected_cover_pixmap is None


def test_clear_title_selection_if_text_changed_keeps_matching_selection():
    selected_anime_result = _anime_result("Sousou no Frieren")
    selected_cover_pixmap = object()

    state = clear_title_selection_if_text_changed(
        "Sousou no Frieren",
        selected_anime_result,
        selected_cover_pixmap,
    )

    assert state.selected_anime_result is selected_anime_result
    assert state.selected_cover_pixmap is selected_cover_pixmap


def test_clear_title_selection_if_text_changed_allows_missing_selection():
    selected_cover_pixmap = object()

    state = clear_title_selection_if_text_changed(
        "Manual title",
        None,
        selected_cover_pixmap,
    )

    assert state.selected_anime_result is None
    assert state.selected_cover_pixmap is selected_cover_pixmap
