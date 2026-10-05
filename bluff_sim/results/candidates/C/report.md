# Strategy search

Table: seat 1 careful_drifter, seat 2 anchor, seat 3 adaptive, seat 4 adaptive

Rules: n_players=4, hand_size=5, rounds=5, hand_lo=1, hand_hi=15, hand_copies=4, hand_copies_auto=True, personal_lo=10, personal_hi=20, personal_copies=2, personal_copies_auto=True, collective_mode=continuous, collective_split=((70, 82), (98, 110)), collective_continuous=(54, 66), win_threshold=20, track_cap=None, bust_limit=22, min_cards=1, max_cards=3, draw_per_round=1, clue_close=2, clue_much=8, vetoes_enabled=True, veto_gap=7, veto_target=any, double_veto_at=2, veto_mode=take, veto_cost=0, final_multiplier=2, final_doubles_stolen=True, bust_win_requires_near_zero=False, bust_near_zero=5

Win score: solo/bust win 1, shared win 1.0.

## Baseline (adaptive seats on default parameters)

```
Baseline (default adaptive)
===========================
Games: 6000    Table: 1:careful_drifter, 2:anchor, 3:adaptive, 4:adaptive

How games end
  solo win         44.8%
  bust win         45.9%
  shared win        9.3%
  average length  4.12 rounds; 45% reach round 5

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         48.2%   35.3%    3.6%    9.3%   40.7%
  2: anchor                  35.2%    2.9%   23.0%    9.3%   26.6%
  3: adaptive                25.4%    3.6%   12.5%    9.3%   17.0%
  4: adaptive                24.2%    3.1%   11.8%    9.3%   15.7%

Wins by strategy (per seat it occupies)
  careful_drifter            48.2%   35.3%    3.6%
  anchor                     35.2%    2.9%   23.0%
  adaptive                   24.8%    3.4%   12.1%

Vetoes
  eligible players per round  1.39
  eligible players who veto     5.3%
  rounds with a veto            6.5%
  vetoes per game             0.30
  vetoed players hit twice+     9.2%
  average drift stolen (abs)  7.1
  games a steal decided         1.8%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner behind at halfway      28.2%
  winner behind before last    30.4%
  won outright in final round   35.3%
  lead changes per game        0.78
  ending spread (0-1)          0.85

Distributions
  per-player drift  mean -1.2  sd 4.6  5/25/50/75/95%: -10 / -3 / +0 / +1 / +6
  round gap         mean -0.1  sd 6.9  5/25/50/75/95%: -12 / -5 / +0 / +5 / +11
```

## Best response

Win score of the tuned seats: 0.339 (default parameters: 0.246).

What the tuned strategy does:

- Commits to a solo win once its track is 25+ from zero.
- When chasing it, drifts up to 16 a round before round 6, then up to 25.
- Keeps 8 of room between the projected tally and a bust.
- Anchors at zero when it is closest to zero and someone is 8+ further out.
- Gives 72% weight to closing the group's gap (71% in the final round).
- Lies on 100% of clues, by 3 bands.
- Believes others' clues 20%.
- Vetoes when the steal is worth 0+ to its goal (6+ in the final round); counts blocking a leader at 150% of its size.
- Prefers playing many cards.
- Hoards very high and very low cards.
- Also blocks any player it expects to end the round within 8 of the solo threshold, leader or not.
- In the final round, goes for the solo win if its track is 3+ from zero, keeping -6 of tally room.

Parameters:

```
{
 "solo_at": 25,
 "anchor_margin": 8,
 "aggr_early": 16.008,
 "aggr_late": 25.293,
 "late_round": 6,
 "room_margin": 8.185,
 "help_weight": 0.719,
 "lie_rate": 1.0,
 "lie_size": 3,
 "veto_threshold": 0.455,
 "deny_weight": 1.5,
 "trust": 0.203,
 "card_cost": -2.617,
 "extreme_cost": 2.146,
 "final_solo_at": 3,
 "final_room_margin": -6.016,
 "final_help_weight": 0.706,
 "final_veto_threshold": 5.954,
 "danger_margin": 8
}
```

