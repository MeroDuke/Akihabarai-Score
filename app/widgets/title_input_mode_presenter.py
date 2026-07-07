from dataclasses import dataclass


TITLE_INPUT_MODE_OFFLINE = "offline"
TITLE_INPUT_MODE_ONLINE = "online"
TITLE_MODE_BUTTON_OFFLINE_TEXT = "✏ Offline"
TITLE_MODE_BUTTON_ONLINE_TEXT = "🌐 Online"


@dataclass(frozen=True)
class TitleInputModePresentation:
    mode: str
    placeholder: str
    button_text: str
    autocomplete_enabled: bool


def build_title_input_mode_presentation(
    mode: str,
    offline_placeholder: str,
    online_placeholder: str,
) -> TitleInputModePresentation:
    if mode == TITLE_INPUT_MODE_ONLINE:
        return TitleInputModePresentation(
            mode=TITLE_INPUT_MODE_ONLINE,
            placeholder=online_placeholder,
            button_text=TITLE_MODE_BUTTON_ONLINE_TEXT,
            autocomplete_enabled=True,
        )

    return TitleInputModePresentation(
        mode=TITLE_INPUT_MODE_OFFLINE,
        placeholder=offline_placeholder,
        button_text=TITLE_MODE_BUTTON_OFFLINE_TEXT,
        autocomplete_enabled=False,
    )
