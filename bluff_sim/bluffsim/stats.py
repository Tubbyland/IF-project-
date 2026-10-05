"""Running many games and summarising them."""
from __future__ import annotations

import os
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field

import numpy as np

from .bots import make_table
from .config import GameConfig
from .engine import (END_BUST, END_BUST_NO_WINNER, END_SHARED, END_SOLO,
                     GameResult, play_game)

END_LABELS = {END_SOLO: "solo win", END_BUST: "bust win",
              END_BUST_NO_WINNER: "bust, no winner",
              END_SHARED: "shared win"}


def _run_chunk(args):
    cfg, specs, seeds = args
    out = []
    for s in seeds:
        out.append(play_game(cfg, make_table(specs), s))
    return out


def default_workers() -> int:
    return max(1, min(8, os.cpu_count() or 1))


def run_games(cfg: GameConfig, specs, n: int, seed: int = 0,
              workers: int | None = None) -> list[GameResult]:
    """Play n games. Game i uses seed `seed * 1_000_003 + i`, so results do
    not depend on the number of workers."""
    cfg.validate()
    seeds = [seed * 1_000_003 + i for i in range(n)]
    workers = workers or default_workers()
    if workers <= 1 or n < 200:
        return _run_chunk((cfg, specs, seeds))
    size = -(-n // (workers * 4))
    chunks = [(cfg, specs, seeds[i:i + size]) for i in range(0, n, size)]
    results: list[GameResult] = []
    with ProcessPoolExecutor(workers) as ex:
        for part in ex.map(_run_chunk, chunks):
            results.extend(part)
    return results


# ---------------------------------------------------------------------------

@dataclass
class Summary:
    n: int
    rounds: int
    strategies: list[str]
    end_types: Counter
    avg_length: float
    reached_final: float
    seat_wins: dict            # seat -> Counter(end_type -> games won)
    seat_share: list[float]    # wins split evenly among tied winners
    strategy_rates: dict       # name -> dict of rates per seat occupied
    veto: dict
    drifts: np.ndarray
    gaps: np.ndarray
    kingmaking: int
    tension: dict = field(default_factory=dict)
    dominance: list[str] = field(default_factory=list)


def summarise(cfg: GameConfig, results: list[GameResult]) -> Summary:
    n = len(results)
    strategies = results[0].strategies
    seats = range(len(strategies))
    end_types = Counter(r.end_type for r in results)
    seat_wins = {s: Counter() for s in seats}
    share = [0.0] * len(strategies)
    for r in results:
        for w in r.winners:
            seat_wins[w][r.end_type] += 1
            share[w] += 1 / len(r.winners)

    # Per strategy, averaged over the seats it occupies.
    by_strat = defaultdict(list)
    for s, name in enumerate(strategies):
        by_strat[name].append(s)
    strategy_rates = {}
    for name, ss in by_strat.items():
        k = len(ss) * n
        strategy_rates[name] = {
            "seats": [s + 1 for s in ss],
            "any_win": sum(sum(seat_wins[s].values()) for s in ss) / k,
            "solo": sum(seat_wins[s][END_SOLO] for s in ss) / k,
            "bust": sum(seat_wins[s][END_BUST] for s in ss) / k,
            "competitive": sum(seat_wins[s][END_SOLO] + seat_wins[s][END_BUST]
                               for s in ss) / k,
        }

    # Vetoes.
    opportunities = declared = rounds_with = 0
    targets = double = 0
    stolen = []
    drifts, gaps = [], []
    kingmaking = 0
    games_with_decisive_steal = sum(1 for r in results if r.decisive_steals)
    for r in results:
        for rec in r.records:
            gaps.append(rec.gap)
            drifts.extend(rec.drifts)
            opportunities += len(rec.eligible)
            vs = [t for t in rec.vetoes.values() if t is not None]
            declared += len(vs)
            rounds_with += bool(vs)
            hits = Counter(vs)
            targets += len(hits)
            double += sum(1 for c in hits.values()
                          if c >= cfg.double_veto_at)
            stolen.extend(abs(a) for _, _, a in rec.stolen)
        last = r.records[-1]
        if r.end_type in (END_SOLO, END_BUST):
            hits = defaultdict(list)
            for v, t in last.vetoes.items():
                if t is not None:
                    hits[t].append(v)
            for t, vs in hits.items():
                if (len(vs) >= cfg.double_veto_at
                        and abs(last.drifts[t]) >= 20
                        and t not in r.winners
                        and any(v in r.winners for v in vs)):
                    kingmaking += 1
                    break
    total_rounds = sum(r.rounds_played for r in results)
    veto = {
        "eligible_per_round": opportunities / total_rounds,
        "veto_rate": declared / opportunities if opportunities else 0.0,
        "rounds_with_veto": rounds_with / total_rounds,
        "vetoes_per_game": declared / n,
        "double_veto_rate": double / targets if targets else 0.0,
        "avg_stolen": float(np.mean(stolen)) if stolen else 0.0,
        "steal_caused_win": games_with_decisive_steal / n,
    }

    s = Summary(n=n, rounds=cfg.rounds, strategies=strategies,
                end_types=end_types,
                avg_length=total_rounds / n,
                reached_final=sum(r.rounds_played == cfg.rounds
                                  for r in results) / n,
                seat_wins=seat_wins, seat_share=[x / n for x in share],
                strategy_rates=strategy_rates, veto=veto,
                drifts=np.array(drifts), gaps=np.array(gaps),
                kingmaking=kingmaking)
    s.tension = tension(results)
    s.dominance = dominance_flags(s)
    return s


def tension(results: list[GameResult]) -> dict:
    """Rough measures of whether a game stays open.

    comeback: of solo and bust wins, the share where the winner was not
      already ahead going into the deciding round (for solo, ahead = furthest
      from zero; for bust, ahead = closest to zero).
    lead_changes: per game, how often the player(s) furthest from zero
      change from one round to the next.
    ending_spread: how evenly games split between solo, bust and shared
      endings, from 0 (always the same) to 1 (a third each).
    comeback_half: of solo and bust wins, the share where the winner was
      not ahead at the halfway point of the game (after round
      ceil(rounds/2), or the last round played if earlier).
    final_decided: share of all games won outright (solo or bust) in the
      last scheduled round.
    """
    comebacks = decided = half_comebacks = final_decided = 0
    changes = 0
    for r in results:
        prev = None
        for rec in r.records:
            top = max(abs(t) for t in rec.tracks_after)
            lead = frozenset(i for i, t in enumerate(rec.tracks_after)
                             if abs(t) == top) if top else None
            if prev is not None and lead is not None and lead != prev:
                changes += 1
            if lead is not None:
                prev = lead
        if r.end_type in (END_SOLO, END_BUST):
            before = [abs(t) for t in r.records[-1].tracks_before]
            best = max(before) if r.end_type == END_SOLO else min(before)
            ahead = {i for i, t in enumerate(before) if t == best}
            decided += 1
            comebacks += not set(r.winners) & ahead
            mid = min(len(r.records) - 1,
                      (rounds_of(r) + 1) // 2 - 1)
            at_mid = [abs(t) for t in r.records[mid].tracks_after]
            best_mid = (max(at_mid) if r.end_type == END_SOLO
                        else min(at_mid))
            ahead_mid = {i for i, t in enumerate(at_mid) if t == best_mid}
            half_comebacks += not set(r.winners) & ahead_mid
            final_decided += r.records[-1].round == rounds_of(r) - 1
    counts = Counter(r.end_type for r in results)
    probs = [counts[e] / len(results) for e in (END_SOLO, END_BUST,
                                                END_SHARED)]
    entropy = -sum(p * np.log(p) for p in probs if p > 0) / np.log(3)
    return {"comeback": comebacks / decided if decided else 0.0,
            "comeback_half": half_comebacks / decided if decided else 0.0,
            "final_decided": final_decided / len(results),
            "lead_changes": changes / len(results),
            "ending_spread": float(entropy)}


def rounds_of(r: GameResult) -> int:
    return r.rounds_total


def dominance_flags(s: Summary) -> list[str]:
    """Warnings that usually point at a rule that needs fixing."""
    flags = []
    for end, c in s.end_types.items():
        if c / s.n >= 0.7:
            flags.append(f"{END_LABELS[end]} ends {c / s.n:.0%} of games.")
    rates = {k: v["competitive"] for k, v in s.strategy_rates.items()}
    if len(rates) > 1:
        for name, r in rates.items():
            rest = [x for k, x in rates.items() if k != name]
            mean_rest = sum(rest) / len(rest)
            if r >= 0.25 and r >= 2 * mean_rest:
                flags.append(
                    f"'{name}' wins {r:.0%} of games outright, at least "
                    f"twice the others' average ({mean_rest:.0%}).")
    return flags


def _pct(x: float) -> str:
    return f"{100 * x:5.1f}%"


def format_summary(s: Summary, title: str = "") -> str:
    lines = []
    if title:
        lines += [title, "=" * len(title)]
    lines.append(f"Games: {s.n}    Table: " + ", ".join(
        f"{i + 1}:{name}" for i, name in enumerate(s.strategies)))
    lines.append("")
    lines.append("How games end")
    for end in (END_SOLO, END_BUST, END_BUST_NO_WINNER, END_SHARED):
        if end in s.end_types or end != END_BUST_NO_WINNER:
            lines.append(f"  {END_LABELS[end]:<16}{_pct(s.end_types[end] / s.n)}")
    lines.append(f"  average length  {s.avg_length:.2f} rounds; "
                 f"{s.reached_final:.0%} reach round {s.rounds}")
    lines.append("")
    lines.append("Wins by seat (share = ties split evenly; shared wins count "
                 "for everyone)")
    lines.append(f"  {'seat':<24}{'any win':>8}{'solo':>8}{'bust':>8}"
                 f"{'shared':>8}{'share':>8}")
    for seat, name in enumerate(s.strategies):
        w = s.seat_wins[seat]
        lines.append(
            f"  {f'{seat + 1}: {name}':<24}"
            f"{_pct(sum(w.values()) / s.n):>8}{_pct(w[END_SOLO] / s.n):>8}"
            f"{_pct(w[END_BUST] / s.n):>8}{_pct(w[END_SHARED] / s.n):>8}"
            f"{_pct(s.seat_share[seat]):>8}")
    if len(s.strategy_rates) < len(s.strategies):
        lines.append("")
        lines.append("Wins by strategy (per seat it occupies)")
        for name, r in s.strategy_rates.items():
            lines.append(f"  {name:<24}{_pct(r['any_win']):>8}"
                         f"{_pct(r['solo']):>8}{_pct(r['bust']):>8}")
    v = s.veto
    lines.append("")
    lines.append("Vetoes")
    lines.append(f"  eligible players per round  {v['eligible_per_round']:.2f}")
    lines.append(f"  eligible players who veto   {_pct(v['veto_rate'])}")
    lines.append(f"  rounds with a veto          {_pct(v['rounds_with_veto'])}")
    lines.append(f"  vetoes per game             {v['vetoes_per_game']:.2f}")
    lines.append(f"  vetoed players hit twice+   {_pct(v['double_veto_rate'])}")
    lines.append(f"  average drift stolen (abs)  {v['avg_stolen']:.1f}")
    lines.append(f"  games a steal decided       {_pct(v['steal_caused_win'])}")
    lines.append(f"  kingmaking (20+ dump double-vetoed into a vetoer's win): "
                 f"{s.kingmaking} games ({_pct(s.kingmaking / s.n).strip()})")
    t = s.tension
    lines.append("")
    lines.append("Tension")
    lines.append(f"  winner behind at halfway     {_pct(t['comeback_half'])}")
    lines.append(f"  winner behind before last   {_pct(t['comeback'])}")
    lines.append(f"  won outright in final round  {_pct(t['final_decided'])}")
    lines.append(f"  lead changes per game        {t['lead_changes']:.2f}")
    lines.append(f"  ending spread (0-1)          {t['ending_spread']:.2f}")
    lines.append("")
    lines.append("Distributions")
    lines.append("  per-player drift  " + _quantiles(s.drifts))
    lines.append("  round gap         " + _quantiles(s.gaps))
    if s.dominance:
        lines.append("")
        lines.append("Flags")
        lines += [f"  ! {f}" for f in s.dominance]
    return "\n".join(lines)


def _quantiles(a: np.ndarray) -> str:
    if not len(a):
        return "(none)"
    q = np.percentile(a, [5, 25, 50, 75, 95])
    return (f"mean {a.mean():+.1f}  sd {a.std():.1f}  "
            f"5/25/50/75/95%: " + " / ".join(f"{x:+.0f}" for x in q))