Search progress (generation, best, mean): (1, 0.281, 0.234), (2, 0.302, 0.241), (3, 0.301, 0.261), (4, 0.318, 0.285), (5, 0.336, 0.282), (6, 0.323, 0.300), (7, 0.327, 0.309), (8, 0.338, 0.309), (9, 0.354, 0.332), (10, 0.330, 0.306)

```
Best response
=============
Games: 6000    Table: 1:careful_drifter, 2:anchor, 3:tuned, 4:tuned

How games end
  solo win         43.2%
  bust win         44.5%
  shared win       12.2%
  average length  4.49 rounds; 63% reach round 5

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         30.1%   12.2%    5.6%   12.2%   20.1%
  2: anchor                  43.4%    4.1%   27.0%   12.2%   32.9%
  3: tuned                   34.6%   14.3%    8.0%   12.2%   24.5%
  4: tuned                   32.8%   13.3%    7.3%   12.2%   22.6%

Wins by strategy (per seat it occupies)
  careful_drifter            30.1%   12.2%    5.6%
  anchor                     43.4%    4.1%   27.0%
  tuned                      33.7%   13.8%    7.6%

Vetoes
  eligible players per round  1.24
  eligible players who veto    42.8%
  rounds with a veto           38.3%
  vetoes per game             2.38
  vetoed players hit twice+    18.5%
  average drift stolen (abs)  6.9
  games a steal decided        14.2%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner behind at halfway      47.6%
  winner behind before last    53.4%
  won outright in final round   50.7%
  lead changes per game        1.86
  ending spread (0-1)          0.89

Distributions
  per-player drift  mean -1.1  sd 6.2  5/25/50/75/95%: -11 / -5 / -1 / +2 / +9
  round gap         mean -0.0  sd 6.9  5/25/50/75/95%: -12 / -5 / +0 / +5 / +11
```

