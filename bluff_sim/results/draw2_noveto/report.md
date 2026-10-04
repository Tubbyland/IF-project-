# Strategy search

Table: seat 1 careful_drifter, seat 2 anchor, seat 3 adaptive, seat 4 adaptive

Rules: n_players=4, hand_size=5, rounds=7, hand_lo=1, hand_hi=20, hand_copies=4, hand_copies_auto=True, personal_lo=15, personal_hi=30, personal_copies=2, collective_mode=split, collective_split=((70, 82), (98, 110)), collective_continuous=(75, 105), win_threshold=30, track_cap=None, bust_limit=20, min_cards=1, max_cards=3, draw_per_round=2, clue_close=2, clue_much=8, vetoes_enabled=False, veto_gap=10, veto_target=any, double_veto_at=2, final_multiplier=2, final_doubles_stolen=True, bust_win_requires_near_zero=False, bust_near_zero=5

Win score: solo/bust win 1, shared win 1.0.

## Baseline (adaptive seats on default parameters)

```
Baseline (default adaptive)
===========================
Games: 10000    Table: 1:careful_drifter, 2:anchor, 3:adaptive, 4:adaptive

How games end
  solo win         47.6%
  bust win         47.2%
  shared win        5.2%
  average length  3.95 rounds; 10% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         49.8%   43.6%    1.0%    5.2%   45.5%
  2: anchor                  44.0%    0.1%   38.6%    5.2%   37.1%
  3: adaptive                14.1%    2.2%    6.7%    5.2%    8.4%
  4: adaptive                15.2%    1.9%    8.1%    5.2%    9.0%

Wins by strategy (per seat it occupies)
  careful_drifter            49.8%   43.6%    1.0%
  anchor                     44.0%    0.1%   38.6%
  adaptive                   14.7%    2.0%    7.4%

Vetoes
  eligible players per round  0.00
  eligible players who veto     0.0%
  rounds with a veto            0.0%
  vetoes per game             0.00
  vetoed players hit twice+     0.0%
  average drift stolen (abs)  0.0
  games a steal decided         0.0%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner came from behind       14.0%
  lead changes per game        0.41
  ending spread (0-1)          0.78

Distributions
  per-player drift  mean -0.5  sd 5.4  5/25/50/75/95%: -10 / -3 / +0 / +2 / +9
  round gap         mean -0.0  sd 16.9  5/25/50/75/95%: -26 / -14 / +0 / +14 / +26
```

## Best response

Win score of the tuned seats: 0.363 (default parameters: 0.147).

What the tuned strategy does:

- Always plays for a solo win.
- When chasing it, drifts up to 0 a round before round 7, then up to 17.
- Keeps 15 of room between the projected tally and a bust.
- Rarely plays as an anchor.
- Gives 0% weight to closing the group's gap (32% in the final round).
- Lies on 90% of clues, by 2 bands.
- Believes others' clues 23%.
- Vetoes when the steal is worth 20+ to its goal (13+ in the final round); counts blocking a leader at 128% of its size.
- In the final round, goes for the solo win if its track is 15+ from zero, keeping 2 of tally room.

Parameters:

```
{
 "solo_at": 2,
 "anchor_margin": 30,
 "aggr_early": 0.0,
 "aggr_late": 16.613,
 "late_round": 7,
 "room_margin": 15.0,
 "help_weight": 0.0,
 "lie_rate": 0.905,
 "lie_size": 2,
 "veto_threshold": 20.0,
 "deny_weight": 1.283,
 "trust": 0.232,
 "card_cost": 0.23,
 "extreme_cost": 0.0,
 "final_solo_at": 15,
 "final_room_margin": 1.951,
 "final_help_weight": 0.322,
 "final_veto_threshold": 12.581
}
```

Search progress (generation, best, mean): (1, 0.240, 0.169), (2, 0.314, 0.193), (3, 0.324, 0.222), (4, 0.343, 0.261), (5, 0.336, 0.282), (6, 0.338, 0.309), (7, 0.340, 0.306), (8, 0.360, 0.329), (9, 0.357, 0.315), (10, 0.341, 0.311), (11, 0.354, 0.304), (12, 0.362, 0.320), (13, 0.360, 0.326), (14, 0.351, 0.309), (15, 0.380, 0.317), (16, 0.382, 0.323), (17, 0.371, 0.321), (18, 0.357, 0.302), (19, 0.381, 0.330), (20, 0.367, 0.320)

