"""A parameterised policy for the tuned seats.

Each turn it picks a goal from its standing:
  solo   |t| >= solo_at (final round: final_solo_at). Drift away from zero
         by up to `aggr_early`/`aggr_late` per round (the late value from
         round `late_round` on), or exactly what is left to the threshold in
         the final round. Never past the tally's room minus `room_margin`.
  anchor strictly closest to zero and someone is `anchor_margin`+ further
         out. Drift back to zero.
  group  otherwise. Hold its track where it is.
Its wanted drift is then blended with the helper's (bring the projected
tally to zero) by `help_weight`, and it plays the cards closest to that,
paying `card_cost` per card and `extreme_cost` for spending extreme cards.

Clue: truthful, except with probability `lie_rate` it shifts the clue
`lie_size` bands. In solo/group mode the shift hides its drift (points the
other way). In anchor mode it points against the tally's lean, to make
helpers push the tally toward a bust.

Veto: for each candidate, gain = change in its own goal (outward in solo
mode, inward otherwise) + `deny_weight` x the leader's outward drift it
would cancel. Vetoes the best candidate if gain >= veto_threshold.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .base import (Bot, drift_room, lie, others_drift, pick_total,
                   projected_tally, sign, unseen_counts)
from .params import TunableParams

# name -> (low, high, is_int)
BOUNDS = {
    "solo_at": (0, 30, True),
    "anchor_margin": (2, 30, True),
    "aggr_early": (0, 20, False),
    "aggr_late": (0, 30, False),
    "late_round": (1, 7, True),
    "room_margin": (-10, 15, False),
    "help_weight": (0, 1, False),
    "lie_rate": (0, 1, False),
    "lie_size": (1, 3, True),
    "veto_threshold": (0, 20, False),
    "deny_weight": (0, 1.5, False),
    "trust": (0, 1, False),
    "card_cost": (-3, 3, False),
    "extreme_cost": (0, 4, False),
    "final_solo_at": (0, 30, True),
    "final_room_margin": (-10, 15, False),
    "final_help_weight": (0, 1, False),
    "final_veto_threshold": (0, 20, False),
    # 0: only leaders are blocked. Above 0: also anyone whose track would
    # end the round within this distance of the solo threshold.
    "danger_margin": (0, 30, True),
}


@dataclass
class Params(TunableParams):
    BOUNDS: ClassVar[dict] = BOUNDS

    solo_at: int = 15
    anchor_margin: int = 8
    aggr_early: float = 6.0
    aggr_late: float = 12.0
    late_round: int = 5
    room_margin: float = 3.0
    help_weight: float = 0.3
    lie_rate: float = 0.2
    lie_size: int = 1
    veto_threshold: float = 5.0
    deny_weight: float = 0.5
    trust: float = 0.7
    card_cost: float = 0.0
    extreme_cost: float = 0.5
    final_solo_at: int = 12
    final_room_margin: float = 2.0
    final_help_weight: float = 0.2
    final_veto_threshold: float = 5.0
    danger_margin: int = 0

    def describe(self) -> list[str]:
        p = self
        out = []
        if p.solo_at <= 2:
            out.append("Always plays for a solo win.")
        elif p.solo_at >= 28:
            out.append("Almost never commits to a solo win before the "
                       "final round.")
        else:
            out.append(f"Commits to a solo win once its track is {p.solo_at}+"
                       f" from zero.")
        out.append(f"When chasing it, drifts up to {p.aggr_early:.0f} a round "
                   f"before round {p.late_round}, then up to "
                   f"{p.aggr_late:.0f}.")
        if p.room_margin < 0:
            out.append(f"Will drift {abs(p.room_margin):.0f} past the point "
                       f"where the tally is projected to bust.")
        else:
            out.append(f"Keeps {p.room_margin:.0f} of room between the "
                       f"projected tally and a bust.")
        if p.anchor_margin >= 28:
            out.append("Rarely plays as an anchor.")
        else:
            out.append(f"Anchors at zero when it is closest to zero and "
                       f"someone is {p.anchor_margin}+ further out.")
        out.append(f"Gives {p.help_weight:.0%} weight to closing the group's "
                   f"gap ({p.final_help_weight:.0%} in the final round).")
        if p.lie_rate < 0.05:
            out.append("Almost always tells the truth.")
        else:
            out.append(f"Lies on {p.lie_rate:.0%} of clues, by {p.lie_size} "
                       f"band{'s' if p.lie_size > 1 else ''}.")
        out.append(f"Believes others' clues {p.trust:.0%}.")
        out.append(f"Vetoes when the steal is worth {p.veto_threshold:.0f}+ "
                   f"to its goal ({p.final_veto_threshold:.0f}+ in the final "
                   f"round); counts blocking a leader at "
                   f"{p.deny_weight:.0%} of its size.")
        if p.card_cost > 0.5:
            out.append("Prefers playing few cards.")
        elif p.card_cost < -0.5:
            out.append("Prefers playing many cards.")
        if p.extreme_cost > 1.5:
            out.append("Hoards very high and very low cards.")
        if p.danger_margin:
            out.append(f"Also blocks any player it expects to end the round "
                       f"within {p.danger_margin} of the solo threshold, "
                       f"leader or not.")
        out.append(f"In the final round, goes for the solo win if its track "
                   f"is {p.final_solo_at}+ from zero, keeping "
                   f"{p.final_room_margin:.0f} of tally room.")
        return out


class Adaptive(Bot):
    name = "adaptive"

    def __init__(self, params: Params | None = None, label: str = "adaptive"):
        self.p = params or Params()
        self.name = label

    def mode(self, seat, pub) -> str:
        p = self.p
        a = [abs(x) for x in pub.tracks]
        me = a[seat]
        solo_at = p.final_solo_at if pub.final else p.solo_at
        if me >= solo_at:
            return "solo"
        others = [x for i, x in enumerate(a) if i != seat]
        if me < min(others) and max(others) >= me + p.anchor_margin:
            return "anchor"
        return "group"

    def play(self, seat, pub, hand):
        p = self.p
        t = pub.tracks[seat]
        mode = self.mode(seat, pub)
        counts = unseen_counts(pub, hand)
        others = others_drift(pub, seat, counts, p.trust)
        margin = p.final_room_margin if pub.final else p.room_margin
        hw = p.final_help_weight if pub.final else p.help_weight

        if mode == "solo":
            if t:
                d = sign(t)
            else:
                d = 1 if (drift_room(pub, 1, others, margin)
                          >= drift_room(pub, -1, others, margin)) else -1
            need = (pub.cfg.win_threshold - abs(t)) / pub.multiplier
            if pub.final:
                want = need
            else:
                aggr = p.aggr_late if pub.round + 1 >= p.late_round \
                    else p.aggr_early
                want = min(need, aggr)
            room = drift_room(pub, d, others, margin)
            own = d * max(-3, min(want, room))
        elif mode == "anchor":
            own = -t / pub.multiplier
        else:
            own = 0.0

        helper = -projected_tally(pub, 0, others)
        desired = (1 - hw) * own + hw * helper
        cards = pick_total(pub, hand, pub.personal[seat] + desired,
                           p.card_cost, p.extreme_cost)

        clue = self.truthful(pub, seat, cards)
        if self.rng.random() < p.lie_rate:
            drift = sum(cards) - pub.personal[seat]
            if mode == "anchor":
                lean = sign(projected_tally(pub, drift, others))
                direction = -lean or self.rng.choice((-1, 1))
            else:
                direction = -sign(drift) or self.rng.choice((-1, 1))
            clue = lie(clue, direction, p.lie_size)
        return cards, clue

    def veto(self, seat, pub, hand, pocket):
        p = self.p
        t = pub.tracks[seat]
        outward = self.mode(seat, pub) == "solo"
        threshold = p.final_veto_threshold if pub.final else p.veto_threshold

        def own(s):
            return (abs(t + s) - abs(t)) if outward else (abs(t) - abs(t + s))
        return self.best_steal(pub, seat, hand, pocket, own, threshold,
                               p.trust, deny_weight=p.deny_weight,
                               danger_margin=p.danger_margin)