```
Decisive rounds (largest swing toward the winner)

Seat 1 (careful_drifter), bust wins: 335
  round of the swing     r1: 0%, r2: 2%, r3: 7%, r4: 30%, r5: 61%
  swing size             mean 12.1
  was also the last      79%
  own drift              mean -5.4, mean |drift| 6.8
  cards played           mean 1.22
  clue was a lie         0%
  vetoed someone         7% (mean stolen when it did: +2.4)
  was vetoed             26%
  in plain words: kept its own drift to about 7 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 1 (careful_drifter), solo wins: 735
  round of the swing     r1: 24%, r2: 12%, r3: 8%, r4: 22%, r5: 34%
  swing size             mean 12.7
  was also the last      63%
  own drift              mean -6.4, mean |drift| 9.5
  cards played           mean 1.47
  clue was a lie         0%
  vetoed someone         11% (mean stolen when it did: -5.7)
  was vetoed             0%
  in plain words: pushed its own track by about 9; mostly told the truth; usually in the round the game ended.

Seat 2 (anchor), bust wins: 1622
  round of the swing     r1: 19%, r2: 14%, r3: 18%, r4: 24%, r5: 24%
  swing size             mean 6.5
  was also the last      44%
  own drift              mean -0.8, mean |drift| 1.7
  cards played           mean 1.70
  clue was a lie         99%
  vetoed someone         0% (mean stolen when it did: +0.2)
  was vetoed             15%
  in plain words: kept its own drift to about 2 while others moved away from zero; lied.

Seat 2 (anchor), solo wins: 245
  round of the swing     r2: 1%, r3: 11%, r4: 17%, r5: 71%
  swing size             mean 20.1
  was also the last      89%
  own drift              mean -11.6, mean |drift| 11.7
  cards played           mean 1.19
  clue was a lie         98%
  vetoed someone         12% (mean stolen when it did: -5.0)
  was vetoed             1%
  in plain words: pushed its own track by about 12; lied; usually in the round the game ended.

Seat 3 (tuned), bust wins: 482
  round of the swing     r1: 0%, r2: 10%, r3: 12%, r4: 37%, r5: 41%
  swing size             mean 10.3
  was also the last      75%
  own drift              mean -3.7, mean |drift| 6.7
  cards played           mean 1.47
  clue was a lie         100%
  vetoed someone         19% (mean stolen when it did: -3.3)
  was vetoed             10%
  in plain words: kept its own drift to about 7 while others moved away from zero; lied; usually in the round the game ended.

Seat 3 (tuned), solo wins: 860
  round of the swing     r1: 1%, r2: 6%, r3: 20%, r4: 19%, r5: 55%
  swing size             mean 20.9
  was also the last      89%
  own drift              mean -0.7, mean |drift| 11.3
  cards played           mean 1.63
  clue was a lie         99%
  vetoed someone         57% (mean stolen when it did: -7.5)
  was vetoed             3%
  in plain words: pushed its own track by about 11; vetoed in 57% of them; lied; usually in the round the game ended.

Seat 4 (tuned), bust wins: 436
  round of the swing     r2: 13%, r3: 13%, r4: 31%, r5: 43%
  swing size             mean 9.4
  was also the last      68%
  own drift              mean -0.5, mean |drift| 6.3
  cards played           mean 1.67
  clue was a lie         100%
  vetoed someone         19% (mean stolen when it did: -4.3)
  was vetoed             11%
  in plain words: kept its own drift to about 6 while others moved away from zero; lied; usually in the round the game ended.

Seat 4 (tuned), solo wins: 798
  round of the swing     r1: 1%, r2: 1%, r3: 17%, r4: 18%, r5: 63%
  swing size             mean 21.7
  was also the last      91%
  own drift              mean -1.0, mean |drift| 10.9
  cards played           mean 1.67
  clue was a lie         98%
  vetoed someone         56% (mean stolen when it did: -9.6)
  was vetoed             4%
  in plain words: pushed its own track by about 11; vetoed in 56% of them; lied; usually in the round the game ended.

```

```
Sensitivity (each parameter moved to its bounds; base score 0.327; differences under ~0.022 are noise)

  parameter                tuned          at low         at high  matters?
  card_cost               -2.617     -3 -0.004       3 -0.067  yes
  veto_threshold           0.455      0 -0.000      20 -0.067  yes
  trust                    0.203      0 -0.006       1 -0.061  yes
  deny_weight                1.5      0 -0.053     1.5 +0.000  yes
  final_help_weight        0.706      0 -0.038       1 -0.002  a little
  lie_rate                   1.0      0 -0.031       1 +0.000  a little
  lie_size                     3      1 -0.025       3 +0.000  a little
  help_weight              0.719      0 -0.021       1 -0.003  no
  extreme_cost             2.146      0 -0.002       4 -0.016  no
  danger_margin                8      0 -0.010      30 -0.014  no
  final_veto_threshold     5.954      0 +0.001      20 -0.011  no
  solo_at                     25      0 -0.005      30 +0.000  no
  anchor_margin                8      2 +0.001      30 +0.003  no
  final_solo_at                3      0 -0.002      30 +0.001  no
  final_room_margin       -6.016    -10 +0.000      15 -0.001  no
  aggr_early              16.008      0 +0.000      20 +0.000  no
  aggr_late               25.293      0 +0.000      30 +0.000  no
  late_round                   6      1 +0.000       7 +0.000  no
  room_margin              8.185    -10 +0.000      15 +0.000  no
```

## Self-play

Converging: champions changed 1 time(s) and the last challenger could not beat the champion (parameter moves: 0.12).

Per iteration (champion in own field -> best challenger): 0.360 -> 0.427 (new), 0.383 -> 0.373, 0.405 -> 0.402

Cross-play: row = strategy in one seat, column = strategy in the other seats; value = row's win score. C0 is the best-response strategy.

