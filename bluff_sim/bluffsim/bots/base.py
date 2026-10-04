"""Shared tools for bots: card choice, clue choice, and reading opponents.

Bots see only the `PublicState` and their own hand. Everything here works
from that alone.

How a bot reads an opponent's drift (`estimate_drift`):
  1. Prior: the opponent's pocket is treated as `n` cards drawn from the
     cards this bot has not seen (full deck minus discards minus its own hand
     and pocket). That gives a distribution of pocket totals.
  2. If the clue were true, the total must lie in the clue's band. The
     conditional mean inside the band is the "believed" estimate.
  3. The estimate is `trust * believed + (1 - trust) * prior mean`.
It ignores that opponents pick cards on purpose. That is a known weakness,
kept for simplicity.
"""
from __future__ import annotations

import itertools
from functools import lru_cache
from typing import Optional, Sequence

import numpy as np

from ..engine import PublicState, clue_for, clue_range


@lru_cache(maxsize=200_000)
def combos(hand: tuple, lo: int, hi: int) -> tuple:
    """Distinct (cards, total) choices of lo..hi cards from a sorted hand."""
    seen = set()
    out = []
    for k in range(lo, hi + 1):
        for idx in itertools.combinations(range(len(hand)), k):
            cards = tuple(hand[i] for i in idx)
            if cards not in seen:
                seen.add(cards)
                out.append((cards, sum(cards)))
    return tuple(out)


def legal_combos(pub: PublicState, hand: Sequence[int]) -> tuple:
    cfg = pub.cfg
    h = tuple(sorted(hand))
    return combos(h, min(cfg.min_cards, len(h)), min(cfg.max_cards, len(h)))


def pick_total(pub: PublicState, hand: Sequence[int], desired: float,
               card_cost: float = 0.0, extreme_cost: float = 0.0):
    """Cards whose total is closest to `desired`.

    `card_cost` is a penalty per card played (positive saves cards, negative
    spends them). `extreme_cost` penalises spending very high or very low
    cards, which are the ones that make big drifts possible later.
    """
    mid = (pub.cfg.hand_lo + pub.cfg.hand_hi) / 2
    span = (pub.cfg.hand_hi - pub.cfg.hand_lo) / 2 or 1
    best, best_score = None, None
    for cards, total in legal_combos(pub, hand):
        score = abs(total - desired) + card_cost * len(cards)
        if extreme_cost:
            score += extreme_cost * sum(abs(c - mid) / span for c in cards)
        if best_score is None or score < best_score:
            best, best_score = cards, score
    return best


def extreme_total(pub: PublicState, hand: Sequence[int], direction: int):
    """The highest (direction > 0) or lowest (direction < 0) legal play."""
    options = legal_combos(pub, hand)
    if direction > 0:
        return max(options, key=lambda ct: ct[1])[0]
    return min(options, key=lambda ct: ct[1])[0]


def lie(true_clue: int, direction: int, size: int) -> int:
    """Shift a clue `size` bands in `direction`, clamped to the scale."""
    return max(-2, min(2, true_clue + direction * size))


def sign(x: float) -> int:
    return (x > 0) - (x < 0)


# ---------------------------------------------------------------------------
# Reading the table
# ---------------------------------------------------------------------------

def unseen_counts(pub: PublicState, hand: Sequence[int],
                  pocket: Sequence[int] = ()) -> list[int]:
    counts = pub.composition()
    for v in range(len(counts)):
        counts[v] -= pub.discard[v]
    for v in list(hand) + list(pocket):
        counts[v] -= 1
    return [max(0, c) for c in counts]


_pmf_cache: dict = {}


def total_pmf(counts: Sequence[int], n: int) -> np.ndarray:
    """Distribution of the sum of n cards drawn (with replacement, as an
    approximation) from the unseen cards. Index = total."""
    key = (tuple(counts), n)
    hit = _pmf_cache.get(key)
    if hit is not None:
        return hit
    base = np.asarray(counts, dtype=float)
    s = base.sum()
    if s == 0:
        base = np.ones_like(base)
        base[0] = 0
        s = base.sum()
    base /= s
    pmf = np.array([1.0])
    for _ in range(n):
        pmf = np.convolve(pmf, base)
    if len(_pmf_cache) > 50_000:
        _pmf_cache.clear()
    _pmf_cache[key] = pmf
    return pmf


