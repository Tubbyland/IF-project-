# Bluffing game simulator

Monte Carlo simulator for a semi-cooperative bluffing card game. It plays
thousands of games with simple bots, reports how games end, and searches for
strong strategies.

This folder stands alone. It is unrelated to the interactive fiction game in
the rest of the repository.

## Setup

    cd bluff_sim
    pip install -r requirements.txt
    python -m pytest tests          # rule-resolution tests

## Running games

    python -m bluffsim run --games 10000
    python -m bluffsim run --seats honest,helper,drifter,anchor --games 5000
    python -m bluffsim run --set bust_limit=30 --set draw_per_round=2
    python -m bluffsim run --config configs/default.yaml --out results/run1 --decisive

`--out` writes `summary.txt`, charts (`endings.png`, `wins_by_seat.png`,
`drift.png`, `gap.png`), up to 50 winning games per seat as JSON lines in
`win_logs/`, and readable replays of typical wins (`replays.html`,
`replays.txt`). `--decisive` also prints the decisive-round analysis.

Strategies: `honest`, `helper`, `drifter`, `anchor`, `opportunist`,
`careful_drifter`, `adaptive`, and `adaptive:path/to/params.json` for a tuned
parameter file written by `experiment`.

Results are reproducible: game *i* always uses the same seed for a given
`--seed`, however many worker processes run.

## Rules and settings

Every rule parameter is a field of `GameConfig` in `bluffsim/config.py`.
`configs/default.yaml` lists them all with their defaults. Override any of
them with a file (`--config`) or on the command line (`--set key=value`).

How the draft's open questions were settled (all configurable where it makes
sense):

| Question | Decision |
|---|---|
| Track limits | Not clamped (`track_cap: null`). A track can pass 30. |
| Tied leaders | All tied players are leaders and none can veto. Round 1 has no vetoes. |
| When eligibility is measured | Tracks at the start of the veto phase. |
| Veto chains (A vetoes B, B vetoes C) | A takes only B's own pocket drift. |
| Group contribution after one veto | Unchanged (the real pocket total). |
| Final-round doubling | Tracks only. The tally is never doubled. |
| Bust boundary | Bust when \|tally\| > limit. Exactly 20 survives. |
| Cards per turn | 1 to 3 (`min_cards`, `max_cards`). |
| Target decks run out | Reshuffle used targets. |
| Hand deck | Grows (`hand_copies_auto`) so it can never run out, so it is never reshuffled. 4 players need 44 of 80 cards. 5 players drawing 2 need 85, so the deck becomes 5 copies of each value. |
| Clue bands | close = within ±2, lower/higher = 3–7, much = 8+. |
| "A steal caused a win" | In the game-ending round, removing that one veto changes the vetoer from winner to not winner. |
| Kingmaking | A player with \|drift\| ≥ 20 is vetoed by two or more players in the game-ending round, and a vetoer wins. |

## Sweeps

    python -m bluffsim sweep --games 3000 \
        --grid bust_limit=20,25,30,35,40 --grid veto_gap=5,10,15 \
        --grid draw_per_round=1,2 --out results/sweep

This writes `sweep.csv`, a Markdown table `sweep.md` (with any dominance
flags), a line chart of endings against each swept parameter, and heat maps
of shared-win and bust-win rates over the first two swept parameters. Any
`GameConfig` field can be swept. The table comes from `--seats` or the config
file.

## Main experiment: what does a winning strategy look like?

    python -m bluffsim experiment --out results/experiment
    python -m bluffsim experiment --set draw_per_round=2 --out results/draw2

Seat 1 is the Careful Drifter, seat 2 the Anchor, and seats 3 and 4 are
adaptive.

1. **Baseline:** seats 3 and 4 on default adaptive parameters.
2. **Best response:** a genetic search tunes one parameter set shared by
   seats 3 and 4 against the fixed bots. All candidates in a generation play
   the same deals, and each generation gets fresh deals. The top five are
   re-checked on 10,000 new games.
3. **Self-play:** the best-response strategy becomes the champion. Each
   iteration searches for a challenger that scores best with the champion
   in every other seat, rotating the challenger through all seats. A
   challenger that clearly beats the champion's own score replaces it. A
   cross-play table then shows whether the strategies converged or cycle.

Win score: 1 for a solo or bust win (a tie counts as a win for each tied
player), and `--shared-value` (default 1) for a shared win. Set it lower
(for example `--shared-value 0.25`) if a shared win should count for less.

Output in `--out`:

- `report.md`: parameters in plain language, search progress, the self-play
  verdict, and full summaries with decisive-round analysis for each table
- `best_response.json`, `self_play_champion.json`: tuned parameters, usable as
  `--seats careful_drifter,anchor,adaptive:results/experiment/best_response.json,...`
- `0_baseline/`, `1_best_response/`, `2_self_play/`,
  `3_champion_vs_fixed/`: summary, charts, win logs and replays for each table
- `search_log.txt`

Budget flags: `--pop`, `--gens`, `--games`, `--validate`, `--final-games`,
`--sp-iters`, `--sp-pop`, `--sp-gens`, `--sp-games`, `--skip-self-play`. The
defaults take about 15–20 minutes on 4 cores.

## The decisive round

For each win, the decisive round is the round with the largest swing toward
the winner:

- **Solo:** the biggest gain in the winner's distance from zero.
- **Bust:** the biggest gain in the winner's lead at being closest to zero.
- **Shared:** the biggest fall in \|tally\|.

The analysis reports, per seat and win type, which round it tended to be and
what the winner did in it: drift, cards played, whether its clue was a lie,
whether it vetoed or was vetoed.

## Code layout

    bluffsim/config.py      all rule parameters
    bluffsim/engine.py      rules only: resolve_round, check_end, play_game
    bluffsim/bots/base.py   Bot base class, card choice, reading clues
    bluffsim/bots/simple.py honest, helper, drifter, anchor, opportunist,
                            careful_drifter
    bluffsim/bots/adaptive.py  tunable policy and its parameter bounds
    bluffsim/stats.py       running games in parallel, summaries, flags
    bluffsim/replay.py      logs, replays, decisive rounds
    bluffsim/tune.py        best-response search and self-play
    bluffsim/sweep.py       parameter sweeps
    bluffsim/charts.py      PNG charts
    bluffsim/cli.py         command line

The engine never imports a strategy. Bots see only a `PublicState` (targets,
clues, card counts, discard pile, tracks, tally, history) and their own hand.

## Adding a strategy

1. Subclass `Bot` in `bluffsim/bots/` and give it a `name`.
2. Implement `play(seat, pub, hand) -> (cards, clue)`. `cards` is a tuple
   from `hand` with `min_cards`..`max_cards` cards. `clue` is −2..2 (much
   lower .. much higher).
3. Optionally implement `veto(seat, pub, hand, pocket) -> seat | None`. It
   is called only when the bot is eligible.
4. Add it to `STRATEGIES` in `bluffsim/bots/__init__.py`.

Helpers in `bots/base.py` do the common work. `pick_total` finds the cards
closest to a wanted total. `estimate_drift` reads another player's likely
drift from their clue, card count and the unseen cards. `drift_room` gives
the room left before the projected tally busts. `best_steal` picks the most
useful veto. `tests/test_rules.py` plays legal games with every registered
strategy, so a new one is checked automatically.

## How bots read clues (and the limits of that)

A bot treats another player's pocket as *n* random cards from the cards it
hasn't seen. It narrows that to the clue's band, then blends the result with
the unconditioned guess by its `trust`. It ignores that players choose their
cards on purpose, so estimates are rough by design. The aim is balance
signals, not strong play.