```
  C0: 0.354  0.360
  C1: 0.404  0.384
```

What the final champion does:

- Almost never commits to a solo win before the final round.
- When chasing it, drifts up to 16 a round before round 7, then up to 24.
- Keeps 0 of room between the projected tally and a bust.
- Anchors at zero when it is closest to zero and someone is 2+ further out.
- Gives 37% weight to closing the group's gap (71% in the final round).
- Lies on 77% of clues, by 3 bands.
- Believes others' clues 0%.
- Vetoes when the steal is worth 0+ to its goal (6+ in the final round); counts blocking a leader at 133% of its size.
- Prefers playing many cards.
- Also blocks any player it expects to end the round within 8 of the solo threshold, leader or not.
- In the final round, goes for the solo win if its track is 0+ from zero, keeping -3 of tally room.

```
Self-play champion, all seats
=============================
Games: 6000    Table: 1:champion, 2:champion, 3:champion, 4:champion

How games end
  solo win         56.3%
  bust win         24.9%
  shared win       18.8%
  average length  4.86 rounds; 88% reach round 5

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: champion                40.4%   14.1%    7.4%   18.8%   25.4%
  2: champion                38.5%   13.0%    6.7%   18.8%   23.8%
  3: champion                40.1%   15.3%    6.0%   18.8%   25.3%
  4: champion                40.4%   14.8%    6.8%   18.8%   25.5%

Wins by strategy (per seat it occupies)
  champion                   39.8%   14.3%    6.7%

Vetoes
  eligible players per round  0.51
  eligible players who veto    84.6%
  rounds with a veto           24.8%
  vetoes per game             2.11
  vetoed players hit twice+    32.1%
  average drift stolen (abs)  12.2
  games a steal decided        22.9%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 10 games (0.2%)

Tension
  winner behind at halfway      70.3%
  winner behind before last    76.8%
  won outright in final round   69.4%
  lead changes per game        2.76
  ending spread (0-1)          0.90

Distributions
  per-player drift  mean -0.8  sd 5.6  5/25/50/75/95%: -11 / -4 / +0 / +3 / +8
  round gap         mean -0.0  sd 7.0  5/25/50/75/95%: -12 / -5 / +0 / +5 / +12
```