```
Best response
=============
Games: 10000    Table: 1:careful_drifter, 2:anchor, 3:tuned, 4:tuned

How games end
  solo win         23.2%
  bust win         73.7%
  shared win        3.1%
  average length  3.38 rounds; 5% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         26.5%   22.6%    0.8%    3.1%   23.8%
  2: anchor                  51.2%    0.2%   47.9%    3.1%   33.8%
  3: tuned                   36.1%    0.3%   32.7%    3.1%   20.8%
  4: tuned                   36.6%    0.2%   33.3%    3.1%   21.5%

Wins by strategy (per seat it occupies)
  careful_drifter            26.5%   22.6%    0.8%
  anchor                     51.2%    0.2%   47.9%
  tuned                      36.3%    0.2%   33.0%

Vetoes
  eligible players per round  0.00
  eligible players who veto     0.0%
  rounds with a veto            0.0%
  vetoes per game             0.00
  vetoed players hit twice+     0.0%
  average drift stolen (abs)  0.0
  games a steal decided         0.0%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner came from behind       11.6%
  lead changes per game        0.18
  ending spread (0-1)          0.61

Distributions
  per-player drift  mean -0.6  sd 4.6  5/25/50/75/95%: -10 / -1 / +0 / +1 / +9
  round gap         mean +0.0  sd 16.9  5/25/50/75/95%: -26 / -14 / +0 / +14 / +26

Flags
  ! bust win ends 74% of games.
```

```
Decisive rounds (largest swing toward the winner)

Seat 1 (careful_drifter), bust wins: 80
  round of the swing     r1: 5%, r2: 29%, r3: 29%, r4: 19%, r5: 6%, r6: 4%, r7: 9%
  swing size             mean 9.3
  was also the last      68%
  own drift              mean -7.7, mean |drift| 8.3
  cards played           mean 2.56
  clue was a lie         0%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: kept its own drift to about 8 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 1 (careful_drifter), solo wins: 2259
  round of the swing     r1: 52%, r2: 21%, r3: 17%, r4: 4%, r5: 1%, r6: 2%, r7: 2%
  swing size             mean 11.3
  was also the last      16%
  own drift              mean -4.2, mean |drift| 11.1
  cards played           mean 1.75
  clue was a lie         0%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 11; mostly told the truth.

Seat 2 (anchor), bust wins: 4790
  round of the swing     r1: 33%, r2: 38%, r3: 19%, r4: 7%, r5: 2%, r6: 1%, r7: 1%
  swing size             mean 1.4
  was also the last      43%
  own drift              mean +0.2, mean |drift| 0.9
  cards played           mean 2.04
  clue was a lie         99%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: kept its own drift to about 1 while others moved away from zero; lied.

Seat 2 (anchor), solo wins: 20
  round of the swing     r2: 10%, r3: 15%, r4: 25%, r5: 10%, r7: 40%
  swing size             mean 22.5
  was also the last      70%
  own drift              mean -16.6, mean |drift| 16.6
  cards played           mean 2.45
  clue was a lie         60%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 17; lied; usually in the round the game ended.

Seat 3 (tuned), bust wins: 3269
  round of the swing     r1: 47%, r2: 26%, r3: 16%, r4: 7%, r5: 3%, r6: 1%, r7: 0%
  swing size             mean 1.0
  was also the last      42%
  own drift              mean +0.1, mean |drift| 0.5
  cards played           mean 2.04
  clue was a lie         90%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: kept its own drift to about 0 while others moved away from zero; lied.

Seat 3 (tuned), solo wins: 27
  round of the swing     r1: 4%, r2: 4%, r3: 11%, r4: 11%, r5: 7%, r6: 7%, r7: 56%
  swing size             mean 21.0
  was also the last      74%
  own drift              mean -12.9, mean |drift| 14.2
  cards played           mean 2.19
  clue was a lie         93%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 14; lied; usually in the round the game ended.

Seat 4 (tuned), bust wins: 3326
  round of the swing     r1: 46%, r2: 27%, r3: 17%, r4: 7%, r5: 3%, r6: 1%, r7: 0%
  swing size             mean 1.0
  was also the last      42%
  own drift              mean +0.1, mean |drift| 0.5
  cards played           mean 2.00
  clue was a lie         90%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: kept its own drift to about 0 while others moved away from zero; lied.

Seat 4 (tuned), solo wins: 21
  round of the swing     r2: 10%, r3: 14%, r4: 5%, r5: 24%, r6: 5%, r7: 43%
  swing size             mean 19.3
  was also the last      81%
  own drift              mean -14.3, mean |drift| 14.3
  cards played           mean 2.05
  clue was a lie         81%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 14; lied; usually in the round the game ended.

```

