from dataclasses import dataclass
from uuid import uuid4


@dataclass
class DimState:
    name: str
    value: float = 5.0


@dataclass(frozen=True)
class ScoredDimension:
    name: str
    value: float


@dataclass(frozen=True)
class ScoringInput:
    title: str
    selected_profiles: tuple[str, ...]
    profile_ratios: tuple[float, ...]
    dimensions: tuple[ScoredDimension, ...]


@dataclass(frozen=True)
class ScoringSummary:
    strengths: tuple[ScoredDimension, ...]
    weakness: ScoredDimension | None


@dataclass(frozen=True)
class ScoringResult:
    score: float
    display_score: float
    tier: str
    input: ScoringInput
    relevances: tuple[float, ...]
    contributions: tuple[float, ...]
    summary: ScoringSummary

    @property
    def selected(self) -> list[str]:
        return list(self.input.selected_profiles)

    @property
    def ratios(self) -> list[float]:
        return list(self.input.profile_ratios)

    @property
    def values(self) -> list[float]:
        return [dimension.value for dimension in self.input.dimensions]


@dataclass(frozen=True)
class AnimeSearchResult:
    anilist_id: int
    title_romaji: str
    title_english: str | None
    title_native: str | None
    cover_url: str | None
    season_year: int | None


@dataclass
class TierCardData:
    """UI-independent metadata for one Tier Board card.

    Keep this object limited to small, serializable values. Downloaded cover
    images and ``QPixmap`` instances must remain runtime-only widget/cache
    state. This lets mode-specific presentations share one source of truth
    without copying or destructively rewriting card data.

    This is an internal architecture detail, not a user-facing capability,
    and should not be advertised as one in release notes.
    """

    card_id: str
    title: str
    current_tier: str
    card_type: str
    score: float | None = None
    score_tier: str | None = None
    anilist_id: int | None = None
    input_snapshot: "TierCardInputSnapshot | None" = None

    TYPE_SCORED = "scored"
    TYPE_MANUAL = "manual"

    @classmethod
    def create(
        cls,
        *,
        title: str,
        current_tier: str,
        card_type: str,
        score: float | None = None,
        score_tier: str | None = None,
        anilist_id: int | None = None,
        input_snapshot: "TierCardInputSnapshot | None" = None,
    ) -> "TierCardData":
        return cls(
            card_id=str(uuid4()),
            title=title,
            current_tier=current_tier,
            card_type=card_type,
            score=score,
            score_tier=score_tier,
            anilist_id=anilist_id,
            input_snapshot=input_snapshot,
        )


@dataclass
class TierCardInputSnapshot:
    """Serializable scored-input state used to reopen a saved card."""

    mix_mode: str
    profile_names: list[str]
    profile_weights: list[int]
    dimension_values: list[float]
