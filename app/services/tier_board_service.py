"""UI-independent Tier Board state and card lifecycle rules."""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from app.core.models import TierCardData, TierCardInputSnapshot

DEFAULT_TIERS = ("S", "A", "B", "C", "D", "E", "F")
EMPTY_TITLE_PLACEHOLDERS = {"(nincs cím)", "(nincs cĂ­m)"}


@dataclass(frozen=True)
class TierBoardMutation:
    changed: bool
    reason: str | None = None
    card: TierCardData | None = None
    removed_count: int = 0


@dataclass
class TierBoardState:
    tiers: tuple[str, ...] = DEFAULT_TIERS
    cards_by_tier: dict[str, list[TierCardData]] = field(init=False)
    normalized_titles: set[str] = field(default_factory=set)
    cards_by_id: dict[str, TierCardData] = field(default_factory=dict)

    def __post_init__(self):
        self.cards_by_tier = {tier: [] for tier in self.tiers}

    def card_count(self) -> int:
        return len(self.cards_by_id)

    def has_cards(self) -> bool:
        return bool(self.cards_by_id)

    def add_card(
        self,
        *,
        title: str,
        tier: str,
        card_type: str,
        score: float | None = None,
        anilist_id: int | None = None,
        input_snapshot: TierCardInputSnapshot | None = None,
    ) -> TierBoardMutation:
        clean_title = title.strip()
        if not clean_title or clean_title in EMPTY_TITLE_PLACEHOLDERS:
            return TierBoardMutation(False, "empty_title")
        if tier not in self.cards_by_tier:
            return TierBoardMutation(False, "invalid_tier")
        normalized_title = clean_title.casefold()
        if normalized_title in self.normalized_titles:
            return TierBoardMutation(False, "duplicate_title")
        if card_type not in (TierCardData.TYPE_SCORED, TierCardData.TYPE_MANUAL):
            return TierBoardMutation(False, "invalid_card_type")
        if card_type == TierCardData.TYPE_MANUAL and score is not None:
            return TierBoardMutation(False, "manual_card_has_score")
        if card_type == TierCardData.TYPE_SCORED and score is None:
            return TierBoardMutation(False, "scored_card_missing_score")

        card = TierCardData.create(
            title=clean_title,
            current_tier=tier,
            card_type=card_type,
            score=score,
            score_tier=tier if card_type == TierCardData.TYPE_SCORED else None,
            anilist_id=anilist_id,
            input_snapshot=input_snapshot,
        )
        self.cards_by_tier[tier].append(card)
        self.cards_by_id[card.card_id] = card
        self.normalized_titles.add(normalized_title)
        return TierBoardMutation(True, card=card)

    def remove_card(self, card_id: str) -> TierBoardMutation:
        card = self.cards_by_id.pop(card_id, None)
        if card is None:
            return TierBoardMutation(False, "card_not_found")
        row = self.cards_by_tier.get(card.current_tier, [])
        if card in row:
            row.remove(card)
        self.normalized_titles.discard(card.title.casefold())
        return TierBoardMutation(True, card=card, removed_count=1)

    def replace_scored_card(
        self,
        card_id: str,
        *,
        title: str,
        score: float,
        tier: str,
        anilist_id: int | None,
        input_snapshot: TierCardInputSnapshot | None,
    ) -> TierBoardMutation:
        card = self.cards_by_id.get(card_id)
        clean_title = title.strip()
        if card is None:
            return TierBoardMutation(False, "card_not_found")
        if card.card_type != TierCardData.TYPE_SCORED:
            return TierBoardMutation(False, "manual_card_not_editable_as_scored")
        if not clean_title or clean_title in EMPTY_TITLE_PLACEHOLDERS:
            return TierBoardMutation(False, "empty_title")
        if tier not in self.cards_by_tier:
            return TierBoardMutation(False, "invalid_tier")
        normalized_title = clean_title.casefold()
        if normalized_title != card.title.casefold() and (
            normalized_title in self.normalized_titles
        ):
            return TierBoardMutation(False, "duplicate_title")

        source_tier = card.current_tier
        source_row = self.cards_by_tier[source_tier]
        source_index = source_row.index(card)
        source_row.remove(card)
        self.normalized_titles.discard(card.title.casefold())
        replacement = replace(
            card,
            title=clean_title,
            score=score,
            current_tier=tier,
            score_tier=tier,
            anilist_id=anilist_id,
            input_snapshot=input_snapshot,
        )
        target_row = self.cards_by_tier[tier]
        target_row.insert(source_index if tier == source_tier else len(target_row), replacement)
        self.cards_by_id[card_id] = replacement
        self.normalized_titles.add(normalized_title)
        return TierBoardMutation(True, card=replacement)

    def clear(self) -> TierBoardMutation:
        removed_count = self.card_count()
        for cards in self.cards_by_tier.values():
            cards.clear()
        self.cards_by_id.clear()
        self.normalized_titles.clear()
        return TierBoardMutation(
            changed=removed_count > 0,
            reason=None if removed_count else "board_empty",
            removed_count=removed_count,
        )

    def synchronize_rows(
        self,
        cards_by_tier: dict[str, list[TierCardData]],
    ) -> None:
        """Synchronize positions after a presentation-owned drag operation.

        Movement rules are extracted in the next refactor stage. Until then,
        this keeps the domain state authoritative for membership and row order
        while Qt still interprets the drag gesture.
        """
        self.cards_by_tier = {
            tier: list(cards_by_tier.get(tier, ())) for tier in self.tiers
        }
        for tier, cards in self.cards_by_tier.items():
            for card in cards:
                card.current_tier = tier
