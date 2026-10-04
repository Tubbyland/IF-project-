"""Command-line entry point.

    python -m bluffsim run        play N games, print the summary
    python -m bluffsim sweep      grid of rule settings -> table + charts
    python -m bluffsim experiment the main experiment: best response, then
                                  self-play, with replays and a report

Every command takes --config FILE (YAML or JSON) and any number of
--set key=value overrides on top of it.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time

from . import charts, replay
from .bots.adaptive import Adaptive, Params
from .config import load_config, parse_value
from .stats import format_summary, run_games, summarise

MAIN_TABLE = ["careful_drifter", "anchor", "adaptive", "adaptive"]


def _common(p):
    p.add_argument("--config", help="YAML or JSON rules file")
    p.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                   help="override one rule, e.g. --set bust_limit=30")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--workers", type=int, default=None)


def _cfg(args):
    cfg = load_config(args.config)
    changes = {}
    for item in args.set:
        k, _, v = item.partition("=")
        changes[k] = parse_value(v)
    cfg = cfg.with_(**changes) if changes else cfg
    cfg.validate()
    return cfg


def _seats(args, cfg):
    if args.seats:
        seats = args.seats.split(",")
    elif args.config:
        seats = _file_section(args.config, "seats") or MAIN_TABLE
    else:
        seats = MAIN_TABLE
    if len(seats) != cfg.n_players:
        sys.exit(f"{len(seats)} seats given for {cfg.n_players} players")
    return seats


def _file_section(path, key):
    with open(path) as f:
        text = f.read()
    if path.endswith((".yaml", ".yml")):
        import yaml
        data = yaml.safe_load(text) or {}
    else:
        data = json.loads(text)
    return data.get(key)


# ---------------------------------------------------------------------------

def analyse_table(cfg, specs, games, seed, workers, out_dir, title,
                  replays_per_group=2):
    """Play a table, write summary, charts, logs and replays. Returns the
    summary text."""
    results = run_games(cfg, specs, games, seed, workers)
    s = summarise(cfg, results)
    text = format_summary(s, title)
    decisive = replay.decisive_summary(results, cfg)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "summary.txt"), "w") as f:
            f.write(text + "\n\n" + decisive)
        charts.summary_charts(s, out_dir)
        replay.save_win_logs(results, os.path.join(out_dir, "win_logs"))
        picks = replay.representative(results, replays_per_group)
        replay.html_replays(picks, cfg, os.path.join(out_dir, "replays.html"),
                            title)
        with open(os.path.join(out_dir, "replays.txt"), "w") as f:
            f.write("\n\n".join(replay.text_replay(r, cfg)
                                for _, r in picks))
    return text, decisive, s


def cmd_run(args):
    cfg = _cfg(args)
    seats = _seats(args, cfg)
    t = time.time()
    text, decisive, _ = analyse_table(cfg, seats, args.games, args.seed,
                                      args.workers, args.out, "Results")
    print(text)
    if args.decisive:
        print()
        print(decisive)
    print(f"\n({args.games} games in {time.time() - t:.1f}s"
          + (f"; files in {args.out})" if args.out else ")"))


def cmd_sweep(args):
    from .sweep import run_sweep, write_sweep
    cfg = _cfg(args)
    seats = _seats(args, cfg)
    grid = {}
    for item in args.grid:
        k, _, vs = item.partition("=")
        grid[k] = [parse_value(v) for v in vs.split(",")]
    if not grid:
        sys.exit("give at least one --grid key=v1,v2,...")
    rows = run_sweep(cfg, grid, seats, args.games, args.seed, args.workers)
    paths = write_sweep(rows, grid, args.out)
    with open(paths[1]) as f:
        print(f.read())
    print("Files:\n  " + "\n  ".join(paths))


def cmd_experiment(args):
    from .tune import Evaluator, best_response, self_play
    cfg = _cfg(args)
    out = args.out
    os.makedirs(out, exist_ok=True)
    rng = random.Random(args.seed)
    seats = _seats(args, cfg)
    tuned = [i for i, s in enumerate(seats) if s == "adaptive"]
    fixed = {i: s for i, s in enumerate(seats) if s != "adaptive"}
    report = [f"# Strategy search\n",
              f"Table: " + ", ".join(f"seat {i + 1} {s}"
                                     for i, s in enumerate(seats)),
              f"\nRules: " + ", ".join(f"{k}={v}" for k, v in
                                       cfg.to_dict().items()) + "\n",
              f"Win score: solo/bust win 1, shared win {args.shared_value}.\n"]
    log_lines = []

    def log(msg):
        print(msg, flush=True)
        log_lines.append(msg)

    ev = Evaluator(cfg, args.workers, args.shared_value)
    try:
        log("Baseline: default adaptive parameters")
        base_text, base_dec, _ = analyse_table(
            cfg, seats, args.final_games, args.seed, args.workers,
            os.path.join(out, "0_baseline"), "Baseline (default adaptive)")
        report += ["## Baseline (adaptive seats on default parameters)\n",
                   "```", base_text, "```\n"]

        log("Best response: tuning seats " +
            ", ".join(str(s + 1) for s in tuned))
        br = best_response(cfg, fixed, tuned, ev, rng, args.pop, args.gens,
                           args.games, args.validate, log)
        _save_params(br.best, os.path.join(out, "best_response.json"),
                     "best_response", br.best_score)
        specs = [s if s != "adaptive" else Adaptive(br.best, "tuned")
                 for s in seats]
        br_text, br_dec, _ = analyse_table(
            cfg, specs, args.final_games, args.seed + 1, args.workers,
            os.path.join(out, "1_best_response"), "Best response")
        report += [
            "## Best response\n",
            f"Win score of the tuned seats: {br.best_score:.3f} "
            f"(default parameters: {br.baseline_score:.3f}).\n",
            "What the tuned strategy does:\n",
            *[f"- {line}" for line in br.best.describe()], "",
            "Parameters:\n", "```", json.dumps(br.best.to_dict(), indent=1),
            "```\n", "Search progress (generation, best, mean): " +
            ", ".join(f"({g}, {b:.3f}, {m:.3f})" for g, b, m in br.history)
            + "\n", "```", br_text, "```\n", "```", br_dec, "```\n"]

        if args.skip_self_play:
            sp = None
        else:
            log("Self-play")
            sp = self_play(cfg, br.best, ev, rng, args.sp_iters, args.sp_pop,
                           args.sp_gens, args.sp_games, args.validate // 2,
                           log)
    finally:
        ev.close()

    if sp:
        champ = sp.champions[-1]
        _save_params(champ, os.path.join(out, "self_play_champion.json"),
                     "self_play", None)
        sp_specs = [Adaptive(champ, "champion")
                    for _ in range(cfg.n_players)]
        sp_text, sp_dec, _ = analyse_table(
            cfg, sp_specs, args.final_games, args.seed + 2, args.workers,
            os.path.join(out, "2_self_play"), "Self-play champion, all seats")
        mixed = [s if s != "adaptive" else Adaptive(champ, "champion")
                 for s in seats]
        mx_text, _, _ = analyse_table(
            cfg, mixed, args.final_games, args.seed + 3, args.workers,
            os.path.join(out, "3_champion_vs_fixed"),
            "Self-play champion against the fixed bots")
        k = len(sp.champions)
        cross = "\n".join(
            f"  C{i}: " + "  ".join(f"{sp.cross[i][j]:.3f}" for j in range(k))
            for i in range(k))
        report += [
            "## Self-play\n",
            sp.verdict + "\n",
            "Per iteration (champion in own field -> best challenger): " +
            ", ".join(f"{a:.3f} -> {b:.3f}{' (new)' if t else ''}"
                      for a, b, t in zip(sp.champion_scores,
                                         sp.challenger_scores, sp.accepted))
            + "\n",
            "Cross-play: row = strategy in one seat, column = strategy in "
            "the other seats; value = row's win score. C0 is the "
            "best-response strategy.\n", "```", cross, "```\n",
            "What the final champion does:\n",
            *[f"- {line}" for line in champ.describe()], "",
            "```", sp_text, "```\n", "```", sp_dec, "```\n",
            "```", mx_text, "```\n"]

    with open(os.path.join(out, "report.md"), "w") as f:
        f.write("\n".join(report))
    with open(os.path.join(out, "search_log.txt"), "w") as f:
        f.write("\n".join(log_lines))
    print(f"\nReport: {os.path.join(out, 'report.md')}")


def _save_params(p: Params, path, label, score):
    with open(path, "w") as f:
        json.dump({"label": label, "score": score, "params": p.to_dict(),
                   "description": p.describe()}, f, indent=1)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bluffsim", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("run", help="play N games and summarise")
    _common(p)
    p.add_argument("--games", type=int, default=10000)
    p.add_argument("--seats", help="comma list of strategies, one per seat")
    p.add_argument("--out", help="folder for charts, logs and replays")
    p.add_argument("--decisive", action="store_true",
                   help="also print the decisive-round analysis")
    p.set_defaults(fn=cmd_run)

    p = sub.add_parser("sweep", help="grid of rule settings")
    _common(p)
    p.add_argument("--grid", action="append", default=[],
                   metavar="KEY=V1,V2,...")
    p.add_argument("--games", type=int, default=3000)
    p.add_argument("--seats")
    p.add_argument("--out", default="results/sweep")
    p.set_defaults(fn=cmd_sweep)

    p = sub.add_parser("experiment", help="best response + self-play")
    _common(p)
    p.add_argument("--seats", help="default: careful_drifter,anchor,"
                   "adaptive,adaptive")
    p.add_argument("--out", default="results/experiment")
    p.add_argument("--shared-value", type=float, default=1.0,
                   help="win score for a shared win (solo/bust = 1)")
    p.add_argument("--pop", type=int, default=32)
    p.add_argument("--gens", type=int, default=20)
    p.add_argument("--games", type=int, default=1500,
                   help="games per candidate per generation")
    p.add_argument("--validate", type=int, default=10000)
    p.add_argument("--final-games", type=int, default=10000)
    p.add_argument("--skip-self-play", action="store_true")
    p.add_argument("--sp-iters", type=int, default=5)
    p.add_argument("--sp-pop", type=int, default=20)
    p.add_argument("--sp-gens", type=int, default=10)
    p.add_argument("--sp-games", type=int, default=400,
                   help="seeds per candidate; each is played once per seat")
    p.set_defaults(fn=cmd_experiment)

    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
