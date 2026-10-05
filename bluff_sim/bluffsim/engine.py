"""The rules engine. No strategy lives here.

`resolve_round` and `check_end` are pure functions of the round's inputs, so
the rules can be tested without bots. `play_game` runs a whole game: it deals,
asks each bot for its play, clue and veto through a `PublicState` plus the
bot's own hand, and records what happened.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional, Sequence

from .config import GameConfig

CLUE_NAMES = {-2: "much lower", -1: "lower", 0: "close",
              1: "higher", 2: "much higher"}

END_BUST = "bust"                  # group lost; closest to zero wins
END_BUST_NO_WINNER = "bust_none"   # bust under the optional near-zero rule
END_SOLO = "solo"
END_SHARED = "shared"


def clue_for(drift: int, cfg: GameConfig) -> int:
    """The truthful clue for a drift (pocket total minus personal target)."""
    if abs(drift) <= cfg.clue_close:
        return 0
    sign = 1 if drift > 0 else -1
    return 2 * sign if abs(drift) >= cfg.clue_much else sign


def clue_range(clue: int, cfg: GameConfig) -> tuple[float, float]:
    """The drift interval a truthful clue covers (inclusive)."""
    inf = float("inf")
    return {-2: (-inf, -cfg.clue_much),
            -1: (-(cfg.clue_much - 1), -(cfg.clue_close + 1)),
            0: (-cfg.clue_close, cfg.clue_close),
            1: (cfg.clue_close + 1, cfg.clue_much - 1),
            2: (cfg.clue_much, inf)}[clue]


# ---------------------------------------------------------------------------
# Pure rule resolution
# ---------------------------------------------------------------------------

def leaders_and_eligible(cfg: GameConfig, tracks: Sequence[int]):
    """Leaders: everyone tied for the largest |track|. Eligible: non-leaders
    whose |track| is at least `veto_gap` below the leaders'. With vetoes
    switched off, nobody is ever eligible."""
    top = max(abs(t) for t in tracks)
    leaders = [i for i, t in enumerate(tracks) if abs(t) == top]
    if not cfg.vetoes_enabled:
        return leaders, []
    eligible = [i for i, t in enumerate(tracks)
                if i not in leaders and abs(t) <= top - cfg.veto_gap]
    return leaders, eligible


@dataclass
class Resolution:
    tracks: list[int]
    tally: int
    track_delta: list[int]
    contributions: list[int]
    vetoed_by: dict[int, list[int]]
    stolen: list[tuple[int, int, int]]   # (vetoer, target, amount added)
    tally_delta: int
    end_type: Optional[str]
    winners: tuple[int, ...]


def resolve_round(cfg: GameConfig, tracks: Sequence[int], tally: int,
                  personal: Sequence[int], collective: int,
                  totals: Sequence[int], vetoes: dict[int, Optional[int]],
                  final: bool, takes: Optional[dict] = None) -> Resolution:
    """Apply step 4 (reveal and resolve) and the end checks.

    `vetoes` maps vetoer -> target (or None for a pass). A vetoer takes only
    the target's own pocket drift, never what the target stole this round.
    Under veto_mode "block" vetoers receive nothing; under "choose",
    `takes[vetoer]` says whether that vetoer kept the drift.
    """
    n = len(tracks)
    mult = cfg.final_multiplier if final else 1
    steal_mult = mult if cfg.final_doubles_stolen else 1
    drifts = [totals[i] - personal[i] for i in range(n)]

    vetoed_by: dict[int, list[int]] = {}
    for v, t in vetoes.items():
        if t is not None:
            vetoed_by.setdefault(t, []).append(v)

    delta = [0] * n
    stolen = []
    contributions = list(totals)
    for j in range(n):
        vs = vetoed_by.get(j)
        if not vs:
            delta[j] += drifts[j] * mult
            continue
        for v in vs:
            if cfg.veto_mode == "block":
                continue
            if cfg.veto_mode == "choose" and takes is not None \
                    and not takes.get(v, True):
                continue
            delta[v] += drifts[j] * steal_mult
            stolen.append((v, j, drifts[j] * steal_mult))
        if len(vs) >= cfg.double_veto_at:
            contributions[j] = personal[j]

    new_tracks = [tracks[i] + delta[i] for i in range(n)]
    if cfg.track_cap is not None:
        c = cfg.track_cap
        new_tracks = [max(-c, min(c, t)) for t in new_tracks]
    tally_delta = sum(contributions) - collective
    new_tally = tally + tally_delta
    end_type, winners = check_end(cfg, new_tracks, new_tally, final)
    return Resolution(new_tracks, new_tally, delta, contributions, vetoed_by,
                      stolen, tally_delta, end_type, winners)


def check_end(cfg: GameConfig, tracks: Sequence[int], tally: int,
              final: bool) -> tuple[Optional[str], tuple[int, ...]]:
    """End conditions in rule order: bust, then solo, then shared."""
    if abs(tally) > cfg.bust_limit:
        best = min(abs(t) for t in tracks)
        if cfg.bust_win_requires_near_zero and best > cfg.bust_near_zero:
            return END_BUST_NO_WINNER, ()
        return END_BUST, tuple(i for i, t in enumerate(tracks)
                               if abs(t) == best)
    top = max(abs(t) for t in tracks)
    if top >= cfg.win_threshold:
        return END_SOLO, tuple(i for i, t in enumerate(tracks)
                               if abs(t) == top)
    if final:
        return END_SHARED, tuple(range(len(tracks)))
    return None, ()


# ---------------------------------------------------------------------------
# Public state handed to bots
# ---------------------------------------------------------------------------

@dataclass
class PublicState:
    """Everything every player can see. Bots must treat it as read-only."""
    cfg: GameConfig
    round: int = 0                      # 0-based
    tracks: list[int] = field(default_factory=list)
    tally: int = 0
    personal: list[int] = field(default_factory=list)
    collective: int = 0
    order: list[int] = field(default_factory=list)
    plays: dict = field(default_factory=dict)        # seat -> (n_cards, clue)
    discard: list[int] = field(default_factory=list)  # count per card value
    hand_sizes: list[int] = field(default_factory=list)
    leaders: list[int] = field(default_factory=list)
    eligible: list[int] = field(default_factory=list)
    history: list["RoundRecord"] = field(default_factory=list)

    @property
    def final(self) -> bool:
        return self.round == self.cfg.rounds - 1

    @property
    def rounds_left(self) -> int:
        """Rounds after this one."""
        return self.cfg.rounds - 1 - self.round

    @property
    def gap(self) -> int:
        return self.collective - sum(self.personal)

    @property
    def multiplier(self) -> int:
        return self.cfg.final_multiplier if self.final else 1

    def composition(self) -> list[int]:
        """Count of each card value in the full hand deck (public)."""
        comp = [0] * (self.cfg.hand_hi + 1)
        copies = self.cfg.effective_hand_copies()
        for v in self.cfg.hand_values():
            comp[v] = copies
        return comp


@dataclass
class RoundRecord:
    round: int
    first: int
    order: list[int]
    tracks_before: list[int]
    tally_before: int
    personal: list[int]
    collective: int
    gap: int
    cards: list[tuple[int, ...]]
    clues: list[int]
    leaders: list[int]
    eligible: list[int]
    vetoes: dict[int, Optional[int]]
    totals: list[int]
    drifts: list[int]
    track_delta: list[int]
    contributions: list[int]
    stolen: list[tuple[int, int, int]]
    tally_delta: int
    tracks_after: list[int]
    tally_after: int
    end_type: Optional[str]
    winners: tuple[int, ...]


@dataclass
class GameResult:
    end_type: str
    winners: tuple[int, ...]
    rounds_played: int
    tracks: list[int]
    tally: int
    strategies: list[str]
    records: list[RoundRecord]
    # Steals in the last round without which a vetoer would not have won:
    # (vetoer, target, amount).
    decisive_steals: list[tuple[int, int, int]]
    seed: int = 0


class RuleViolation(Exception):
    pass


def _remove_cards(hand: list[int], cards: Sequence[int]) -> None:
    for c in cards:
        try:
            hand.remove(c)
        except ValueError:
            raise RuleViolation(f"played {c} not in hand {hand}") from None


def play_game(cfg: GameConfig, bots: Sequence, seed: int) -> GameResult:
    """Play one full game. `bots[i]` sits in seat i."""
    n = cfg.n_players
    if len(bots) != n:
        raise ValueError(f"need {n} bots, got {len(bots)}")
    rng = random.Random(seed)

    hand_deck = cfg.hand_deck()
    rng.shuffle(hand_deck)
    p_deck, p_used = cfg.personal_deck(), []
    c_deck, c_used = cfg.collective_deck(), []
    rng.shuffle(p_deck)
    rng.shuffle(c_deck)

    def draw_target(deck, used):
        if not deck:
            deck.extend(used)
            used.clear()
            rng.shuffle(deck)
        card = deck.pop()
        used.append(card)
        return card

    hands = [[hand_deck.pop() for _ in range(cfg.hand_size)] for _ in range(n)]
    pub = PublicState(cfg=cfg, tracks=[0] * n,
                      discard=[0] * (cfg.hand_hi + 1))
    for i, bot in enumerate(bots):
        bot.new_game(i, cfg, random.Random(seed * 1009 + i + 1))

    end_type, winners, decisive = None, (), []
    for r in range(cfg.rounds):
        final = r == cfg.rounds - 1
        pub.round = r
        pub.personal = [draw_target(p_deck, p_used) for _ in range(n)]
        pub.collective = draw_target(c_deck, c_used)
        first = r % n
        pub.order = [(first + k) % n for k in range(n)]
        pub.plays = {}
        pub.hand_sizes = [len(h) for h in hands]
        pub.leaders, pub.eligible = leaders_and_eligible(cfg, pub.tracks)

        # Play and clue, in turn order.
        cards: list = [()] * n
        clues = [0] * n
        for i in pub.order:
            hand = hands[i]
            lo = min(cfg.min_cards, len(hand))
            hi = min(cfg.max_cards, len(hand))
            chosen, clue = bots[i].play(i, pub, tuple(hand))
            chosen = tuple(chosen)
            if not lo <= len(chosen) <= hi:
                raise RuleViolation(
                    f"seat {i} played {len(chosen)} cards; allowed {lo}-{hi}")
            if clue not in CLUE_NAMES:
                raise RuleViolation(f"seat {i} gave clue {clue!r}")
            _remove_cards(hand, chosen)
            cards[i], clues[i] = chosen, clue
            pub.plays[i] = (len(chosen), clue)
            pub.hand_sizes[i] = len(hand)

        # Vetoes, declared simultaneously: each bot decides from the same view.
        vetoes: dict[int, Optional[int]] = {}
        paid: list[int] = []
        for i in pub.eligible:
            if len(hands[i]) < cfg.veto_cost:
                continue
            t = bots[i].veto(i, pub, tuple(hands[i]), cards[i])
            if t is not None:
                if t == i or not 0 <= t < n:
                    raise RuleViolation(f"seat {i} vetoed {t}")
                if cfg.veto_target == "leader" and t not in pub.leaders:
                    raise RuleViolation(f"seat {i} vetoed non-leader {t}")
            vetoes[i] = t

        # Paying for vetoes: each vetoer discards veto_cost cards.
        if cfg.veto_cost:
            for i, t in vetoes.items():
                if t is None:
                    continue
                gone = tuple(bots[i].veto_discard(i, pub, tuple(hands[i]),
                                                  cfg.veto_cost))
                if len(gone) != cfg.veto_cost:
                    raise RuleViolation(f"seat {i} paid {len(gone)} cards")
                _remove_cards(hands[i], gone)
                paid.extend(gone)

        totals = [sum(c) for c in cards]
        takes = None
        if cfg.veto_mode == "choose":
            mult = (cfg.final_multiplier
                    if final and cfg.final_doubles_stolen else 1)
            takes = {v: bool(bots[v].keep_steal(
                         v, pub, t, (totals[t] - pub.personal[t]) * mult))
                     for v, t in vetoes.items() if t is not None}
        res = resolve_round(cfg, pub.tracks, pub.tally, pub.personal,
                            pub.collective, totals, vetoes, final, takes)

        if res.end_type is not None and any(
                t is not None for t in vetoes.values()):
            decisive = _decisive_steals(cfg, pub, totals, vetoes, final, res,
                                        takes)

        rec = RoundRecord(
            round=r, first=first, order=list(pub.order),
            tracks_before=list(pub.tracks), tally_before=pub.tally,
            personal=list(pub.personal), collective=pub.collective,
            gap=pub.gap, cards=list(cards), clues=clues,
            leaders=list(pub.leaders), eligible=list(pub.eligible),
            vetoes=dict(vetoes), totals=totals,
            drifts=[totals[i] - pub.personal[i] for i in range(n)],
            track_delta=res.track_delta, contributions=res.contributions,
            stolen=res.stolen, tally_delta=res.tally_delta,
            tracks_after=res.tracks, tally_after=res.tally,
            end_type=res.end_type, winners=res.winners)
        pub.history.append(rec)

        # Cleanup.
        for c in list(cards) + [paid]:
            for v in c:
                pub.discard[v] += 1
        pub.tracks, pub.tally = res.tracks, res.tally
        if res.end_type is not None:
            end_type, winners = res.end_type, res.winners
            break
        for h in hands:
            for _ in range(cfg.draw_per_round):
                if hand_deck:
                    h.append(hand_deck.pop())

    return GameResult(end_type=end_type, winners=winners,
                      rounds_played=len(pub.history), tracks=pub.tracks,
                      tally=pub.tally, strategies=[b.name for b in bots],
                      records=pub.history, decisive_steals=decisive, seed=seed)


def _decisive_steals(cfg, pub, totals, vetoes, final, res, takes=None):
    """Vetoes the winning vetoer could not have won without.

    For each veto in the game-ending round, re-resolve with that single veto
    turned into a pass. If the vetoer won and would not have won otherwise,
    the veto caused the win. Returns (vetoer, target, drift taken).
    """
    taken = {(v, t): a for v, t, a in res.stolen}
    out = []
    for v, t in vetoes.items():
        if t is None or v not in res.winners:
            continue
        alt = dict(vetoes)
        alt[v] = None
        cf = resolve_round(cfg, pub.tracks, pub.tally, pub.personal,
                           pub.collective, totals, alt, final, takes)
        if cf.end_type is None or v not in cf.winners:
            out.append((v, t, taken.get((v, t), 0)))
    return out
