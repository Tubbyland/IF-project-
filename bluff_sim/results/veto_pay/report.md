# Strategy search

Table: seat 1 careful_drifter, seat 2 anchor, seat 3 adaptive, seat 4 adaptive

Rules: n_players=4, hand_size=5, rounds=7, hand_lo=1, hand_hi=20, hand_copies=4, hand_copies_auto=True, personal_lo=15, personal_hi=30, personal_copies=2, collective_mode=split, collective_split=((70, 82), (98, 110)), collective_continuous=(75, 105), win_threshold=30, track_cap=None, bust_limit=20, min_cards=1, max_cards=3, draw_per_round=2, clue_close=2, clue_much=8, vetoes_enabled=True, veto_gap=10, veto_target=any, double_veto_at=2, veto_mode=take, veto_cost=1, final_multiplier=2, final_doubles_stolen=True, bust_win_requires_near_zero=False, bust_near_zero=5

Win score: solo/bust win 1, shared win 1.0.

## Baseline (adaptive seats on default parameters)

```
Baseline (default adaptive)
===========================
Games: 10000    Table: 1:careful_drifter, 2:anchor, 3:adaptive, 4:adaptive

How games end
  solo win         42.6%
  bust win         51.1%
  shared win        6.3%
  average length  4.04 rounds; 12% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         45.6%   38.4%    0.9%    6.3%   40.6%
  2: anchor                  49.0%    0.3%   42.4%    6.3%   41.1%
  3: adaptive                15.7%    2.1%    7.3%    6.3%    9.0%
  4: adaptive                16.4%    2.2%    8.0%    6.3%    9.4%

Wins by strategy (per seat it occupies)
  careful_drifter            45.6%   38.4%    0.9%
  anchor                     49.0%    0.3%   42.4%
  adaptive                   16.1%    2.1%    7.6%

Vetoes
  eligible players per round  1.44
  eligible players who veto     7.0%
  rounds with a veto            8.4%
  vetoes per game             0.41
  vetoed players hit twice+    15.4%
  average drift stolen (abs)  5.1
  games a steal decided         1.1%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner came from behind       14.6%
  lead changes per game        0.43
  ending spread (0-1)          0.80

Distributions
  per-player drift  mean -0.5  sd 5.4  5/25/50/75/95%: -10 / -3 / +0 / +2 / +10
  round gap         mean -0.0  sd 16.9  5/25/50/75/95%: -26 / -14 / +0 / +14 / +26
```

## Best response

Win score of the tuned seats: 0.363 (default parameters: 0.162).

What the tuned strategy does:

- Commits to a solo win once its track is 3+ from zero.
- When chasing it, drifts up to 12 a round before round 3, then up to 28.
- Keeps 10 of room between the projected tally and a bust.
- Anchors at zero when it is closest to zero and someone is 5+ further out.
- Gives 0% weight to closing the group's gap (41% in the final round).
- Lies on 45% of clues, by 1 band.
- Believes others' clues 45%.
- Vetoes when the steal is worth 11+ to its goal (2+ in the final round); counts blocking a leader at 144% of its size.
- In the final round, goes for the solo win if its track is 24+ from zero, keeping 4 of tally room.

Parameters:

```
{
 "solo_at": 3,
 "anchor_margin": 5,
 "aggr_early": 11.519,
 "aggr_late": 27.652,
 "late_round": 3,
 "room_margin": 10.206,
 "help_weight": 0.0,
 "lie_rate": 0.446,
 "lie_size": 1,
 "veto_threshold": 10.667,
 "deny_weight": 1.437,
 "trust": 0.453,
 "card_cost": 0.303,
 "extreme_cost": 0.391,
 "final_solo_at": 24,
 "final_room_margin": 4.454,
 "final_help_weight": 0.407,
 "final_veto_threshold": 1.876
}
```

Search progress (generation, best, mean): (1, 0.261, 0.185), (2, 0.305, 0.222), (3, 0.319, 0.248), (4, 0.320, 0.260), (5, 0.317, 0.255), (6, 0.338, 0.280), (7, 0.338, 0.299), (8, 0.334, 0.297), (9, 0.347, 0.310), (10, 0.345, 0.310), (11, 0.370, 0.320), (12, 0.377, 0.341), (13, 0.340, 0.307), (14, 0.357, 0.329), (15, 0.367, 0.323), (16, 0.359, 0.329), (17, 0.371, 0.325), (18, 0.363, 0.315), (19, 0.350, 0.314), (20, 0.356, 0.334)

```
Best response
=============
Games: 10000    Table: 1:careful_drifter, 2:anchor, 3:tuned, 4:tuned

How games end
  solo win         25.6%
  bust win         72.4%
  shared win        2.0%
  average length  3.26 rounds; 3% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         23.1%   20.3%    0.7%    2.0%   21.0%
  2: anchor                  50.2%    0.1%   48.0%    2.0%   33.7%
  3: tuned                   37.2%    2.8%   32.3%    2.0%   23.0%
  4: tuned                   36.3%    2.7%   31.6%    2.0%   22.3%

Wins by strategy (per seat it occupies)
  careful_drifter            23.1%   20.3%    0.7%
  anchor                     50.2%    0.1%   48.0%
  tuned                      36.8%    2.8%   32.0%

Vetoes
  eligible players per round  1.43
  eligible players who veto     2.9%
  rounds with a veto            3.8%
  vetoes per game             0.13
  vetoed players hit twice+     6.4%
  average drift stolen (abs)  7.8
  games a steal decided         1.5%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner came from behind       13.9%
  lead changes per game        0.25
  ending spread (0-1)          0.60

Distributions
  per-player drift  mean -0.6  sd 5.1  5/25/50/75/95%: -10 / -1 / +0 / +1 / +9
  round gap         mean +0.2  sd 16.9  5/25/50/75/95%: -26 / -14 / +0 / +14 / +27

Flags
  ! bust win ends 72% of games.
```