```
Sensitivity (each parameter moved to its bounds; base score 0.366; differences under ~0.018 are noise)

  parameter                tuned          at low         at high  matters?
  help_weight                0.0      0 +0.000       1 -0.176  yes
  card_cost                 0.23     -3 -0.094       3 -0.102  yes
  extreme_cost               0.0      0 +0.000       4 -0.090  yes
  lie_rate                 0.905      0 -0.019       1 +0.005  a little
  solo_at                      2      0 -0.018      30 -0.018  no
  room_margin               15.0    -10 -0.012      15 +0.000  no
  lie_size                     2      1 -0.011       3 -0.001  no
  final_solo_at               15      0 -0.008      30 -0.000  no
  final_help_weight        0.322      0 -0.005       1 -0.007  no
  late_round                   7      1 -0.004       7 +0.000  no
  aggr_early                 0.0      0 +0.000      20 -0.003  no
  trust                    0.232      0 -0.001       1 -0.001  no
  final_room_margin        1.951    -10 -0.000      15 +0.000  no
  anchor_margin               30      2 -0.000      30 +0.000  no
  aggr_late               16.613      0 +0.000      30 +0.000  no
  veto_threshold            20.0      0 +0.000      20 +0.000  no
  deny_weight              1.283      0 +0.000     1.5 +0.000  no
  final_veto_threshold    12.581      0 +0.000      20 +0.000  no
```

## Self-play

Cycling: earlier champions beat later ones on their own ground (C0 beats C2's field, C0 beats C3's field, C0 beats C4's field, C1 beats C4's field). No single strategy dominates; expect the meta to rotate.

Per iteration (champion in own field -> best challenger): 0.518 -> 0.677 (new), 0.299 -> 0.638 (new), 0.473 -> 0.613 (new), 0.354 -> 0.564 (new), 0.428 -> 0.630 (new)

Cross-play: row = strategy in one seat, column = strategy in the other seats; value = row's win score. C0 is the best-response strategy.

```
  C0: 0.519  0.647  0.505  0.539  0.611  0.546
  C1: 0.676  0.292  0.610  0.316  0.630  0.289
  C2: 0.490  0.645  0.478  0.504  0.583  0.534
  C3: 0.672  0.299  0.615  0.351  0.628  0.316
  C4: 0.323  0.661  0.305  0.560  0.420  0.576
  C5: 0.672  0.314  0.606  0.347  0.624  0.334
```

What the final champion does:

- Commits to a solo win once its track is 11+ from zero.
- When chasing it, drifts up to 16 a round before round 2, then up to 22.
- Keeps 6 of room between the projected tally and a bust.
- Anchors at zero when it is closest to zero and someone is 11+ further out.
- Gives 87% weight to closing the group's gap (76% in the final round).
- Lies on 67% of clues, by 1 band.
- Believes others' clues 22%.
- Vetoes when the steal is worth 13+ to its goal (9+ in the final round); counts blocking a leader at 41% of its size.
- Prefers playing many cards.
- In the final round, goes for the solo win if its track is 28+ from zero, keeping 15 of tally room.

```
Self-play champion, all seats
=============================
Games: 10000    Table: 1:champion, 2:champion, 3:champion, 4:champion

How games end
  solo win         30.8%
  bust win         60.1%
  shared win        9.1%
  average length  4.00 rounds; 19% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: champion                34.6%    9.6%   15.9%    9.1%   26.5%
  2: champion                31.9%    7.7%   15.2%    9.1%   23.9%
  3: champion                31.0%    8.2%   13.8%    9.1%   22.8%
  4: champion                35.0%    5.6%   20.3%    9.1%   26.8%

Wins by strategy (per seat it occupies)
  champion                   33.1%    7.8%   16.3%

Vetoes
  eligible players per round  0.00
  eligible players who veto     0.0%
  rounds with a veto            0.0%
  vetoes per game             0.00
  vetoed players hit twice+     0.0%
  average drift stolen (abs)  0.0
  games a steal decided         0.0%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner came from behind       50.2%
  lead changes per game        1.61
  ending spread (0-1)          0.81

Distributions
  per-player drift  mean -0.2  sd 9.8  5/25/50/75/95%: -16 / -6 / +0 / +5 / +17
  round gap         mean +0.0  sd 16.9  5/25/50/75/95%: -26 / -14 / +0 / +14 / +26
```

