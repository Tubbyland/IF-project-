"""Screen card ranges, target ranges, thresholds and game length.

Each rule set is played by two tables with different temperaments:
  competitive  careful_drifter, careful_drifter, anchor, opportunist
  cooperative  helper, helper, opportunist, anchor
Measures (per table, then combined):
  mix        how close solo / bust / shared is to the target (40/40/20):
             1 - half the summed absolute differences (1 = exact)
  comeback   share of outright wins taken by a player who was behind at
             the halfway point
  reach      share of games that reach the last round
  final      share of games won outright in the last round
Score = 0.5 x mix (on the worse table) + 0.2 x comeback + 0.15 x reach
        + 0.15 x final  (averaged over the two tables).
The weights are a starting point; the CSV has every measure so any
weighting can be recomputed.

Run from bluff_sim/:  python scripts/screen_ranges.py [--games N]
"""
import argparse
import csv
import itertools
import os
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np  # noqa: E402

from bluffsim import charts  # noqa: E402
from bluffsim.bots import make_table  # noqa: E402
from bluffsim.config import GameConfig  # noqa: E402
from bluffsim.engine import END_BUST, END_SHARED, END_SOLO, play_game  # noqa: E402
from bluffsim.stats import summarise  # noqa: E402

TARGET = {"solo": 0.4, "bust": 0.4, "shared": 0.2}
TABLES = {
    "competitive": ["careful_drifter", "careful_drifter", "anchor",
                    "opportunist"],
    "cooperative": ["helper", "helper", "opportunist", "anchor"],
}
GRID = {
    "hand_hi": [12, 15, 18],
    "coll_half_width": [6, 10, 15],
    "rounds": [5, 6, 7],
    "bust_limit": [10, 14, 18, 22],
    "win_threshold": [16, 20, 25, 30],
    "draw_per_round": [1, 2],
}
PERSONAL = (10, 20)


def make_cfg(p: dict) -> GameConfig:
    lo, hi = PERSONAL
    centre = round(4 * (lo + hi) / 2)
    w = p["coll_half_width"]
    return GameConfig(
        hand_lo=1, hand_hi=p["hand_hi"], personal_lo=lo, personal_hi=hi,
        collective_mode="continuous",
        collective_continuous=(centre - w, centre + w),
        rounds=p["rounds"], bust_limit=p["bust_limit"],
        win_threshold=p["win_threshold"],
        draw_per_round=p["draw_per_round"],
        veto_gap=max(1, round(p["win_threshold"] / 3)))


