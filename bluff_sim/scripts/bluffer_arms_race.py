"""The Bluffer against three tuned players, with both sides adapting.

Stages alternate:
  B1  tune the Bluffer (solo wins only) against three copies of the tuned
      player, who do not know a bluffer is at the table
  O1  re-tune the three (one shared parameter set, ordinary win score)
      against that Bluffer; they can learn to watch non-leaders and to
      distrust clues
  B2  re-tune the Bluffer against them, and so on.
The Bluffer's seat rotates through all four seats in every evaluation.
After each stage, all measures use the same validation deals.

Run from bluff_sim/:
    python scripts/bluffer_arms_race.py --rule block --out results/bluffer_block
"""
import argparse
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bluffsim import replay  # noqa: E402
from bluffsim.bots.adaptive import Adaptive, Params  # noqa: E402
from bluffsim.bots.bluffer import Bluffer, BluffParams, honest_twin  # noqa: E402
from bluffsim.config import GameConfig  # noqa: E402
from bluffsim.engine import END_SOLO, clue_for  # noqa: E402
from bluffsim.stats import run_games  # noqa: E402
from bluffsim.tune import Evaluator, _seeds, genetic_search  # noqa: E402

RULES = {
    "block": ({"veto_mode": "block"}, "results/veto_block"),
    "take": ({}, "results/draw2"),
    "none": ({"vetoes_enabled": False}, "results/draw2_noveto"),
}


def tables(cfg, bluff, opp, scored):
    """Bluffer in each seat in turn. scored: 'bluffer' or 'opponents'."""
    out = []
    for seat in range(cfg.n_players):
        specs = [Adaptive(opp, "tuned") for _ in range(cfg.n_players)]
        specs[seat] = Bluffer(bluff)
        who = ([seat] if scored == "bluffer" else
               [i for i in range(cfg.n_players) if i != seat])
        out.append((specs, who))
    return out


def ordinary_tables(cfg, opp):
    """A tuned player in the Bluffer's seat: the reference to beat."""
    return [([Adaptive(opp, "tuned") for _ in range(cfg.n_players)], [s])
            for s in range(cfg.n_players)]


def measure(cfg, bluff, opp, seeds, workers):
    solo = Evaluator(cfg, workers, shared_value=-1)
    win = Evaluator(cfg, workers, shared_value=1.0)
    try:
        b_solo, h_solo, ref_solo = solo.score(
            [tables(cfg, bluff, opp, "bluffer"),
             tables(cfg, honest_twin(bluff), opp, "bluffer"),
             ordinary_tables(cfg, opp)], seeds)
        b_win, o_win, ref_win = win.score(
            [tables(cfg, bluff, opp, "bluffer"),
             tables(cfg, bluff, opp, "opponents"),
             ordinary_tables(cfg, opp)], seeds)
    finally:
        solo.close()
        win.close()
    return {"bluffer_solo": b_solo, "honest_twin_solo": h_solo,
            "bluffer_any_win": b_win, "opponent_win": o_win,
            "ordinary_solo": ref_solo, "ordinary_win": ref_win}