```
Decisive rounds (largest swing toward the winner)

Seat 1 (champion), bust wins: 447
  round of the swing     r1: 6%, r2: 4%, r3: 10%, r4: 20%, r5: 61%
  swing size             mean 9.3
  was also the last      78%
  own drift              mean -2.7, mean |drift| 5.2
  cards played           mean 1.50
  clue was a lie         77%
  vetoed someone         10% (mean stolen when it did: -1.5)
  was vetoed             19%
  in plain words: kept its own drift to about 5 while others moved away from zero; lied; usually in the round the game ended.

Seat 1 (champion), solo wins: 845
  round of the swing     r2: 0%, r3: 3%, r4: 8%, r5: 88%
  swing size             mean 26.5
  was also the last      97%
  own drift              mean -7.1, mean |drift| 9.5
  cards played           mean 1.24
  clue was a lie         79%
  vetoed someone         58% (mean stolen when it did: -13.9)
  was vetoed             10%
  in plain words: pushed its own track by about 9; vetoed in 58% of them; lied; usually in the round the game ended.

Seat 2 (champion), bust wins: 401
  round of the swing     r1: 2%, r2: 5%, r3: 7%, r4: 25%, r5: 61%
  swing size             mean 9.7
  was also the last      79%
  own drift              mean -4.0, mean |drift| 6.5
  cards played           mean 1.37
  clue was a lie         76%
  vetoed someone         10% (mean stolen when it did: -2.2)
  was vetoed             23%
  in plain words: kept its own drift to about 6 while others moved away from zero; lied; usually in the round the game ended.

Seat 2 (champion), solo wins: 782
  round of the swing     r2: 1%, r3: 3%, r4: 10%, r5: 86%
  swing size             mean 25.8
  was also the last      97%
  own drift              mean -5.5, mean |drift| 9.9
  cards played           mean 1.28
  clue was a lie         77%
  vetoed someone         51% (mean stolen when it did: -14.1)
  was vetoed             8%
  in plain words: pushed its own track by about 10; vetoed in 51% of them; lied; usually in the round the game ended.

Seat 3 (champion), bust wins: 358
  round of the swing     r1: 1%, r2: 9%, r3: 8%, r4: 18%, r5: 65%
  swing size             mean 9.5
  was also the last      77%
  own drift              mean -2.2, mean |drift| 5.8
  cards played           mean 1.51
  clue was a lie         79%
  vetoed someone         14% (mean stolen when it did: -2.6)
  was vetoed             24%
  in plain words: kept its own drift to about 6 while others moved away from zero; lied; usually in the round the game ended.

Seat 3 (champion), solo wins: 920
  round of the swing     r1: 0%, r3: 2%, r4: 7%, r5: 90%
  swing size             mean 25.9
  was also the last      98%
  own drift              mean -3.7, mean |drift| 9.9
  cards played           mean 1.42
  clue was a lie         78%
  vetoed someone         51% (mean stolen when it did: -15.3)
  was vetoed             9%
  in plain words: pushed its own track by about 10; vetoed in 51% of them; lied; usually in the round the game ended.

Seat 4 (champion), bust wins: 407
  round of the swing     r2: 11%, r3: 16%, r4: 18%, r5: 55%
  swing size             mean 9.4
  was also the last      71%
  own drift              mean -0.2, mean |drift| 6.4
  cards played           mean 1.64
  clue was a lie         76%
  vetoed someone         12% (mean stolen when it did: -4.6)
  was vetoed             29%
  in plain words: kept its own drift to about 6 while others moved away from zero; lied; usually in the round the game ended.

Seat 4 (champion), solo wins: 887
  round of the swing     r1: 0%, r2: 0%, r3: 2%, r4: 10%, r5: 87%
  swing size             mean 24.8
  was also the last      97%
  own drift              mean -1.9, mean |drift| 10.5
  cards played           mean 1.62
  clue was a lie         77%
  vetoed someone         46% (mean stolen when it did: -17.7)
  was vetoed             8%
  in plain words: pushed its own track by about 10; vetoed in 46% of them; lied; usually in the round the game ended.

```

```
Self-play champion against the fixed bots
=========================================
Games: 6000    Table: 1:careful_drifter, 2:anchor, 3:champion, 4:champion

How games end
  solo win         39.6%
  bust win         46.5%
  shared win       13.8%
  average length  4.60 rounds; 68% reach round 5

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         32.9%   13.7%    5.4%   13.8%   21.8%
  2: anchor                  45.7%    2.6%   29.2%   13.8%   33.9%
  3: champion                33.9%   12.4%    7.7%   13.8%   22.5%
  4: champion                33.2%   11.5%    7.9%   13.8%   21.8%

Wins by strategy (per seat it occupies)
  careful_drifter            32.9%   13.7%    5.4%
  anchor                     45.7%    2.6%   29.2%
  champion                   33.6%   11.9%    7.8%

Vetoes
  eligible players per round  1.25
  eligible players who veto    48.6%
  rounds with a veto           40.9%
  vetoes per game             2.79
  vetoed players hit twice+    22.2%
  average drift stolen (abs)  7.4
  games a steal decided        14.0%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner behind at halfway      47.3%
  winner behind before last    51.3%
  won outright in final round   54.0%
  lead changes per game        1.56
  ending spread (0-1)          0.91

Distributions
  per-player drift  mean -1.2  sd 5.4  5/25/50/75/95%: -11 / -4 / -1 / +2 / +7
  round gap         mean -0.0  sd 6.9  5/25/50/75/95%: -12 / -5 / +0 / +5 / +11
```
