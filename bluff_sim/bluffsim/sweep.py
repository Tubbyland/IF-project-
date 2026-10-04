"""Parameter sweeps: every combination of a grid, one summary row each."""
from __future__ import annotations

import csv
import itertools
import os

from . import charts
from .config import GameConfig
from .engine import END_BUST, END_SHARED, END_SOLO
from .stats import run_games, summarise


def run_sweep(base: GameConfig, grid: dict[str, list], specs, games: int,
              seed: int = 0, workers=None, log=print) -> list[dict]:
    keys = list(grid)
    rows = []
    combos = list(itertools.product(*(grid[k] for k in keys)))
    for i, values in enumerate(combos):
        changes = dict(zip(keys, values))
        cfg = base.with_(**changes)
        cfg.validate()
        s = summarise(cfg, run_games(cfg, specs, games, seed, workers))
        comp = {k: v["competitive"] for k, v in s.strategy_rates.items()}
        top = max(comp, key=comp.get)
        row = dict(changes)
        row.update({
            "solo": s.end_types[END_SOLO] / s.n,
            "bust": s.end_types[END_BUST] / s.n,
            "shared": s.end_types[END_SHARED] / s.n,
            "avg_rounds": s.avg_length,
            "reach_final": s.reached_final,
            "veto_rate": s.veto["veto_rate"],
            "rounds_with_veto": s.veto["rounds_with_veto"],
            "double_veto_rate": s.veto["double_veto_rate"],
            "steal_decided": s.veto["steal_caused_win"],
            "kingmaking": s.kingmaking / s.n,
            "top_strategy": top,
            "top_outright_wins": comp[top],
            "flags": " | ".join(s.dominance),
        })
        rows.append(row)
        log(f"  [{i + 1}/{len(combos)}] {changes}: solo {row['solo']:.0%} "
            f"bust {row['bust']:.0%} shared {row['shared']:.0%}")
    return rows


def write_sweep(rows: list[dict], grid: dict, out_dir: str) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    csv_path = os.path.join(out_dir, "sweep.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    paths.append(csv_path)

    md_path = os.path.join(out_dir, "sweep.md")
    keys = list(grid)
    cols = keys + ["solo", "bust", "shared", "avg_rounds", "veto_rate",
                   "kingmaking", "top_strategy", "top_outright_wins"]
    pct = {"solo", "bust", "shared", "veto_rate", "kingmaking",
           "top_outright_wins"}
    with open(md_path, "w") as f:
        f.write("| " + " | ".join(cols) + " |\n")
        f.write("|" + "---|" * len(cols) + "\n")
        for r in rows:
            cells = []
            for c in cols:
                v = r[c]
                if c in pct:
                    cells.append(f"{100 * v:.1f}%")
                elif isinstance(v, float):
                    cells.append(f"{v:.2f}")
                else:
                    cells.append(str(v))
            f.write("| " + " | ".join(cells) + " |\n")
        flagged = [r for r in rows if r["flags"]]
        if flagged:
            f.write("\nFlags\n\n")
            for r in flagged:
                setting = ", ".join(f"{k}={r[k]}" for k in keys)
                f.write(f"- {setting}: {r['flags']}\n")
    paths.append(md_path)

    for k in keys:
        if len(grid[k]) > 1:
            paths.append(charts.sweep_lines(
                rows, k, os.path.join(out_dir, f"endings_vs_{k}.png"),
                "averaged over other settings" if len(keys) > 1 else ""))
    multi = [k for k in keys if len(grid[k]) > 1]
    if len(multi) >= 2:
        a, b = multi[0], multi[1]
        for metric in ("shared", "bust"):
            paths.append(charts.sweep_heatmap(
                rows, a, b, metric,
                os.path.join(out_dir, f"{metric}_{a}_x_{b}.png"),
                f"{metric.capitalize()} win % by {a} and {b}"))
    return paths
