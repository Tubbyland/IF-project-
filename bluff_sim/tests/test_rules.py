"""Rule resolution tests. Run from bluff_sim/: python -m pytest tests"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bluffsim.bots import STRATEGIES, make_table  # noqa: E402
from bluffsim.bots.base import Bot  # noqa: E402
from bluffsim.config import GameConfig  # noqa: E402
from bluffsim.engine import (END_BUST, END_BUST_NO_WINNER, END_SHARED,  # noqa: E402
                             END_SOLO, RuleViolation, check_end, clue_for,
                             leaders_and_eligible, play_game, resolve_round)

CFG = GameConfig()
P = [20, 20, 20, 20]          # personal targets
C = 80                        # collective target equal to sum(P)


def resolve(totals, vetoes=None, tracks=(0, 0, 0, 0), tally=0, final=False,
            cfg=CFG, collective=C, personal=P):
    return resolve_round(cfg, list(tracks), tally, personal, collective,
                         totals, vetoes or {}, final)


class NoVeto(unittest.TestCase):
    def test_own_drift_goes_to_own_track(self):
        r = resolve([25, 18, 20, 21])
        self.assertEqual(r.tracks, [5, -2, 0, 1])
        self.assertEqual(r.tally_delta, 84 - 80)
        self.assertEqual(r.tally, 4)


class SingleVeto(unittest.TestCase):
    def test_vetoer_takes_drift_and_target_keeps_track(self):
        r = resolve([27, 20, 20, 20], {1: 0}, tracks=(15, 2, 0, 0))
        self.assertEqual(r.tracks, [15, 9, 0, 0])
        self.assertEqual(r.stolen, [(1, 0, 7)])

    def test_single_veto_keeps_real_group_contribution(self):
        r = resolve([27, 20, 20, 20], {1: 0})
        self.assertEqual(r.contributions, [27, 20, 20, 20])
        self.assertEqual(r.tally, 7)

    def test_negative_drift_is_copied_with_sign(self):
        r = resolve([12, 20, 20, 20], {2: 0})
        self.assertEqual(r.tracks, [0, 0, -8, 0])

    def test_pass_is_not_a_veto(self):
        r = resolve([27, 20, 20, 20], {1: None})
        self.assertEqual(r.tracks, [7, 0, 0, 0])

    def test_vetoer_takes_only_target_own_drift_in_a_chain(self):
        # 1 vetoes 0, 2 vetoes 1. Seat 1 gets 0's drift; seat 2 gets only
        # seat 1's own pocket drift (-3), not what seat 1 stole.
        r = resolve([30, 17, 20, 20], {1: 0, 2: 1})
        self.assertEqual(r.tracks, [0, 10, -3, 0])


class DoubleVeto(unittest.TestCase):
    def test_each_vetoer_gets_full_drift(self):
        r = resolve([32, 20, 20, 20], {1: 0, 2: 0})
        self.assertEqual(r.tracks, [0, 12, 12, 0])

    def test_group_contribution_becomes_personal_target(self):
        r = resolve([32, 20, 20, 20], {1: 0, 2: 0})
        self.assertEqual(r.contributions, [20, 20, 20, 20])
        self.assertEqual(r.tally, 0)

    def test_triple_veto(self):
        r = resolve([10, 20, 20, 20], {1: 0, 2: 0, 3: 0})
        self.assertEqual(r.tracks, [0, -10, -10, -10])
        self.assertEqual(r.tally, 0)


class VetoModes(unittest.TestCase):
    def test_block_cancels_drift_and_vetoer_gets_nothing(self):
        cfg = CFG.with_(veto_mode="block")
        r = resolve([30, 20, 20, 20], {1: 0}, tracks=(15, 2, 0, 0), cfg=cfg)
        self.assertEqual(r.tracks, [15, 2, 0, 0])
        self.assertEqual(r.stolen, [])
        self.assertEqual(r.tally, 10)          # single veto: real total

    def test_block_double_veto_still_zeroes_group_drift(self):
        cfg = CFG.with_(veto_mode="block")
        r = resolve([30, 20, 20, 20], {1: 0, 2: 0}, cfg=cfg)
        self.assertEqual(r.tracks, [0, 0, 0, 0])
        self.assertEqual(r.tally, 0)

    def test_choose_lets_each_vetoer_decide(self):
        cfg = CFG.with_(veto_mode="choose")
        r = resolve_round(cfg, [0] * 4, 0, P, C, [30, 20, 20, 20],
                          {1: 0, 2: 0}, False, takes={1: True, 2: False})
        self.assertEqual(r.tracks, [0, 10, 0, 0])

    def test_veto_cost_discards_cards(self):
        sizes = {}

        class AlwaysVeto(Bot):
            name = "always"

            def play(self, seat, pub, hand):
                sizes[(pub.round, seat)] = len(hand)
                return (sorted(hand)[-1],), 0

            def veto(self, seat, pub, hand, pocket):
                return next(x for x in pub.leaders if x != seat)
        cfg = CFG.with_(veto_cost=1, veto_gap=1, bust_limit=1000,
                        win_threshold=1000)
        r = play_game(cfg, [AlwaysVeto() for _ in range(4)], seed=4)
        vetoed = [(rec.round, v) for rec in r.records
                  for v, t in rec.vetoes.items() if t is not None]
        self.assertTrue(vetoed)
        for rnd, v in vetoed:
            if (rnd + 1, v) in sizes:
                # played 1, paid 1, drew 1: one card fewer next round
                self.assertEqual(sizes[(rnd + 1, v)], sizes[(rnd, v)] - 1)


class FinalRound(unittest.TestCase):
    def test_own_drift_doubled(self):
        r = resolve([25, 20, 20, 20], final=True)
        self.assertEqual(r.tracks, [10, 0, 0, 0])

    def test_stolen_drift_doubled_by_default(self):
        r = resolve([25, 20, 20, 20], {1: 0}, final=True)
        self.assertEqual(r.tracks, [0, 10, 0, 0])

    def test_stolen_drift_not_doubled_when_switched_off(self):
        cfg = CFG.with_(final_doubles_stolen=False)
        r = resolve([25, 20, 20, 20], {1: 0}, final=True, cfg=cfg)
        self.assertEqual(r.tracks, [0, 5, 0, 0])

    def test_tally_not_doubled(self):
        r = resolve([25, 20, 20, 20], final=True)
        self.assertEqual(r.tally, 5)

    def test_shared_win_when_nothing_else_happens(self):
        r = resolve([20, 20, 20, 20], final=True)
        self.assertEqual((r.end_type, r.winners), (END_SHARED, (0, 1, 2, 3)))

    def test_no_shared_win_before_final_round(self):
        r = resolve([20, 20, 20, 20])
        self.assertIsNone(r.end_type)


class EndConditions(unittest.TestCase):
    def test_simultaneous_solo_crossing_furthest_wins(self):
        r = resolve([20, 20, 20, 20], tracks=(31, -34, 5, 0))
        self.assertEqual((r.end_type, r.winners), (END_SOLO, (1,)))

    def test_simultaneous_solo_crossing_tie_is_shared(self):
        r = resolve([25, 15, 20, 20], tracks=(27, -27, 0, 0))
        self.assertEqual(r.tracks[:2], [32, -32])
        self.assertEqual((r.end_type, r.winners), (END_SOLO, (0, 1)))

    def test_exactly_threshold_is_a_solo_win(self):
        r = resolve([30, 20, 20, 20], tracks=(20, 0, 0, 0), tally=-10)
        self.assertEqual((r.end_type, r.winners), (END_SOLO, (0,)))

    def test_bust_beats_same_round_solo(self):
        r = resolve([35, 20, 20, 20], tracks=(20, 3, -1, 6), tally=10)
        self.assertEqual(r.tracks[0], 35)
        self.assertEqual((r.end_type, r.winners), (END_BUST, (2,)))

    def test_tally_at_limit_is_not_a_bust(self):
        r = resolve([20, 20, 20, 20], tally=20)
        self.assertIsNone(r.end_type)
        r = resolve([21, 20, 20, 20], tally=20)
        self.assertEqual(r.end_type, END_BUST)

    def test_negative_bust(self):
        r = resolve([20, 20, 20, 20], tally=-15, collective=86)
        self.assertEqual(r.tally, -21)
        self.assertEqual(r.end_type, END_BUST)

    def test_bust_ties_shared(self):
        _, w = check_end(CFG, [4, -4, 10, 9], 25, False)
        self.assertEqual(w, (0, 1))

    def test_bust_near_zero_rule(self):
        cfg = CFG.with_(bust_win_requires_near_zero=True)
        self.assertEqual(check_end(cfg, [6, -7, 10, 9], 25, False),
                         (END_BUST_NO_WINNER, ()))
        self.assertEqual(check_end(cfg, [5, -7, 10, 9], 25, False),
                         (END_BUST, (0,)))

    def test_track_cap(self):
        cfg = CFG.with_(track_cap=30)
        r = resolve([40, 20, 20, 20], tracks=(25, 0, 0, 0), tally=-20, cfg=cfg)
        self.assertEqual(r.tracks[0], 30)


class Eligibility(unittest.TestCase):
    def test_nobody_eligible_at_start(self):
        self.assertEqual(leaders_and_eligible(CFG, [0, 0, 0, 0]),
                         ([0, 1, 2, 3], []))

    def test_gap_rule(self):
        leaders, elig = leaders_and_eligible(CFG, [-14, 4, 5, 0])
        self.assertEqual(leaders, [0])
        self.assertEqual(elig, [1, 3])

    def test_vetoes_switched_off(self):
        cfg = CFG.with_(vetoes_enabled=False)
        self.assertEqual(leaders_and_eligible(cfg, [-14, 4, 5, 0])[1], [])
        r = play_game(cfg, make_table(["drifter", "anchor", "opportunist",
                                       "adaptive"]), 5)
        self.assertTrue(all(not rec.vetoes for rec in r.records))

    def test_tied_leaders_both_ineligible(self):
        leaders, elig = leaders_and_eligible(CFG, [12, -12, 2, 1])
        self.assertEqual(leaders, [0, 1])
        self.assertEqual(elig, [2, 3])


class Clues(unittest.TestCase):
    def test_bands(self):
        got = [clue_for(d, CFG) for d in (-9, -8, -7, -3, -2, 0, 2, 3, 7, 8)]
        self.assertEqual(got, [-2, -2, -1, -1, 0, 0, 0, 1, 1, 2])


class Decks(unittest.TestCase):
    def test_default_deck_is_80_cards(self):
        self.assertEqual(len(CFG.hand_deck()), 80)

    def test_deck_grows_so_it_never_runs_out(self):
        cfg = CFG.with_(n_players=5, draw_per_round=2)
        self.assertGreaterEqual(len(cfg.hand_deck()), cfg.cards_needed())
        self.assertEqual(cfg.effective_hand_copies(), 5)

    def test_fixed_deck_too_small_is_rejected(self):
        cfg = CFG.with_(n_players=5, draw_per_round=2, hand_copies_auto=False)
        with self.assertRaises(ValueError):
            cfg.validate()

    def test_personal_targets_reshuffle(self):
        cfg = CFG.with_(n_players=5)   # 35 draws from a 32-card deck
        r = play_game(cfg, make_table(["honest"] * 5), seed=3)
        self.assertTrue(r.records)


class Greedy(Bot):
    name = "greedy"

    def play(self, seat, pub, hand):
        return tuple(sorted(hand))[-4:], 0


class Engine(unittest.TestCase):
    def test_max_cards_enforced(self):
        with self.assertRaises(RuleViolation):
            play_game(CFG, [Greedy() for _ in range(4)], seed=1)

    def test_all_strategies_play_legal_games(self):
        names = [n for n in STRATEGIES]
        for n_players, extra in ((3, {}), (4, {}), (5, {}),
                                 (4, {"veto_mode": "block"}),
                                 (4, {"veto_mode": "choose"}),
                                 (4, {"veto_cost": 1})):
            cfg = CFG.with_(n_players=n_players, **extra)
            for seed in range(40):
                table = [names[(seed + i) % len(names)]
                         for i in range(n_players)]
                r = play_game(cfg, make_table(table), seed)
                self.assertIn(r.end_type, (END_BUST, END_SOLO, END_SHARED))
                self.assertLessEqual(r.rounds_played, cfg.rounds)

    def test_same_seed_same_game(self):
        table = ["careful_drifter", "anchor", "adaptive", "opportunist"]
        a = play_game(CFG, make_table(table), 42)
        b = play_game(CFG, make_table(table), 42)
        self.assertEqual(a.tracks, b.tracks)
        self.assertEqual(a.winners, b.winners)

    def test_record_is_consistent(self):
        r = play_game(CFG, make_table(["drifter", "anchor", "helper",
                                       "opportunist"]), 7)
        tally = 0
        for rec in r.records:
            self.assertEqual(rec.tally_before, tally)
            for cards in rec.cards:
                self.assertTrue(1 <= len(cards) <= 3)
            tally = rec.tally_after
        self.assertEqual(tally, r.tally)


if __name__ == "__main__":
    unittest.main()