def estimate_drift(pub: PublicState, seat: int, counts: Sequence[int],
                   trust: float = 0.7) -> float:
    """Expected drift (pocket total - personal target) of another seat."""
    n_cards, clue = pub.plays[seat]
    target = pub.personal[seat]
    if n_cards == 0:
        return -target
    pmf = total_pmf(counts, n_cards)
    totals = np.arange(len(pmf))
    prior = float((pmf * totals).sum()) - target
    lo, hi = clue_range(clue, pub.cfg)
    drifts = totals - target
    mask = (drifts >= lo) & (drifts <= hi)
    mass = pmf[mask].sum()
    if mass > 1e-9:
        believed = float((pmf[mask] * drifts[mask]).sum() / mass)
    else:
        # The clue is impossible under the prior: take the nearest edge.
        believed = lo if abs(lo - prior) < abs(hi - prior) else hi
        if not np.isfinite(believed):
            believed = prior
    return trust * believed + (1 - trust) * prior


def others_drift(pub: PublicState, me: int, counts: Sequence[int],
                 trust: float = 0.7) -> float:
    """Expected total drift of everyone else this round. Seats that have not
    played yet are assumed to play to their target (drift 0)."""
    return sum(estimate_drift(pub, s, counts, trust)
               for s in pub.plays if s != me)


def projected_tally(pub: PublicState, my_drift: float, others: float) -> float:
    """Tally after this round if nobody is double-vetoed.

    tally += sum(pocket totals) - collective = sum(drifts) - gap.
    """
    return pub.tally + others + my_drift - pub.gap


def drift_room(pub: PublicState, direction: int, others: float,
               margin: float) -> float:
    """How far my drift can go in `direction` before the projected tally
    comes within `margin` of the bust limit. Can be negative."""
    base = projected_tally(pub, 0, others)
    limit = pub.cfg.bust_limit - margin
    return limit - base if direction > 0 else limit + base


def steal_value(pub: PublicState, target: int, counts, trust: float) -> float:
    """Signed drift a vetoer would add to its own track by vetoing `target`."""
    d = estimate_drift(pub, target, counts, trust)
    if pub.final and pub.cfg.final_doubles_stolen:
        d *= pub.cfg.final_multiplier
    return d


def veto_candidates(pub: PublicState, me: int) -> list[int]:
    if pub.cfg.veto_target == "leader":
        return [s for s in pub.leaders if s != me]
    return [s for s in range(pub.cfg.n_players) if s != me]


class Bot:
    """Base class. Subclasses override `play` and `veto`."""
    name = "base"

    def new_game(self, seat: int, cfg, rng) -> None:
        self.seat, self.cfg, self.rng = seat, cfg, rng

    def play(self, seat: int, pub: PublicState, hand: tuple):
        raise NotImplementedError

    def veto(self, seat: int, pub: PublicState, hand: tuple,
             pocket: tuple) -> Optional[int]:
        return None

    # Helpers subclasses use.
    def truthful(self, pub: PublicState, seat: int, cards) -> int:
        return clue_for(sum(cards) - pub.personal[seat], pub.cfg)

    def best_steal(self, pub, seat, hand, pocket, gain_fn, threshold,
                   trust=0.7) -> Optional[int]:
        """Veto the candidate with the largest `gain_fn(steal)` if it reaches
        `threshold`; otherwise pass."""
        counts = unseen_counts(pub, hand, pocket)
        best, best_gain = None, threshold
        for t in veto_candidates(pub, seat):
            g = gain_fn(t, steal_value(pub, t, counts, trust), counts)
            if g >= best_gain:
                best, best_gain = t, g
        return best
