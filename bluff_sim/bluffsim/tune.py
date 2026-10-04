"""Strategy search for the adaptive seats.

Best response
    Seats listed in `tuned_seats` share one parameter set (so both tuned
    seats play the same strategy) and face the fixed bots. A genetic search
    maximises their mean win score. Every candidate in a generation plays the
    same seeds (common random numbers) so differences are not luck; each
    generation uses fresh seeds so nothing overfits a fixed deal. The top
    candidates are then re-checked on a larger, separate set of games.

Self-play
    Start from the best-response winner as the "champion". Each iteration
    searches for a strategy that does best when it sits in one seat and the
    champion fills the others (the seat rotates to remove seat bias). If the
    challenger beats the champion's own score in that table, it becomes the
    new champion. A cross-play table afterwards shows whether later
    champions still beat earlier ones (convergence) or not (cycling).

Win score: 1 for a solo or bust win (shared among tied winners counts 1 for
each), `shared_value` for a shared win.
"""
from __future__ import annotations

import random
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field

import numpy as np

from .bots import make_table
from .bots.adaptive import Adaptive, Params
from .config import GameConfig
from .engine import END_SHARED, play_game
from .stats import default_workers


def _score(r, seat, shared_value):
    if seat not in r.winners:
        return 0.0
    return shared_value if r.end_type == END_SHARED else 1.0


def _eval_task(args):
    cfg, tables, seeds, shared_value = args
    # tables: list of (specs, scored seats)
    total = 0.0
    count = 0
    for specs, scored in tables:
        bots = make_table(specs)
        for s in seeds:
            r = play_game(cfg, bots, s)
            for seat in scored:
                total += _score(r, seat, shared_value)
                count += 1
    return total, count


