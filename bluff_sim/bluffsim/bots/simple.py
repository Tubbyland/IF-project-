"""Hand-written strategies. Each one's heuristics are stated in its docstring.

Notation: t = my track, s = signed drift I would steal by vetoing, P = my
personal target, mult = 2 in the final round (else 1).
"""
from __future__ import annotations

from typing import Optional

from .base import (Bot, drift_room, estimate_drift, extreme_total, lie,
                   others_drift, pick_total, projected_tally, sign,
                   unseen_counts)


def _toward_zero(pub, seat):
    t = pub.tracks[seat]
    return lambda target, s, counts: abs(t) - abs(t + s)


def _away_from_zero(pub, seat):
    t = pub.tracks[seat]
    return lambda target, s, counts: abs(t + s) - abs(t)


def helper_desired_drift(pub, seat, hand, trust=0.7) -> float:
    """The drift that would bring the projected tally back to zero, given
    earlier clues and assuming later players play to target."""
    counts = unseen_counts(pub, hand)
    others = others_drift(pub, seat, counts, trust)
    return -projected_tally(pub, 0, others)


class Honest(Bot):
    """Plays the cards closest to its target. Truthful clue.
    Vetoes only when the steal moves it at least 6 toward zero."""
    name = "honest"
    veto_gain = 6

    def play(self, seat, pub, hand):
        cards = pick_total(pub, hand, pub.personal[seat])
        return cards, self.truthful(pub, seat, cards)

    def veto(self, seat, pub, hand, pocket):
        return self.best_steal(pub, seat, hand, pocket,
                               _toward_zero(pub, seat), self.veto_gain)


class GroupHelper(Honest):
    """Aims its own drift at whatever would bring the projected tally back to
    zero, reading earlier players' clues. Truthful clue. Vetoes like Honest."""
    name = "helper"

    def play(self, seat, pub, hand):
        d = helper_desired_drift(pub, seat, hand)
        cards = pick_total(pub, hand, pub.personal[seat] + d)
        return cards, self.truthful(pub, seat, cards)


class Drifter(Bot):
    """Pushes toward the nearer track extreme with its most extreme legal play.
    At zero it picks the side its hand reaches furthest. Misleads by shifting
    its clue two bands the other way ("much higher" becomes "close").
    Vetoes when the steal moves it 4+ further from zero."""
    name = "drifter"
    veto_gain = 4

    def direction(self, seat, pub, hand):
        t = pub.tracks[seat]
        if t:
            return sign(t)
        p = pub.personal[seat]
        hi = sum(extreme_total(pub, hand, 1)) - p
        lo = p - sum(extreme_total(pub, hand, -1))
        return 1 if hi >= lo else -1

    def play(self, seat, pub, hand):
        d = self.direction(seat, pub, hand)
        cards = extreme_total(pub, hand, d)
        return cards, lie(self.truthful(pub, seat, cards), -d, 2)

    def veto(self, seat, pub, hand, pocket):
        return self.best_steal(pub, seat, hand, pocket,
                               _away_from_zero(pub, seat), self.veto_gain)


class Anchor(Bot):
    """Plays to land its track on zero (drift = -t / mult).
    Clue: if the projected tally leans one way, claims "much" the other way,
    so helpers who believe it push the tally further toward a bust.
    Vetoes when the steal moves it 3+ toward zero."""
    name = "anchor"
    veto_gain = 3

    def play(self, seat, pub, hand):
        t = pub.tracks[seat]
        cards = pick_total(pub, hand, pub.personal[seat] - t / pub.multiplier)
        counts = unseen_counts(pub, hand, cards)
        others = others_drift(pub, seat, counts)
        lean = sign(projected_tally(pub, sum(cards) - pub.personal[seat],
                                    others))
        clue = -2 * lean if lean else self.truthful(pub, seat, cards)
        return cards, clue

    def veto(self, seat, pub, hand, pocket):
        return self.best_steal(pub, seat, hand, pocket,
                               _toward_zero(pub, seat), self.veto_gain)


class CarefulDrifter(Bot):
    """Seat 1 of the main experiment. Chases +/-30 without busting the group.

    Direction: its track's sign; at zero, the side with more tally room.
    Wanted drift: what is left to the threshold (halved in the final round),
    at most `per_round` per round before the last two rounds.
    Bust guard: never drifts past the projected tally's room, keeping
    `margin` in reserve; if there is no room it gives up to 3 the other way.
    Clue: truthful, so helpers can absorb its drift.
    Vetoes when the steal moves it 4+ further from zero."""
    name = "careful_drifter"
    per_round = 10
    margin = 3
    veto_gain = 4

    def play(self, seat, pub, hand):
        t = pub.tracks[seat]
        counts = unseen_counts(pub, hand)
        others = others_drift(pub, seat, counts)
        if t:
            d = sign(t)
        else:
            up = drift_room(pub, 1, others, self.margin)
            down = drift_room(pub, -1, others, self.margin)
            d = 1 if up >= down else -1
        need = (pub.cfg.win_threshold - abs(t)) / pub.multiplier
        want = need if pub.rounds_left <= 1 else min(need, self.per_round)
        room = drift_room(pub, d, others, self.margin)
        amount = max(-3, min(want, room))
        cards = pick_total(pub, hand, pub.personal[seat] + d * amount)
        return cards, self.truthful(pub, seat, cards)

    def veto(self, seat, pub, hand, pocket):
        return self.best_steal(pub, seat, hand, pocket,
                               _away_from_zero(pub, seat), self.veto_gain)


class Opportunist(Bot):
    """Switches goal by standing, re-checked every turn:
      - drift (as CarefulDrifter, margin 2) when |t| >= 18, or when it leads
        with |t| >= 12 and at most 2 rounds remain;
      - anchor when it is strictly closest to zero and someone is 6+ further
        out;
      - otherwise group helper.
    Vetoes by the same goal: drift mode steals outward (gain 4+), anchor mode
    steals inward (gain 3+), helper mode vetoes a leader whose drift points
    outward, weighing that denial against any push on its own track (gain 5+).
    """
    name = "opportunist"

    def mode(self, seat, pub):
        a = [abs(x) for x in pub.tracks]
        me = a[seat]
        if me >= 18 or (pub.rounds_left <= 2 and me == max(a) and me >= 12):
            return "drift"
        others = [x for i, x in enumerate(a) if i != seat]
        if me < min(others) and max(others) >= me + 6:
            return "anchor"
        return "help"

    def play(self, seat, pub, hand):
        m = self.mode(seat, pub)
        if m == "drift":
            bot = CarefulDrifter()
            bot.margin = 2
            return bot.play(seat, pub, hand)
        if m == "anchor":
            return Anchor().play(seat, pub, hand)
        return GroupHelper().play(seat, pub, hand)

    def veto(self, seat, pub, hand, pocket):
        m = self.mode(seat, pub)
        if m == "drift":
            return self.best_steal(pub, seat, hand, pocket,
                                   _away_from_zero(pub, seat), 4)
        if m == "anchor":
            return self.best_steal(pub, seat, hand, pocket,
                                   _toward_zero(pub, seat), 3)
        t = pub.tracks[seat]

        def gain(target, s, counts):
            if target not in pub.leaders:
                return float("-inf")
            lt = pub.tracks[target]
            deny = abs(s) if sign(s) == sign(lt) else 0
            return deny - 0.5 * max(0, abs(t + s) - abs(t))
        return self.best_steal(pub, seat, hand, pocket, gain, 5)
