UNTITLED_TIER_PREVIEW_TITLE = "(nincs cím)"


def build_tier_preview_title(title: str) -> str:
    cleaned_title = title.strip()
    if cleaned_title:
        return cleaned_title

    return UNTITLED_TIER_PREVIEW_TITLE