```
Decisive rounds (largest swing toward the winner)

Seat 1 (champion), bust wins: 1588
  round of the swing     r1: 16%, r2: 38%, r3: 19%, r4: 13%, r5: 8%, r6: 4%, r7: 2%
  swing size             mean 11.3
  was also the last      84%
  own drift              mean -0.1, mean |drift| 9.0
  cards played           mean 2.29
  clue was a lie         69%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: kept its own drift to about 9 while others moved away from zero; lied; usually in the round the game ended.

Seat 1 (champion), solo wins: 959
  round of the swing     r1: 50%, r2: 1%, r3: 3%, r4: 11%, r5: 22%, r6: 2%, r7: 10%
  swing size             mean 19.9
  was also the last      38%
  own drift              mean -0.2, mean |drift| 18.7
  cards played           mean 2.06
  clue was a lie         62%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 19; lied.

Seat 2 (champion), bust wins: 1515
  round of the swing     r1: 17%, r2: 27%, r3: 29%, r4: 13%, r5: 7%, r6: 4%, r7: 3%
  swing size             mean 11.2
  was also the last      78%
  own drift              mean -1.9, mean |drift| 9.4
  cards played           mean 2.26
  clue was a lie         69%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: kept its own drift to about 9 while others moved away from zero; lied; usually in the round the game ended.

Seat 2 (champion), solo wins: 766
  round of the swing     r1: 10%, r2: 41%, r3: 2%, r4: 6%, r5: 12%, r6: 20%, r7: 8%
  swing size             mean 18.9
  was also the last      50%
  own drift              mean +1.9, mean |drift| 18.6
  cards played           mean 2.16
  clue was a lie         61%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 19; lied.

Seat 3 (champion), bust wins: 1375
  round of the swing     r1: 25%, r2: 22%, r3: 20%, r4: 18%, r5: 9%, r6: 4%, r7: 2%
  swing size             mean 8.6
  was also the last      79%
  own drift              mean -0.9, mean |drift| 8.9
  cards played           mean 2.34
  clue was a lie         70%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: kept its own drift to about 9 while others moved away from zero; lied; usually in the round the game ended.

Seat 3 (champion), solo wins: 816
  round of the swing     r1: 1%, r2: 7%, r3: 34%, r4: 2%, r5: 4%, r6: 10%, r7: 41%
  swing size             mean 24.2
  was also the last      68%
  own drift              mean +1.4, mean |drift| 18.8
  cards played           mean 2.09
  clue was a lie         58%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 19; lied; usually in the round the game ended.

Seat 4 (champion), bust wins: 2033
  round of the swing     r1: 43%, r2: 26%, r3: 12%, r4: 9%, r5: 6%, r6: 3%, r7: 2%
  swing size             mean 7.8
  was also the last      78%
  own drift              mean -0.1, mean |drift| 7.3
  cards played           mean 2.24
  clue was a lie         68%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: kept its own drift to about 7 while others moved away from zero; lied; usually in the round the game ended.

Seat 4 (champion), solo wins: 560
  round of the swing     r1: 0%, r2: 2%, r3: 15%, r4: 42%, r5: 5%, r6: 5%, r7: 29%
  swing size             mean 21.5
  was also the last      65%
  own drift              mean +0.8, mean |drift| 18.1
  cards played           mean 2.12
  clue was a lie         58%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 18; lied; usually in the round the game ended.

```

```
Self-play champion against the fixed bots
=========================================
Games: 10000    Table: 1:careful_drifter, 2:anchor, 3:champion, 4:champion

How games end
  solo win         66.3%
  bust win         30.1%
  shared win        3.5%
  average length  3.86 rounds; 9% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         47.1%   42.9%    0.7%    3.5%   44.0%
  2: anchor                  30.2%    0.2%   26.5%    3.5%   26.6%
  3: champion                21.3%   15.7%    2.1%    3.5%   18.0%
  4: champion                14.8%    8.3%    2.9%    3.5%   11.4%

Wins by strategy (per seat it occupies)
  careful_drifter            47.1%   42.9%    0.7%
  anchor                     30.2%    0.2%   26.5%
  champion                   18.0%   12.0%    2.5%

Vetoes
  eligible players per round  0.00
  eligible players who veto     0.0%
  rounds with a veto            0.0%
  vetoes per game             0.00
  vetoed players hit twice+     0.0%
  average drift stolen (abs)  0.0
  games a steal decided         0.0%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner came from behind       22.3%
  lead changes per game        1.10
  ending spread (0-1)          0.68

Distributions
  per-player drift  mean -0.4  sd 8.9  5/25/50/75/95%: -14 / -6 / +0 / +4 / +14
  round gap         mean -0.1  sd 17.0  5/25/50/75/95%: -27 / -14 / +0 / +14 / +27

Flags
  ! 'careful_drifter' wins 44% of games outright, at least twice the others' average (21%).
```
