from dataclasses import dataclass


@dataclass
class DimState:
    name: str
    value: float = 5.0


@dataclass(frozen=True)
class AnimeSearchResult:
    anilist_id: int
    title_romaji: str
    title_english: str | None
    title_native: str | None
    cover_url: str | None
    season_year: int | None