```
Decisive rounds (largest swing toward the winner)

Seat 1 (careful_drifter), bust wins: 73
  round of the swing     r1: 12%, r2: 42%, r3: 18%, r4: 19%, r5: 4%, r6: 4%
  swing size             mean 7.3
  was also the last      84%
  own drift              mean -6.2, mean |drift| 7.3
  cards played           mean 2.66
  clue was a lie         0%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: kept its own drift to about 7 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 1 (careful_drifter), solo wins: 2029
  round of the swing     r1: 50%, r2: 26%, r3: 17%, r4: 3%, r5: 1%, r6: 1%, r7: 1%
  swing size             mean 11.2
  was also the last      17%
  own drift              mean -3.7, mean |drift| 11.1
  cards played           mean 1.75
  clue was a lie         0%
  vetoed someone         1% (mean stolen when it did: -12.3)
  was vetoed             0%
  in plain words: pushed its own track by about 11; mostly told the truth.

Seat 2 (anchor), bust wins: 4803
  round of the swing     r1: 34%, r2: 39%, r3: 16%, r4: 6%, r5: 3%, r6: 1%, r7: 0%
  swing size             mean 1.5
  was also the last      45%
  own drift              mean +0.1, mean |drift| 0.8
  cards played           mean 2.05
  clue was a lie         99%
  vetoed someone         0% (mean stolen when it did: +1.3)
  was vetoed             0%
  in plain words: kept its own drift to about 1 while others moved away from zero; lied.

Seat 2 (anchor), solo wins: 12
  round of the swing     r2: 8%, r4: 25%, r5: 33%, r6: 17%, r7: 17%
  swing size             mean 21.2
  was also the last      75%
  own drift              mean -18.4, mean |drift| 18.4
  cards played           mean 2.33
  clue was a lie         58%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 18; lied; usually in the round the game ended.

Seat 3 (tuned), bust wins: 3230
  round of the swing     r1: 50%, r2: 26%, r3: 14%, r4: 7%, r5: 2%, r6: 1%, r7: 0%
  swing size             mean 1.0
  was also the last      44%
  own drift              mean +0.0, mean |drift| 0.4
  cards played           mean 2.02
  clue was a lie         45%
  vetoed someone         0% (mean stolen when it did: -4.9)
  was vetoed             0%
  in plain words: kept its own drift to about 0 while others moved away from zero; mostly told the truth.

Seat 3 (tuned), solo wins: 283
  round of the swing     r1: 1%, r2: 5%, r3: 48%, r4: 24%, r5: 11%, r6: 5%, r7: 6%
  swing size             mean 21.4
  was also the last      59%
  own drift              mean -8.9, mean |drift| 18.0
  cards played           mean 1.70
  clue was a lie         47%
  vetoed someone         31% (mean stolen when it did: -4.1)
  was vetoed             0%
  in plain words: pushed its own track by about 18; vetoed in 31% of them; mostly told the truth.

Seat 4 (tuned), bust wins: 3162
  round of the swing     r1: 49%, r2: 25%, r3: 15%, r4: 7%, r5: 3%, r6: 1%, r7: 0%
  swing size             mean 1.0
  was also the last      43%
  own drift              mean +0.0, mean |drift| 0.4
  cards played           mean 2.00
  clue was a lie         44%
  vetoed someone         0% (mean stolen when it did: -2.4)
  was vetoed             0%
  in plain words: kept its own drift to about 0 while others moved away from zero; mostly told the truth.

Seat 4 (tuned), solo wins: 268
  round of the swing     r1: 0%, r2: 5%, r3: 43%, r4: 34%, r5: 10%, r6: 3%, r7: 4%
  swing size             mean 22.5
  was also the last      62%
  own drift              mean -9.5, mean |drift| 18.7
  cards played           mean 1.65
  clue was a lie         44%
  vetoed someone         38% (mean stolen when it did: -5.9)
  was vetoed             1%
  in plain words: pushed its own track by about 19; vetoed in 38% of them; mostly told the truth; usually in the round the game ended.

```

```
Sensitivity (each parameter moved to its bounds; base score 0.360; differences under ~0.018 are noise)

  parameter                tuned          at low         at high  matters?
  solo_at                      3      0 -0.174      30 -0.015  yes
  help_weight                0.0      0 +0.000       1 -0.118  yes
  card_cost                0.303     -3 -0.083       3 -0.094  yes
  veto_threshold          10.667      0 -0.094      20 -0.003  yes
  extreme_cost             0.391      0 +0.006       4 -0.072  yes
  lie_rate                 0.446      0 +0.000       1 +0.008  no
  deny_weight              1.437      0 -0.007     1.5 +0.003  no
  lie_size                     1      1 +0.000       3 +0.007  no
  aggr_late               27.652      0 -0.005      30 +0.000  no
  aggr_early              11.519      0 +0.004      20 +0.001  no
  final_help_weight        0.407      0 -0.002       1 -0.004  no
  room_margin             10.206    -10 -0.001      15 +0.003  no
  final_solo_at               24      0 -0.003      30 +0.000  no
  late_round                   3      1 +0.001       7 -0.003  no
  final_veto_threshold     1.876      0 +0.001      20 -0.002  no
  trust                    0.453      0 +0.002       1 +0.002  no
  anchor_margin                5      2 +0.000      30 +0.001  no
  final_room_margin        4.454    -10 +0.000      15 +0.000  no
```