def behaviour(cfg, bluff, opp, games, seed):
    """How the Bluffer's games go, from full game records (seat 1)."""
    specs = [Bluffer(bluff)] + [Adaptive(opp, "tuned")] * (cfg.n_players - 1)
    res = run_games(cfg, specs, games, seed)
    burst_rounds = blocked = lies = clues = solo = 0
    for r in res:
        b = Bluffer(bluff)
        for rec in r.records:
            truth = clue_for(rec.drifts[0], cfg)
            clues += 1
            lies += rec.clues[0] != truth
            final = rec.round == cfg.rounds - 1
            if final or rec.round + 1 >= bluff.burst_round:
                burst_rounds += 1
                blocked += any(t == 0 for t in rec.vetoes.values())
        solo += r.end_type == END_SOLO and 0 in r.winners
    return res, {"lie_rate": lies / max(1, clues),
                 "burst_rounds_per_game": burst_rounds / len(res),
                 "blocked_in_burst": blocked / max(1, burst_rounds),
                 "solo": solo / len(res)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rule", choices=RULES, default="block")
    ap.add_argument("--out", default=None)
    ap.add_argument("--rounds", type=int, default=2,
                    help="opponent re-tunes; the Bluffer gets one more")
    ap.add_argument("--pop", type=int, default=20)
    ap.add_argument("--gens", type=int, default=10)
    ap.add_argument("--seeds", type=int, default=300,
                    help="seeds per candidate; each played in all 4 seats")
    ap.add_argument("--validate", type=int, default=2500)
    ap.add_argument("--seed", type=int, default=41)
    ap.add_argument("--workers", type=int, default=None)
    args = ap.parse_args()
    rule, path = RULES[args.rule]
    out = args.out or f"results/bluffer_{args.rule}"
    os.makedirs(out, exist_ok=True)
    cfg = GameConfig(draw_per_round=2).with_(**rule)
    with open(os.path.join(path, "best_response.json")) as f:
        opp = Params.from_dict(json.load(f)["params"])
    bluff = BluffParams()
    rng = random.Random(args.seed)
    val_seeds = _seeds(random.Random(args.seed + 1), args.validate)
    log_lines = []

    def log(msg):
        print(msg, flush=True)
        log_lines.append(msg)

    stages = []

    def record(name):
        m = measure(cfg, bluff, opp, val_seeds, args.workers)
        stages.append((name, m, bluff, opp))
        log(f"  {name}: bluffer solo {m['bluffer_solo']:.3f} (no-lie twin "
            f"{m['honest_twin_solo']:.3f}, ordinary player "
            f"{m['ordinary_solo']:.3f}); bluffer any win "
            f"{m['bluffer_any_win']:.3f}; opponents {m['opponent_win']:.3f}")

    t0 = time.time()
    log(f"Rule: draw 2, {args.rule}. Opponents start from {path}.")
    record("start (untuned Bluffer)")
    for k in range(args.rounds + 1):
        log(f"B{k + 1}: tuning the Bluffer")
        ev = Evaluator(cfg, args.workers, shared_value=-1)
        try:
            res = genetic_search(
                lambda ps, seeds: ev.score(
                    [tables(cfg, p, opp, "bluffer") for p in ps], seeds),
                rng, [bluff, BluffParams()], args.pop, args.gens,
                args.seeds, args.validate // 2, log, space=BluffParams)
        finally:
            ev.close()
        bluff = res.best
        record(f"B{k + 1}")
        if k == args.rounds:
            break
        log(f"O{k + 1}: re-tuning the three opponents")
        ev = Evaluator(cfg, args.workers, shared_value=1.0)
        try:
            res = genetic_search(
                lambda ps, seeds: ev.score(
                    [tables(cfg, bluff, p, "opponents") for p in ps], seeds),
                rng, [opp] + [opp.mutate(rng, rate=0.5) for _ in range(4)],
                args.pop, args.gens, args.seeds, args.validate // 2, log,
                space=Params)
        finally:
            ev.close()
        opp = res.best
        record(f"O{k + 1}")
    log(f"done in {(time.time() - t0) / 60:.0f} min")

    # Final behaviour, replays and report.
    games, beh = behaviour(cfg, bluff, opp, 6000, args.seed + 2)
    wins = [r for r in games if r.end_type == END_SOLO and 0 in r.winners]
    picks = [((0, END_SOLO), r) for r in wins[:6]]
    if picks:
        replay.html_replays(picks, cfg, os.path.join(out, "replays.html"),
                            "Bluffer solo wins (seat 1)")
        with open(os.path.join(out, "replays.txt"), "w") as f:
            f.write("\n\n".join(replay.text_replay(r, cfg) for _, r in picks))
    for name, obj in (("bluffer", bluff), ("opponents", opp)):
        with open(os.path.join(out, f"{name}.json"), "w") as f:
            json.dump({"label": name, "params": obj.to_dict(),
                       "description": obj.describe()}, f, indent=1)

    rows = []
    for name, m, _, _ in stages:
        rows.append(
            f"| {name} | {m['bluffer_solo']:.1%} | {m['honest_twin_solo']:.1%}"
            f" | {m['bluffer_solo'] - m['honest_twin_solo']:+.1%} | "
            f"{m['ordinary_solo']:.1%} | {m['bluffer_any_win']:.1%} | "
            f"{m['ordinary_win']:.1%} | {m['opponent_win']:.1%} |")
    lines = [
        f"# The Bluffer against three tuned players (draw 2, {args.rule})",
        "",
        f"Every measure uses the same {args.validate} deals, each played "
        "with the Bluffer in all four seats. \"Ordinary player\" is a tuned "
        "player sitting in the Bluffer's seat instead (the reference). "
        "Wins count ties and shared wins for every winner.", "",
        "| Stage | Bluffer solo wins | Same plan, no lies | Value of lying | "
        "Ordinary player solo | Bluffer any win | Ordinary player any win "
        "| Each opponent any win |",
        "|---|---|---|---|---|---|---|---|", *rows, "",
        "## Final Bluffer", "", *[f"- {x}" for x in bluff.describe()], "",
        "## Final opponents", "", *[f"- {x}" for x in opp.describe()], "",
        "## How the final Bluffer's games go (Bluffer in seat 1, 6000 games)",
        "",
        f"- Solo win rate: {beh['solo']:.1%}",
        f"- Share of its clues that are lies: {beh['lie_rate']:.0%}",
        f"- Burst rounds per game: {beh['burst_rounds_per_game']:.2f}; "
        f"blocked in {beh['blocked_in_burst']:.0%} of them",
        "", "Search log:", "", "```", *log_lines, "```", ""]
    with open(os.path.join(out, "report.md"), "w") as f:
        f.write("\n".join(lines))
    print(f"Report: {os.path.join(out, 'report.md')}")


if __name__ == "__main__":
    main()
