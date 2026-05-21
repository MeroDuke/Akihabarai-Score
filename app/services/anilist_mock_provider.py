"""Mock AniList provider for UI autocomplete and service tests.

This module intentionally contains no network/API logic.
It exists so the mock data can be reused by application code and tests
without placing temporary data inside main.py.
"""

from app.core.models import AnimeSearchResult


def get_mock_anime_results() -> list[AnimeSearchResult]:
    return [
        AnimeSearchResult(
            anilist_id=21355,
            title_romaji="Re:Zero kara Hajimeru Isekai Seikatsu",
            title_english="Re:ZERO -Starting Life in Another World-",
            title_native="Re:ゼロから始める異世界生活",
            cover_url="https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21355-wN7M9zZA7P2Q.jpg",
            season_year=2016,
        ),
        AnimeSearchResult(
            anilist_id=108632,
            title_romaji="Re:Zero kara Hajimeru Isekai Seikatsu 2nd Season",
            title_english="Re:ZERO -Starting Life in Another World- Season 2",
            title_native="Re:ゼロから始める異世界生活 2nd season",
            cover_url="https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx108632-Gn10sXCt7c2K.jpg",
            season_year=2020,
        ),
        AnimeSearchResult(
            anilist_id=163134,
            title_romaji="Re:Zero kara Hajimeru Isekai Seikatsu 3rd Season",
            title_english="Re:ZERO -Starting Life in Another World- Season 3",
            title_native="Re:ゼロから始める異世界生活 3rd season",
            cover_url="https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx163134-BS3E3X7d9q5k.jpg",
            season_year=2024,
        ),
        AnimeSearchResult(
            anilist_id=154587,
            title_romaji="Sousou no Frieren",
            title_english="Frieren: Beyond Journey’s End",
            title_native="葬送のフリーレン",
            cover_url="https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx154587-gHSraOSa0nBG.jpg",
            season_year=2023,
        ),
        AnimeSearchResult(
            anilist_id=116589,
            title_romaji="86 Eighty-Six",
            title_english="86 EIGHTY-SIX",
            title_native="86―エイティシックス―",
            cover_url="https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx116589-rbMeCD5Ke7nL.jpg",
            season_year=2021,
        ),
        AnimeSearchResult(
            anilist_id=5114,
            title_romaji="Fullmetal Alchemist: Brotherhood",
            title_english="Fullmetal Alchemist: Brotherhood",
            title_native="鋼の錬金術師 FULLMETAL ALCHEMIST",
            cover_url="https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx5114-KJTQz9AIm6Wk.jpg",
            season_year=2009,
        ),
    ]


def get_mock_anime_titles() -> list[str]:
    return [result.title_romaji for result in get_mock_anime_results()]
