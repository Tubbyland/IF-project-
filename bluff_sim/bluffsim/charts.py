"""Static PNG charts (matplotlib). Colours follow a fixed categorical order so
an ending or seat keeps its colour across every chart."""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .engine import END_BUST, END_BUST_NO_WINNER, END_SHARED, END_SOLO  # noqa: E402

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300",
          "#4a3aa7", "#e34948"]
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
END_COLOURS = {END_SOLO: SERIES[0], END_BUST: SERIES[1], END_SHARED: SERIES[2],
               END_BUST_NO_WINNER: SERIES[3]}
END_NAMES = {END_SOLO: "Solo win", END_BUST: "Bust win",
             END_SHARED: "Shared win", END_BUST_NO_WINNER: "Bust, no winner"}


def _style(ax, title, xlabel="", ylabel=""):
    ax.set_facecolor(SURFACE)
    ax.figure.set_facecolor(SURFACE)
    ax.set_title(title, color=INK, fontsize=12, loc="left", pad=10)
    ax.set_xlabel(xlabel, color=INK_2)
    ax.set_ylabel(ylabel, color=INK_2)
    ax.tick_params(colors=INK_2, length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def _save(fig, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def histogram(values, path, title, xlabel):
    fig, ax = plt.subplots(figsize=(7, 3.6))
    values = np.asarray(values)
    lo, hi = int(values.min()), int(values.max())
    bins = np.arange(lo - 0.5, hi + 1.5, max(1, (hi - lo) // 40 or 1))
    ax.hist(values, bins=bins, color=SERIES[0], edgecolor=SURFACE,
            linewidth=1)
    ax.axvline(0, color=INK_2, linewidth=1)
    _style(ax, title, xlabel, "count")
    return _save(fig, path)


def summary_charts(summary, out_dir) -> list[str]:
    """Endings, wins by seat, and the drift and gap distributions."""
    paths = []
    s = summary
    # Endings.
    fig, ax = plt.subplots(figsize=(7, 3))
    ends = [e for e in (END_SOLO, END_BUST, END_BUST_NO_WINNER, END_SHARED)
            if s.end_types.get(e)]
    vals = [100 * s.end_types[e] / s.n for e in ends]
    bars = ax.barh([END_NAMES[e] for e in ends], vals,
                   color=[END_COLOURS[e] for e in ends], height=0.6)
    for b, v in zip(bars, vals):
        ax.text(b.get_width() + 1, b.get_y() + b.get_height() / 2,
                f"{v:.1f}%", va="center", color=INK, fontsize=9)
    ax.set_xlim(0, 105)
    ax.invert_yaxis()
    _style(ax, "How games end", "% of games")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.grid(axis="y", visible=False)
    paths.append(_save(fig, os.path.join(out_dir, "endings.png")))

    # Wins by seat, stacked by ending.
    fig, ax = plt.subplots(figsize=(7, 3.6))
    labels = [f"{i + 1}: {n}" for i, n in enumerate(s.strategies)]
    left = np.zeros(len(labels))
    for e in (END_SOLO, END_BUST, END_SHARED):
        v = np.array([100 * s.seat_wins[i][e] / s.n
                      for i in range(len(labels))])
        if v.sum() == 0:
            continue
        ax.barh(labels, v, left=left, color=END_COLOURS[e], height=0.6,
                label=END_NAMES[e], edgecolor=SURFACE, linewidth=2)
        left += v
    for i, total in enumerate(left):
        ax.text(total + 1, i, f"{total:.1f}%", va="center", color=INK,
                fontsize=9)
    ax.set_xlim(0, max(left.max() * 1.15, 10))
    ax.invert_yaxis()
    _style(ax, "Wins by seat", "% of games won (ties count for each winner)")
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.grid(axis="y", visible=False)
    ax.legend(frameon=False, loc="lower right", fontsize=9)
    paths.append(_save(fig, os.path.join(out_dir, "wins_by_seat.png")))

    paths.append(histogram(s.drifts, os.path.join(out_dir, "drift.png"),
                           "Per-player drift each round",
                           "pocket total - personal target"))
    paths.append(histogram(s.gaps, os.path.join(out_dir, "gap.png"),
                           "Round gap",
                           "collective target - sum of personal targets"))
    return paths


def sweep_lines(rows, param, out_path, fixed_note=""):
    """Share of each ending as one swept parameter changes."""
    xs = sorted({r[param] for r in rows})
    fig, ax = plt.subplots(figsize=(7, 3.8))
    for key, e in (("solo", END_SOLO), ("bust", END_BUST),
                   ("shared", END_SHARED)):
        ys = [np.mean([r[key] for r in rows if r[param] == x]) * 100
              for x in xs]
        ax.plot(xs, ys, color=END_COLOURS[e], linewidth=2, marker="o",
                markersize=6, label=END_NAMES[e])
    ax.set_ylim(0, 100)
    ax.set_xticks(xs, [str(x) for x in xs])
    _style(ax, f"Endings vs {param}" + (f"  ({fixed_note})" if fixed_note
                                         else ""), param, "% of games")
    ax.legend(frameon=False, fontsize=9)
    return _save(fig, out_path)


def sweep_heatmap(rows, px, py, metric, out_path, title):
    xs = sorted({r[px] for r in rows})
    ys = sorted({r[py] for r in rows})
    grid = np.full((len(ys), len(xs)), np.nan)
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            vals = [r[metric] for r in rows if r[px] == x and r[py] == y]
            if vals:
                grid[j, i] = 100 * np.mean(vals)
    fig, ax = plt.subplots(figsize=(1.2 * len(xs) + 2.5, 0.7 * len(ys) + 2))
    im = ax.imshow(grid, cmap="Blues", vmin=0, vmax=100, aspect="auto",
                   origin="lower")
    ax.set_xticks(range(len(xs)), [str(x) for x in xs])
    ax.set_yticks(range(len(ys)), [str(y) for y in ys])
    for j in range(len(ys)):
        for i in range(len(xs)):
            if not np.isnan(grid[j, i]):
                v = grid[j, i]
                ax.text(i, j, f"{v:.0f}", ha="center", va="center",
                        fontsize=9, color="white" if v > 55 else INK)
    _style(ax, title, px, py)
    ax.grid(False)
    fig.colorbar(im, ax=ax, label="% of games", shrink=0.8)
    return _save(fig, out_path)
