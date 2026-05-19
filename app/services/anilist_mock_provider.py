"""Mock AniList title provider for UI autocomplete spike.

This module intentionally contains no network/API logic.
It exists so the mock data can be reused by application code and tests
without placing temporary data inside main.py.
"""


def get_mock_anime_titles() -> list[str]:
    return [
        "Re:Zero kara Hajimeru Isekai Seikatsu",
        "Re:Zero kara Hajimeru Isekai Seikatsu 2nd Season",
        "Re:Zero kara Hajimeru Isekai Seikatsu 3rd Season",
        "Sousou no Frieren",
        "86 Eighty-Six",
        "Fullmetal Alchemist: Brotherhood",
    ]
