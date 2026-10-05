"""The Bluffer: wants a solo win, and hides it.

Plan, in two phases:
  creep   Pick a direction (its track's sign; at zero, the side with more
          tally room). Move toward it by at most `creep` a round, but stay
          `shadow_gap` behind the player furthest from zero and never past
          `cap`, so it is rarely the leader the others watch. With
          probability `creep_lie_rate` it says "close" whatever it played.
  burst   From round `burst_round` (and always in the final round, where
          drift counts double) it plays for the threshold outright: the
          drift that would carry it past ±30, limited only by
          `burst_room_margin` of tally room. With probability
          `burst_lie_rate` it lies about the burst, claiming `burst_claim`
          bands the other way (0 = "close", 1 = "lower", 2 = "much lower"
          when it is really going up).
Cards: while creeping it pays `extreme_cost` to spend its extreme cards,
so it saves them for the burst.
Veto: like the tuned players, it blocks threats to its own solo win.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .base import (Bot, drift_room, others_drift, pick_total,
                   projected_tally, sign, unseen_counts)
from .params import TunableParams

BLUFF_BOUNDS = {
    "shadow_gap": (0, 15, True),
    "cap": (5, 29, True),
    "creep": (0, 12, False),
    "burst_round": (3, 7, True),
    "room_margin": (-10, 15, False),
    "burst_room_margin": (-20, 15, False),
    "creep_lie_rate": (0, 1, False),
    "burst_lie_rate": (0, 1, False),
    "burst_claim": (0, 2, True),
    "help_weight": (0, 1, False),
    "card_cost": (-3, 3, False),
    "extreme_cost": (0, 4, False),
    "veto_threshold": (0, 20, False),
    "deny_weight": (0, 1.5, False),
    "danger_margin": (0, 30, True),
    "trust": (0, 1, False),
}


@dataclass
class BluffParams(TunableParams):
    BOUNDS: ClassVar[dict] = BLUFF_BOUNDS

    shadow_gap: int = 3
    cap: int = 16
    creep: float = 6.0
    burst_round: int = 7
    room_margin: float = 3.0
    burst_room_margin: float = -5.0
    creep_lie_rate: float = 0.3
    burst_lie_rate: float = 0.8
    burst_claim: int = 1
    help_weight: float = 0.2
    card_cost: float = 0.0
    extreme_cost: float = 1.0
    veto_threshold: float = 5.0
    deny_weight: float = 1.0
    danger_margin: int = 8
    trust: float = 0.5

    def describe(self) -> list[str]:
        p = self
        claim = {0: '"close"', 1: '"lower" (or "higher")',
                 2: '"much lower" (or "much higher")'}[p.burst_claim]
        return [
            f"Creeps up to {p.creep:.0f} a round toward its side, staying "
            f"{p.shadow_gap} behind whoever is furthest from zero and never "
            f"past {p.cap} before its burst.",
            f"Bursts for the threshold from round {p.burst_round} "
            f"(always in the final round), accepting "
            f"{'a projected bust overshoot of ' + format(-p.burst_room_margin, '.0f') if p.burst_room_margin < 0 else format(p.burst_room_margin, '.0f') + ' of tally room'}.",
            f"While creeping, says \"close\" {p.creep_lie_rate:.0%} of the "
            f"time whatever it played.",
            f"When bursting, lies {p.burst_lie_rate:.0%} of the time, "
            f"claiming {claim} in the opposite direction.",
            f"Gives {p.help_weight:.0%} weight to closing the group gap "
            f"while creeping.",
            f"{'Hoards' if p.extreme_cost > 1.5 else 'Lightly saves' if p.extreme_cost > 0.5 else 'Does not save'} "
            f"extreme cards for the burst.",
            f"Blocks threats when worth {p.veto_threshold:.0f}+ "
            f"(weight {p.deny_weight:.2f}, watching anyone within "
            f"{p.danger_margin} of the threshold).",
        ]


class Bluffer(Bot):
    name = "bluffer"

    def __init__(self, params: BluffParams | None = None,
                 label: str = "bluffer"):
        self.p = params or BluffParams()
        self.name = label

    def new_game(self, seat, cfg, rng):
        super().new_game(seat, cfg, rng)
        self.dir = 0

    def bursting(self, pub) -> bool:
        return pub.final or pub.round + 1 >= self.p.burst_round

    def play(self, seat, pub, hand):
        p = self.p
        t = pub.tracks[seat]
        counts = unseen_counts(pub, hand)
        others = others_drift(pub, seat, counts, p.trust)
        if t:
            self.dir = sign(t)
        elif not self.dir:
            self.dir = 1 if (drift_room(pub, 1, others, p.room_margin)
                             >= drift_room(pub, -1, others, p.room_margin)) \
                else -1
        d = self.dir
        burst = self.bursting(pub)
        if burst:
            need = (pub.cfg.win_threshold - abs(t)) / pub.multiplier + 1
            room = drift_room(pub, d, others, p.burst_room_margin)
            desired = d * min(need, max(room, 0))
            cards = pick_total(pub, hand, pub.personal[seat] + desired,
                               p.card_cost)
        else:
            furthest = max(abs(x) for i, x in enumerate(pub.tracks)
                           if i != seat)
            ceiling = max(0, min(p.cap, furthest - p.shadow_gap))
            target_abs = min(ceiling, abs(t) + p.creep)
            own = d * (target_abs - abs(t))   # negative pulls back
            room = drift_room(pub, d, others, p.room_margin)
            if own > 0:
                own = min(own, max(room, 0))
            helper = -projected_tally(pub, 0, others)
            desired = (1 - p.help_weight) * own + p.help_weight * helper
            cards = pick_total(pub, hand, pub.personal[seat] + desired,
                               p.card_cost, p.extreme_cost)

        clue = self.truthful(pub, seat, cards)
        if burst:
            if self.rng.random() < p.burst_lie_rate:
                clue = -d * p.burst_claim
        elif self.rng.random() < p.creep_lie_rate:
            clue = 0
        return cards, clue

    def veto(self, seat, pub, hand, pocket):
        p = self.p
        t = pub.tracks[seat]
        return self.best_steal(
            pub, seat, hand, pocket, lambda s: abs(t + s) - abs(t),
            p.veto_threshold, p.trust, deny_weight=p.deny_weight,
            danger_margin=p.danger_margin)


def honest_twin(p: BluffParams) -> BluffParams:
    """The same plan with every lie switched off."""
    d = p.to_dict()
    d["creep_lie_rate"] = d["burst_lie_rate"] = 0.0
    return BluffParams(**d)
