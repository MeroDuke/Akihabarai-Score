from dataclasses import dataclass
from typing import Protocol

from PyQt6.QtWidgets import QLineEdit


class TitleSearchController(Protocol):
    def reset_online_state(self) -> None:
        ...


@dataclass(frozen=True)
class TitleInputResetState:
    selected_anime_result: object | None = None
    selected_cover_pixmap: object | None = None


def reset_title_input_state(
    title_edit: QLineEdit,
    title_search_controller: TitleSearchController | None,
) -> TitleInputResetState:
    title_edit.clear()

    if title_search_controller is not None:
        title_search_controller.reset_online_state()

    return TitleInputResetState()
