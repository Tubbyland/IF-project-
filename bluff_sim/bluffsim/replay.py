"""Winning-game logs, readable replays and decisive-round analysis.

Decisive round: the round with the largest swing toward the winner, measured
per kind of win:
  solo  increase in the winner's |track| (progress toward the threshold)
  bust  increase in (smallest other |track|) - (winner's |track|), i.e. how
        much the winner's lead at being closest to zero grew
  shared  fall in |tally| (shared wins have no single winner; reported
        under every seat)
"""
from __future__ import annotations

import html
import json
import os
from collections import Counter, defaultdict

import numpy as np

from .engine import (CLUE_NAMES, END_BUST, END_SHARED, END_SOLO, GameResult,
                     clue_for)


def game_to_dict(r: GameResult) -> dict:
    return {
        "seed": r.seed, "end_type": r.end_type, "winners": list(r.winners),
        "rounds_played": r.rounds_played, "strategies": r.strategies,
        "final_tracks": r.tracks, "final_tally": r.tally,
        "decisive_steals": r.decisive_steals,
        "rounds": [{
            "round": rec.round + 1, "first_player": rec.first + 1,
            "personal_targets": rec.personal,
            "collective_target": rec.collective, "gap": rec.gap,
            "cards": [list(c) for c in rec.cards],
            "clues": [CLUE_NAMES[c] for c in rec.clues],
            "leaders": rec.leaders, "eligible": rec.eligible,
            "vetoes": {str(k): v for k, v in rec.vetoes.items()},
            "drifts": rec.drifts, "track_change": rec.track_delta,
            "stolen": rec.stolen, "contributions": rec.contributions,
            "tracks_after": rec.tracks_after,
            "tally_after": rec.tally_after,
        } for rec in r.records],
    }


def _metric(r: GameResult, w: int, tracks, tally) -> float:
    if r.end_type == END_SOLO:
        return abs(tracks[w])
    if r.end_type == END_BUST:
        others = [abs(t) for i, t in enumerate(tracks) if i != w]
        return min(others) - abs(tracks[w])
    return -abs(tally)


def decisive_round(r: GameResult, w: int) -> tuple[int, float]:
    best, best_swing = 0, float("-inf")
    for rec in r.records:
        swing = (_metric(r, w, rec.tracks_after, rec.tally_after)
                 - _metric(r, w, rec.tracks_before, rec.tally_before))
        if swing > best_swing:
            best, best_swing = rec.round, swing
    return best, best_swing


def actions(r: GameResult, w: int, rnd: int, cfg) -> dict:
    """What seat w did in round rnd."""
    rec = r.records[rnd]
    truth = clue_for(rec.drifts[w], cfg)
    vetoed = rec.vetoes.get(w)
    hit_by = [v for v, t in rec.vetoes.items() if t == w]
    stole = sum(a for v, _, a in rec.stolen if v == w)
    return {
        "round": rnd + 1,
        "final_round": rnd == cfg.rounds - 1,
        "drift": rec.drifts[w],
        "cards": len(rec.cards[w]),
        "lied": rec.clues[w] != truth,
        "lie_size": rec.clues[w] - truth,
        "vetoed_someone": vetoed is not None,
        "stole": stole,
        "was_vetoed": len(hit_by),
        "track_change": rec.track_delta[w],
        "tally_change": rec.tally_delta,
        "ended_game": rnd == r.rounds_played - 1,
    }


def decisive_summary(results: list[GameResult], cfg) -> str:
    """Per seat and win type: what the winner did in its decisive round."""
    groups = defaultdict(list)
    for r in results:
        if r.end_type not in (END_SOLO, END_BUST):
            continue
        for w in r.winners:
            rnd, swing = decisive_round(r, w)
            a = actions(r, w, rnd, cfg)
            a["swing"] = swing
            groups[(w, r.strategies[w], r.end_type)].append(a)
    lines = ["Decisive rounds (largest swing toward the winner)", ""]
    for (w, name, end), acts in sorted(groups.items()):
        n = len(acts)
        drift = np.array([a["drift"] for a in acts])
        rounds = Counter(a["round"] for a in acts)
        common = ", ".join(f"r{k}: {v / n:.0%}"
                           for k, v in sorted(rounds.items()))
        lines.append(f"Seat {w + 1} ({name}), {end} wins: {n}")
        lines.append(f"  round of the swing     {common}")
        lines.append(f"  swing size             mean {np.mean([a['swing'] for a in acts]):.1f}")
        lines.append(f"  was also the last      {np.mean([a['ended_game'] for a in acts]):.0%}")
        lines.append(f"  own drift              mean {drift.mean():+.1f}, "
                     f"mean |drift| {np.abs(drift).mean():.1f}")
        lines.append(f"  cards played           mean {np.mean([a['cards'] for a in acts]):.2f}")
        lines.append(f"  clue was a lie         {np.mean([a['lied'] for a in acts]):.0%}")
        lines.append(f"  vetoed someone         {np.mean([a['vetoed_someone'] for a in acts]):.0%}"
                     f" (mean stolen when it did: "
                     f"{_mean([a['stole'] for a in acts if a['vetoed_someone']]):+.1f})")
        lines.append(f"  was vetoed             {np.mean([a['was_vetoed'] > 0 for a in acts]):.0%}")
        lines.append("  in plain words: " + _plain(acts, end))
        lines.append("")
    return "\n".join(lines)


