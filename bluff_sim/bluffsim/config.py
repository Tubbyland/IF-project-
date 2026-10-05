"""Every rule parameter in one place.

`GameConfig` holds the rules. Load overrides from a YAML or JSON file with
`load_config(path)`; any field left out keeps its default.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field, fields, replace
from typing import Optional


@dataclass(frozen=True)
class GameConfig:
    # --- Table ---------------------------------------------------------------
    n_players: int = 4                 # 3-5
    hand_size: int = 5                 # cards dealt at setup
    rounds: int = 7

    # --- Hand deck: values lo..hi, `hand_copies` of each ------------------------
    hand_lo: int = 1
    hand_hi: int = 20
    hand_copies: int = 4
    # If True, copies are raised (never lowered) so the deck can never run out:
    # the hand deck is never reshuffled.
    hand_copies_auto: bool = True

    # --- Personal Target deck (reshuffled from its discards when empty) --------
    personal_lo: int = 15
    personal_hi: int = 30
    personal_copies: int = 2
    # If True, copies are raised (never lowered) so a game never needs to
    # reshuffle the personal target deck.
    personal_copies_auto: bool = True

    # --- Collective Target deck (reshuffled from its discards when empty) ------
    # "split": one copy of each value in each range of `collective_split`.
    # "continuous": one copy of each value in `collective_continuous`.
    collective_mode: str = "split"
    collective_split: tuple = ((70, 82), (98, 110))
    collective_continuous: tuple = (75, 105)

    # --- Tracks and tally ------------------------------------------------------
    win_threshold: int = 30            # |track| >= this is a solo win
    track_cap: Optional[int] = None    # None: tracks are not clamped
    bust_limit: int = 20               # |tally| > this is a bust

    # --- Playing cards ---------------------------------------------------------
    min_cards: int = 1
    max_cards: int = 3
    draw_per_round: int = 1

    # --- Clues: band edges on (pocket total - personal target) ----------------
    # |d| <= clue_close -> "close"; |d| >= clue_much -> "much lower/higher";
    # otherwise "lower/higher".
    clue_close: int = 2
    clue_much: int = 8

    # --- Vetoes ----------------------------------------------------------------
    vetoes_enabled: bool = True        # False removes the veto phase
    veto_gap: int = 10                 # X: eligible if |track| <= leader's - X
    veto_target: str = "any"           # "any" or "leader"
    double_veto_at: int = 2            # vetoes needed to zero group drift
    # What a veto does to the vetoer:
    #   "take"   each vetoer adds the target's drift to its own track
    #   "block"  the target's drift is cancelled; vetoers receive nothing
    #   "choose" after the reveal, each vetoer takes the drift or discards it
    veto_mode: str = "take"
    veto_cost: int = 0                 # hand cards a vetoer must discard

    # --- Final round -----------------------------------------------------------
    final_multiplier: int = 2
    final_doubles_stolen: bool = True

    # --- Bust win --------------------------------------------------------------
    bust_win_requires_near_zero: bool = False
    bust_near_zero: int = 5

    # ---------------------------------------------------------------------------
    def hand_values(self) -> list[int]:
        return list(range(self.hand_lo, self.hand_hi + 1))

    def cards_needed(self) -> int:
        """Hand cards a full game can consume: the deal plus every draw.

        Players draw at cleanup after every round except the last, since
        nothing happens after it.
        """
        return self.n_players * (self.hand_size
                                 + self.draw_per_round * (self.rounds - 1))

    def effective_hand_copies(self) -> int:
        if not self.hand_copies_auto:
            return self.hand_copies
        n_values = self.hand_hi - self.hand_lo + 1
        return max(self.hand_copies, math.ceil(self.cards_needed() / n_values))

    def hand_deck(self) -> list[int]:
        return [v for v in self.hand_values()
                for _ in range(self.effective_hand_copies())]

    def effective_personal_copies(self) -> int:
        if not self.personal_copies_auto:
            return self.personal_copies
        n_values = self.personal_hi - self.personal_lo + 1
        return max(self.personal_copies,
                   math.ceil(self.n_players * self.rounds / n_values))

    def personal_deck(self) -> list[int]:
        return [v for v in range(self.personal_lo, self.personal_hi + 1)
                for _ in range(self.effective_personal_copies())]

    def collective_deck(self) -> list[int]:
        if self.collective_mode == "split":
            return [v for lo, hi in self.collective_split
                    for v in range(lo, hi + 1)]
        if self.collective_mode == "continuous":
            lo, hi = self.collective_continuous
            return list(range(lo, hi + 1))
        raise ValueError(f"unknown collective_mode {self.collective_mode!r}")

    def validate(self) -> None:
        problems = []
        if not 2 <= self.n_players <= 8:
            problems.append("n_players must be 2-8")
        if self.min_cards < 0 or self.max_cards < max(1, self.min_cards):
            problems.append("need 0 <= min_cards <= max_cards, max_cards >= 1")
        if self.veto_mode not in ("take", "block", "choose"):
            problems.append("veto_mode must be 'take', 'block' or 'choose'")
        if self.veto_cost < 0:
            problems.append("veto_cost must be >= 0")
        if self.veto_target not in ("any", "leader"):
            problems.append("veto_target must be 'any' or 'leader'")
        if len(self.hand_deck()) < self.cards_needed():
            problems.append(
                f"hand deck has {len(self.hand_deck())} cards but a game can "
                f"need {self.cards_needed()}; raise hand_copies or set "
                f"hand_copies_auto")
        if len(self.collective_deck()) < self.rounds:
            problems.append("collective deck has fewer cards than rounds")
        if not 0 <= self.clue_close < self.clue_much:
            problems.append("need 0 <= clue_close < clue_much")
        if problems:
            raise ValueError("; ".join(problems))

    def with_(self, **changes) -> "GameConfig":
        return replace(self, **changes)

    def to_dict(self) -> dict:
        return asdict(self)


def _coerce(name: str, value):
    """Turn YAML/JSON lists back into the tuples the dataclass uses."""
    if name == "collective_split":
        return tuple(tuple(r) for r in value)
    if name == "collective_continuous":
        return tuple(value)
    return value


def config_from_dict(d: dict) -> GameConfig:
    known = {f.name for f in fields(GameConfig)}
    unknown = set(d) - known
    if unknown:
        raise ValueError(f"unknown config keys: {sorted(unknown)}")
    cfg = GameConfig(**{k: _coerce(k, v) for k, v in d.items()})
    cfg.validate()
    return cfg


def load_config(path: Optional[str]) -> GameConfig:
    if not path:
        return GameConfig()
    with open(path) as f:
        text = f.read()
    if path.endswith((".yaml", ".yml")):
        import yaml
        data = yaml.safe_load(text) or {}
    else:
        data = json.loads(text)
    game = data.get("game", data)
    return config_from_dict(game)


def parse_value(text: str):
    """Parse a command-line value: int, float, bool, None or string."""
    low = text.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("none", "null"):
        return None
    for cast in (int, float):
        try:
            return cast(text)
        except ValueError:
            pass
    return text