def job(args):
    p, table, games, seed = args
    cfg = make_cfg(p)
    cfg.validate()
    bots = make_table(TABLES[table])
    res = [play_game(cfg, bots, seed * 1_000_003 + i) for i in range(games)]
    s = summarise(cfg, res)
    n = s.n
    solo = s.end_types[END_SOLO] / n
    bust = s.end_types[END_BUST] / n
    shared = s.end_types[END_SHARED] / n
    mix = 1 - 0.5 * (abs(solo - TARGET["solo"]) + abs(bust - TARGET["bust"])
                     + abs(shared - TARGET["shared"]))
    rates = [v["competitive"] for v in s.strategy_rates.values()]
    return p, table, {
        "solo": solo, "bust": bust, "shared": shared, "mix": mix,
        "comeback": s.tension["comeback_half"],
        "reach": s.reached_final, "final": s.tension["final_decided"],
        "length": s.avg_length,
        "top_strategy_share": max(rates) / max(1e-9, np.mean(rates)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=51)
    ap.add_argument("--out", default="results/screen_ranges")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    keys = list(GRID)
    points = [dict(zip(keys, v)) for v in itertools.product(*GRID.values())]
    jobs = [(p, t, args.games, args.seed) for p in points for t in TABLES]
    print(f"{len(points)} rule sets x {len(TABLES)} tables x {args.games} "
          f"games", flush=True)
    by_point = {}
    with ProcessPoolExecutor(args.workers) as ex:
        for i, (p, table, m) in enumerate(ex.map(job, jobs, chunksize=4)):
            by_point.setdefault(tuple(p.values()), {})[table] = m
            if (i + 1) % 200 == 0:
                print(f"  {i + 1}/{len(jobs)}", flush=True)

    rows = []
    for vals, per in by_point.items():
        row = dict(zip(keys, vals))
        for t, m in per.items():
            for k, v in m.items():
                row[f"{t}_{k}"] = v
        avg = {k: np.mean([per[t][k] for t in TABLES])
               for k in per["competitive"]}
        row.update({k: avg[k] for k in avg})
        row["mix_worst"] = min(per[t]["mix"] for t in TABLES)
        row["score"] = (0.5 * row["mix_worst"] + 0.2 * avg["comeback"]
                        + 0.15 * avg["reach"] + 0.15 * avg["final"])
        rows.append(row)
    rows.sort(key=lambda r: -r["score"])

    with open(os.path.join(args.out, "screen.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    def pct(x):
        return f"{100 * x:.0f}%"

    cols = keys + ["score", "solo", "bust", "shared", "mix_worst",
                   "comeback", "reach", "final", "length"]
    lines = ["# Screening card ranges, thresholds and length", "",
             f"Personal targets {PERSONAL[0]}-{PERSONAL[1]}; collective "
             "targets continuous around 60; hand cards 1 to hand_hi. "
             f"{args.games} games per table per rule set. Endings and "
             "measures are averaged over the two tables; mix_worst is the "
             "worse table's.", "", "## Top 25", "",
             "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows[:25]:
        cells = []
        for c in cols:
            v = r[c]
            if c in ("solo", "bust", "shared", "comeback", "reach", "final"):
                cells.append(pct(v))
            elif isinstance(v, float):
                cells.append(f"{v:.2f}")
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")

    lines += ["", "## Effect of each setting (mean over all other settings)",
              ""]
    for k in keys:
        lines.append(f"**{k}**")
        lines.append("")
        lines.append("| value | score | solo | bust | shared | comeback | "
                     "reach last round | won in last round | length |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for v in GRID[k]:
            sub = [r for r in rows if r[k] == v]
            m = {c: np.mean([r[c] for r in sub]) for c in
                 ("score", "solo", "bust", "shared", "comeback", "reach",
                  "final", "length")}
            lines.append(
                f"| {v} | {m['score']:.3f} | {pct(m['solo'])} | "
                f"{pct(m['bust'])} | {pct(m['shared'])} | "
                f"{pct(m['comeback'])} | {pct(m['reach'])} | "
                f"{pct(m['final'])} | {m['length']:.2f} |")
        lines.append("")

    lines += ["## Best rule set for each number of rounds", ""]
    for n in GRID["rounds"]:
        best = next(r for r in rows if r["rounds"] == n)
        lines.append(
            f"- {n} rounds: score {best['score']:.3f}, endings "
            f"{pct(best['solo'])} / {pct(best['bust'])} / "
            f"{pct(best['shared'])}, comeback {pct(best['comeback'])}, "
            f"reach last {pct(best['reach'])}, won in last "
            f"{pct(best['final'])} — " + ", ".join(
                f"{k}={best[k]}" for k in keys if k != "rounds"))
    with open(os.path.join(args.out, "screen.md"), "w") as f:
        f.write("\n".join(lines) + "\n")

    for k in keys:
        charts.sweep_lines(rows, k, os.path.join(args.out,
                                                 f"endings_vs_{k}.png"),
                           "mean over other settings")
    charts.sweep_heatmap(rows, "win_threshold", "bust_limit", "mix_worst",
                         os.path.join(args.out, "mix_threshold_x_bust.png"),
                         "Ending-mix score (worse table)")
    print("\n".join(lines[:40]))


if __name__ == "__main__":
    main()