def _mean(xs):
    return float(np.mean(xs)) if xs else 0.0


def _plain(acts, end) -> str:
    drift = np.mean([abs(a["drift"]) for a in acts])
    lie = np.mean([a["lied"] for a in acts])
    veto = np.mean([a["vetoed_someone"] for a in acts])
    last = np.mean([a["ended_game"] for a in acts])
    parts = []
    if end == END_SOLO:
        parts.append(f"pushed its own track by about {drift:.0f}")
    else:
        parts.append(f"kept its own drift to about {drift:.0f} while "
                     f"others moved away from zero")
    if veto >= 0.25:
        parts.append(f"vetoed in {veto:.0%} of them")
    parts.append("lied" if lie >= 0.5 else "mostly told the truth")
    if last >= 0.6:
        parts.append("usually in the round the game ended")
    return "; ".join(parts) + "."


def save_win_logs(results: list[GameResult], out_dir: str,
                  per_seat: int = 50) -> list[str]:
    """JSONL of up to `per_seat` winning games for each seat."""
    os.makedirs(out_dir, exist_ok=True)
    by_seat = defaultdict(list)
    for r in results:
        for w in r.winners:
            if len(by_seat[w]) < per_seat:
                by_seat[w].append(r)
    paths = []
    for w, games in sorted(by_seat.items()):
        p = os.path.join(out_dir, f"wins_seat{w + 1}.jsonl")
        with open(p, "w") as f:
            for g in games:
                f.write(json.dumps(game_to_dict(g)) + "\n")
        paths.append(p)
    return paths


