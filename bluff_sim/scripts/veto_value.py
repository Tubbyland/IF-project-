"""Is vetoing a winning strategy? Compare veto rules (draw 2).

For each rule, take the strategy tuned under it (best_response.json) and
build a twin that is identical except it never vetoes. Then, on the same
deals:
  A. against the fixed bots (careful_drifter, anchor): tuned seats 3 and 4
     with and without vetoing;
  B. in a field of four tuned copies: does one seat gain by not vetoing?
     And in a field of non-vetoers, does one seat gain by vetoing?
Run from bluff_sim/:  python scripts/veto_value.py [--games N]
"""
import argparse
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bluffsim.bots.adaptive import Adaptive, Params  # noqa: E402
from bluffsim.config import GameConfig  # noqa: E402
from bluffsim.stats import run_games  # noqa: E402
from bluffsim.tune import Evaluator, _seeds  # noqa: E402

RULES = [
    ("no veto", {"vetoes_enabled": False}, "results/draw2_noveto"),
    ("take (current)", {}, "results/draw2"),
    ("block", {"veto_mode": "block"}, "results/veto_block"),
    ("choose", {"veto_mode": "choose"}, "results/veto_choose"),
    ("pay 1 card", {"veto_cost": 1}, "results/veto_pay"),
]
FIXED = ["careful_drifter", "anchor"]


def load(path):
    with open(os.path.join(path, "best_response.json")) as f:
        return Params.from_dict(json.load(f)["params"])


def never_vetoes(p: Params) -> Params:
    d = p.to_dict()
    d["veto_threshold"] = d["final_veto_threshold"] = 1e9
    return Params(**d)


def vs_fixed(p):
    a = Adaptive(p, "tuned")
    return [(FIXED + [a, a], [2, 3])]


def deviant(dev, field, n=4):
    tables = []
    for seat in range(n):
        specs = [Adaptive(field, "field") for _ in range(n)]
        specs[seat] = Adaptive(dev, "deviant")
        tables.append((specs, [seat]))
    return tables


def veto_stats(cfg, p, games, seed):
    a = Adaptive(p, "tuned")
    res = run_games(cfg, FIXED + [a, a], games, seed)
    vetoes = decisive = 0
    by = {}
    for r in res:
        for rec in r.records:
            for v, t in rec.vetoes.items():
                if t is not None and v in (2, 3):
                    vetoes += 1
                    by[r.strategies[t]] = by.get(r.strategies[t], 0) + 1
        decisive += sum(1 for v, _, _ in r.decisive_steals if v in (2, 3))
    n = len(res)
    wins = {s: sum(1 for r in res if i in r.winners) / n
            for i, s in enumerate(["careful_drifter", "anchor"])}
    return vetoes / n, decisive / n, by, wins


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=31)
    ap.add_argument("--out", default="results/veto_value.md")
    args = ap.parse_args()
    lines = ["# Is vetoing a winning strategy? (draw 2)", "",
             f"{args.games} games per cell, same deals within each rule. "
             "Win score: share of games won by the seat (ties count for "
             "each tied winner; shared wins count).", ""]
    a_rows, b_rows, s_rows = [], [], []
    for name, rule, path in RULES:
        if not os.path.exists(os.path.join(path, "best_response.json")):
            print(f"skip {name}: no tuned strategy in {path}")
            continue
        cfg = GameConfig(draw_per_round=2).with_(**rule)
        p = load(path)
        q = never_vetoes(p)
        ev = Evaluator(cfg)
        rng = random.Random(args.seed)
        try:
            seeds = _seeds(rng, args.games)
            if not cfg.vetoes_enabled:
                (s,) = ev.score([vs_fixed(p)], seeds)
                a_rows.append(f"| {name} | {s:.3f} | — | — |")
                print(name, s)
                continue
            s_p, s_q = ev.score([vs_fixed(p), vs_fixed(q)], seeds)
            seeds4 = seeds[: args.games // 4]
            own_p, dev_q, own_q, dev_p = ev.score(
                [deviant(p, p), deviant(q, p), deviant(q, q),
                 deviant(p, q)], seeds4)
        finally:
            ev.close()
        vpg, dpg, by, fixed_wins = veto_stats(cfg, p, args.games // 2,
                                              args.seed)
        a_rows.append(f"| {name} | {s_p:.3f} | {s_q:.3f} | "
                      f"{s_p - s_q:+.3f} |")
        b_rows.append(f"| {name} | {own_p:.3f} | {dev_q:.3f} "
                      f"({dev_q - own_p:+.3f}) | {own_q:.3f} | {dev_p:.3f} "
                      f"({dev_p - own_q:+.3f}) |")
        targets = ", ".join(f"{k} {v / max(1, sum(by.values())):.0%}"
                            for k, v in sorted(by.items()))
        s_rows.append(f"| {name} | {vpg:.2f} | {dpg:.3f} | {targets} | "
                      f"{fixed_wins['careful_drifter']:.1%} | "
                      f"{fixed_wins['anchor']:.1%} |")
        print(name, s_p, s_q, own_p, dev_q, own_q, dev_p, vpg, dpg)

    se = (0.25 / args.games) ** 0.5
    lines += ["## A. Against the fixed bots", "",
              "Tuned seats 3-4 with their vetoing switched on and off. "
              f"Differences under about {2 * se:.3f} are noise.", "",
              "| Rule | Tuned, vetoing | Same strategy, never vetoes | "
              "Value of vetoing |", "|---|---|---|---|", *a_rows, "",
              "## B. When everyone plays the tuned strategy", "",
              "Field of four copies. A positive change means the deviant "
              "gains by breaking from the field.", "",
              "| Rule | Vetoing field, own score | One non-vetoer in it | "
              "Non-vetoing field, own score | One vetoer in it |",
              "|---|---|---|---|---|", *b_rows, "",
              "## How the tuned seats use the veto (against the fixed bots)",
              "", "| Rule | Vetoes per game (seats 3-4) | Vetoes that "
              "decided the game, per game | Targets | Careful drifter wins "
              "| Anchor wins |", "|---|---|---|---|---|---|", *s_rows, ""]
    with open(args.out, "w") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