class Evaluator:
    """Scores many candidates in parallel over shared seeds."""

    def __init__(self, cfg: GameConfig, workers: int | None = None,
                 shared_value: float = 1.0):
        self.cfg = cfg
        self.workers = workers or default_workers()
        self.shared_value = shared_value
        self.pool = (ProcessPoolExecutor(self.workers)
                     if self.workers > 1 else None)

    def close(self):
        if self.pool:
            self.pool.shutdown()

    def score(self, table_sets: list[list], seeds: list[int]) -> list[float]:
        """table_sets[i] is a list of (specs, scored seats) for candidate i.
        Returns each candidate's mean score over all its games."""
        n_chunks = max(1, self.workers * 2 // max(1, len(table_sets)))
        size = -(-len(seeds) // n_chunks)
        tasks, owner = [], []
        for i, tables in enumerate(table_sets):
            for k in range(0, len(seeds), size):
                tasks.append((self.cfg, tables, seeds[k:k + size],
                              self.shared_value))
                owner.append(i)
        if self.pool:
            results = list(self.pool.map(_eval_task, tasks))
        else:
            results = [_eval_task(t) for t in tasks]
        sums = [[0.0, 0] for _ in table_sets]
        for i, (tot, cnt) in zip(owner, results):
            sums[i][0] += tot
            sums[i][1] += cnt
        return [t / c if c else 0.0 for t, c in sums]


@dataclass
class SearchResult:
    best: Params
    best_score: float
    baseline_score: float
    history: list = field(default_factory=list)    # (gen, best, mean)
    finalists: list = field(default_factory=list)  # (validated score, Params)


def _seeds(rng: random.Random, n: int) -> list[int]:
    return [rng.randrange(1, 2**31) for _ in range(n)]


def genetic_search(evaluate, rng: random.Random, start: list[Params],
                   pop: int, gens: int, games: int, validate_games: int,
                   log=print) -> SearchResult:
    """`evaluate(params_list, seeds) -> scores`. Elitist GA with
    tournament selection, uniform crossover and Gaussian mutation."""
    population = list(start)[:pop]
    while len(population) < pop:
        population.append(Params.random(rng))
    history = []
    scored = []
    elite = max(2, pop // 6)
    for g in range(gens):
        seeds = _seeds(rng, games)
        scores = evaluate(population, seeds)
        scored = sorted(zip(scores, range(len(population))), reverse=True)
        best = scored[0][0]
        history.append((g + 1, best, float(np.mean(scores))))
        log(f"  generation {g + 1}/{gens}: best {best:.3f}  "
            f"mean {np.mean(scores):.3f}")
        if g == gens - 1:
            break
        ranked = [population[i] for _, i in scored]
        nxt = ranked[:elite]

        def pick():
            contenders = rng.sample(range(len(ranked)), 3)
            return ranked[min(contenders)]
        while len(nxt) < pop:
            child = Params.crossover(pick(), pick(), rng)
            nxt.append(child.mutate(rng))
        population = nxt

    finalists = [population[i] for _, i in scored[:5]]
    seeds = _seeds(rng, validate_games)
    v = evaluate(finalists + [Params()], seeds)
    ranked = sorted(zip(v[:-1], range(len(finalists))), reverse=True)
    best_score, bi = ranked[0]
    log(f"  validated on {validate_games} new games: best {best_score:.3f} "
        f"(default parameters {v[-1]:.3f})")
    return SearchResult(best=finalists[bi], best_score=best_score,
                        baseline_score=v[-1], history=history,
                        finalists=[(s, finalists[i]) for s, i in ranked])


def best_response(cfg: GameConfig, fixed: dict[int, str],
                  tuned_seats: list[int], ev: Evaluator, rng, pop=24,
                  gens=12, games=800, validate_games=6000,
                  log=print) -> SearchResult:
    """Tune one parameter set for `tuned_seats` against fixed bots."""
    def evaluate(params_list, seeds):
        sets = []
        for p in params_list:
            specs = [fixed.get(i) for i in range(cfg.n_players)]
            for s in tuned_seats:
                specs[s] = Adaptive(p, label="tuned")
            sets.append([(specs, tuned_seats)])
        return ev.score(sets, seeds)
    start = [Params()]
    return genetic_search(evaluate, rng, start, pop, gens, games,
                          validate_games, log)


def _vs_field(cfg, challenger: Params, champion: Params):
    """Tables with the challenger in each seat in turn, champion elsewhere."""
    n = cfg.n_players
    tables = []
    for seat in range(n):
        specs = [Adaptive(champion, "champion") for _ in range(n)]
        specs[seat] = Adaptive(challenger, "challenger")
        tables.append((specs, [seat]))
    return tables


@dataclass
class SelfPlayResult:
    champions: list           # Params, in order
    champion_scores: list     # champion's score against its own field
    challenger_scores: list   # best challenger's score vs previous champion
    accepted: list            # bool per iteration
    cross: np.ndarray         # cross[i][j]: champion i vs field of champion j
    verdict: str


def self_play(cfg: GameConfig, start: Params, ev: Evaluator, rng,
              iterations=4, pop=16, gens=8, games=600, validate_games=4000,
              log=print) -> SelfPlayResult:
    champions = [start]
    per_seat = max(1, games // cfg.n_players)
    v_per_seat = max(1, validate_games // cfg.n_players)
    champion_scores, challenger_scores, accepted = [], [], []
    for it in range(iterations):
        champ = champions[-1]
        log(f" self-play iteration {it + 1}/{iterations}")

        def evaluate(params_list, seeds):
            # Each seed is played once per seat, so a candidate plays
            # len(seeds) * n_players games.
            return ev.score([_vs_field(cfg, p, champ) for p in params_list],
                            seeds)
        start_pop = [champ] + [champ.mutate(rng, rate=0.5)
                               for _ in range(pop // 2)]
        res = genetic_search(evaluate, rng, start_pop, pop, gens,
                             per_seat, v_per_seat, log)
        seeds = _seeds(rng, v_per_seat)
        own, chal = ev.score([_vs_field(cfg, champ, champ),
                              _vs_field(cfg, res.best, champ)], seeds)
        champion_scores.append(own)
        challenger_scores.append(chal)
        se = np.sqrt(max(chal * (1 - chal), 1e-6) / (v_per_seat * cfg.n_players))
        take = chal > own + 2 * se
        accepted.append(bool(take))
        log(f"  champion in its own field {own:.3f}; best challenger "
            f"{chal:.3f} -> {'new champion' if take else 'champion holds'}")
        if take:
            champions.append(res.best)
        else:
            champions.append(champ)

    # Cross-play: does each champion still do well against earlier fields?
    uniq = []
    for c in champions:
        if not uniq or c is not uniq[-1]:
            uniq.append(c)
    k = len(uniq)
    seeds = _seeds(rng, v_per_seat)
    sets = [_vs_field(cfg, uniq[i], uniq[j]) for i in range(k)
            for j in range(k)]
    flat = ev.score(sets, seeds)
    cross = np.array(flat).reshape(k, k)
    verdict = _verdict(uniq, cross, accepted)
    return SelfPlayResult(champions=uniq, champion_scores=champion_scores,
                          challenger_scores=challenger_scores,
                          accepted=accepted, cross=cross, verdict=verdict)


def _verdict(uniq, cross, accepted) -> str:
    k = len(uniq)
    if k == 1:
        return ("Stable: no challenger beat the starting strategy in its own "
                "field, so the best-response strategy is already a "
                "self-play equilibrium at this search budget.")
    # Cycling: a later champion that an earlier champion beats on the later
    # champion's own field.
    cycles = []
    for j in range(1, k):
        for i in range(j - 1):
            if cross[i][j] > cross[j][j] + 0.02:
                cycles.append((i, j))
    drift = [uniq[i].distance(uniq[i + 1]) for i in range(k - 1)]
    tail = "accepted" if accepted and accepted[-1] else "held"
    if cycles:
        pairs = ", ".join(f"C{i} beats C{j}'s field" for i, j in cycles[:4])
        return (f"Cycling: earlier champions beat later ones on their own "
                f"ground ({pairs}). No single strategy dominates; expect "
                f"the meta to rotate.")
    if not accepted[-1]:
        return (f"Converging: champions changed {k - 1} time(s) and the "
                f"last challenger could not beat the champion "
                f"(parameter moves: {', '.join(f'{d:.2f}' for d in drift)}).")
    return (f"Still moving: the last iteration was {tail} with parameter "
            f"moves {', '.join(f'{d:.2f}' for d in drift)}; run more "
            f"iterations to see whether it settles.")