def representative(results: list[GameResult], k: int = 2):
    """Up to k games per (seat, win type), chosen near the median swing so
    they are typical rather than freak results."""
    groups = defaultdict(list)
    for r in results:
        if r.end_type == END_SHARED:
            groups[(-1, END_SHARED)].append((0.0, r))
            continue
        for w in r.winners:
            groups[(w, r.end_type)].append((decisive_round(r, w)[1], r))
    picks = []
    for key, items in sorted(groups.items()):
        items.sort(key=lambda x: x[0])
        mid = len(items) // 2
        chosen = items[max(0, mid - k // 2): max(0, mid - k // 2) + k]
        picks += [(key, r) for _, r in chosen]
    return picks


def text_replay(r: GameResult, cfg) -> str:
    seats = [f"{i + 1}:{s}" for i, s in enumerate(r.strategies)]
    out = [f"Game seed {r.seed}: {r.end_type}, winners "
           f"{[w + 1 for w in r.winners]}  ({', '.join(seats)})"]
    for rec in r.records:
        fin = "  FINAL (x2)" if rec.round == cfg.rounds - 1 else ""
        out.append(f"Round {rec.round + 1}{fin}: collective {rec.collective}, "
                   f"personal {rec.personal}, gap {rec.gap:+d}; "
                   f"tally {rec.tally_before:+d}")
        for i in rec.order:
            truth = clue_for(rec.drifts[i], cfg)
            lie = "" if rec.clues[i] == truth else \
                f" (lie; truth {CLUE_NAMES[truth]})"
            out.append(f"   {i + 1} plays {list(rec.cards[i])} = "
                       f"{rec.totals[i]}, says '{CLUE_NAMES[rec.clues[i]]}'"
                       f"{lie}, drift {rec.drifts[i]:+d}")
        vs = [f"{v + 1}->{t + 1}" for v, t in rec.vetoes.items()
              if t is not None]
        out.append(f"   vetoes: {', '.join(vs) or 'none'} "
                   f"(eligible {[e + 1 for e in rec.eligible]})")
        out.append(f"   tracks {rec.tracks_after}, tally "
                   f"{rec.tally_after:+d} ({rec.tally_delta:+d})")
    return "\n".join(out)


_CSS = """
:root{--bg:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--line:#e4e3df;
--win:#1baf7a;--lie:#e34948;--veto:#2a78d6;--card:#ffffff}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
--bg:#1a1a19;--ink:#ffffff;--ink2:#c3c2b7;--line:#383835;--win:#199e70;
--lie:#e66767;--veto:#3987e5;--card:#232322}}
:root[data-theme="dark"]{--bg:#1a1a19;--ink:#ffffff;--ink2:#c3c2b7;
--line:#383835;--win:#199e70;--lie:#e66767;--veto:#3987e5;--card:#232322}
body{background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,sans-serif;
margin:0 auto;max-width:1000px;padding:24px 16px}
h1{font-size:22px}h2{font-size:17px;margin-top:36px}
.meta{color:var(--ink2)}
section{background:var(--card);border:1px solid var(--line);border-radius:8px;
padding:12px 16px;margin:16px 0;overflow-x:auto}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:4px 8px;border-bottom:1px solid var(--line);
white-space:nowrap}th{color:var(--ink2);font-weight:500}
.lie{color:var(--lie)}.veto{color:var(--veto)}.win{color:var(--win);font-weight:600}
.decisive{outline:2px solid var(--win);outline-offset:-2px}
"""


def html_replays(picks, cfg, path, title="Replays") -> str:
    parts = [f"<!doctype html><html><head><meta charset='utf-8'>"
             f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
             f"<title>{html.escape(title)}</title><style>{_CSS}</style>"
             f"</head><body><h1>{html.escape(title)}</h1>"
             f"<p class='meta'>Red clue = a lie. Blue = a veto. The outlined "
             f"round is the decisive round (largest swing toward the "
             f"winner). The final round doubles drift on tracks.</p>"]
    current = None
    for (seat, end), r in picks:
        head = (f"Shared wins" if end == END_SHARED else
                f"Seat {seat + 1} ({r.strategies[seat]}): {end} wins")
        if head != current:
            parts.append(f"<h2>{html.escape(head)}</h2>")
            current = head
        dec = decisive_round(r, seat)[0] if seat >= 0 else None
        parts.append(_game_html(r, cfg, dec))
    parts.append("</body></html>")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write("".join(parts))
    return path


def _game_html(r: GameResult, cfg, dec) -> str:
    n = len(r.strategies)
    who = ", ".join(f"{i + 1}: {html.escape(s)}"
                    for i, s in enumerate(r.strategies))
    winners = ", ".join(str(w + 1) for w in r.winners) or "nobody"
    rows = []
    for rec in r.records:
        fin = " ×2" if rec.round == cfg.rounds - 1 else ""
        cls = " class='decisive'" if rec.round == dec else ""
        cells = []
        for i in range(n):
            truth = clue_for(rec.drifts[i], cfg)
            clue = CLUE_NAMES[rec.clues[i]]
            clue_html = (f"<span class='lie'>{clue}</span>"
                         if rec.clues[i] != truth else clue)
            t = rec.vetoes.get(i)
            veto = (f" <span class='veto'>veto→{t + 1}</span>"
                    if t is not None else "")
            cells.append(f"<td>{'+'.join(map(str, rec.cards[i]))} "
                         f"vs {rec.personal[i]} ({rec.drifts[i]:+d})<br>"
                         f"{clue_html}{veto}<br>"
                         f"track {rec.tracks_after[i]:+d}</td>")
        rows.append(f"<tr{cls}><td>R{rec.round + 1}{fin}<br>first "
                    f"{rec.first + 1}</td><td>{rec.collective}<br>gap "
                    f"{rec.gap:+d}</td>{''.join(cells)}<td>"
                    f"{rec.tally_after:+d}<br>({rec.tally_delta:+d})</td></tr>")
    head = "".join(f"<th>Seat {i + 1}</th>" for i in range(n))
    return (f"<section><div><b>Seed {r.seed}</b> · {who} · "
            f"<span class='win'>{r.end_type} → seat {winners}</span></div>"
            f"<table><tr><th>Round</th><th>Collective</th>{head}"
            f"<th>Tally</th></tr>{''.join(rows)}</table></section>")
