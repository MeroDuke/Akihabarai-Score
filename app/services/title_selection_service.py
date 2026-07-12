from dataclasses import dataclass
from typing import Protocol


class SelectedAnimeResult(Protocol):
    title_romaji: str


@dataclass(frozen=True)
class TitleSelectionState:
    selected_anime_result: SelectedAnimeResult | None
    selected_cover_pixmap: object | None


def clear_title_selection_if_text_changed(
    text: str,
    selected_anime_result: SelectedAnimeResult | None,
    selected_cover_pixmap: object | None,
) -> TitleSelectionState:
    if (
        selected_anime_result is not None
        and text != selected_anime_result.title_romaji
    ):
        return TitleSelectionState(
            selected_anime_result=None,
            selected_cover_pixmap=None,
        )

    return TitleSelectionState(
        selected_anime_result=selected_anime_result,
        selected_cover_pixmap=selected_cover_pixmap,
    )
