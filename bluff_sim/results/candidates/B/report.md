# Strategy search

Table: seat 1 careful_drifter, seat 2 anchor, seat 3 adaptive, seat 4 adaptive

Rules: n_players=4, hand_size=5, rounds=5, hand_lo=1, hand_hi=18, hand_copies=4, hand_copies_auto=True, personal_lo=10, personal_hi=20, personal_copies=2, personal_copies_auto=True, collective_mode=continuous, collective_split=((70, 82), (98, 110)), collective_continuous=(45, 75), win_threshold=25, track_cap=None, bust_limit=18, min_cards=1, max_cards=3, draw_per_round=1, clue_close=2, clue_much=8, vetoes_enabled=True, veto_gap=8, veto_target=any, double_veto_at=2, veto_mode=take, veto_cost=0, final_multiplier=2, final_doubles_stolen=True, bust_win_requires_near_zero=False, bust_near_zero=5

Win score: solo/bust win 1, shared win 1.0.

## Baseline (adaptive seats on default parameters)

```
Baseline (default adaptive)
===========================
Games: 6000    Table: 1:careful_drifter, 2:anchor, 3:adaptive, 4:adaptive

How games end
  solo win         32.3%
  bust win         39.9%
  shared win       27.9%
  average length  4.08 rounds; 50% reach round 5

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         58.0%   28.5%    1.6%   27.9%   36.8%
  2: anchor                  56.0%    0.9%   27.3%   27.9%   32.1%
  3: adaptive                38.1%    1.5%    8.8%   27.9%   15.2%
  4: adaptive                39.1%    1.6%    9.7%   27.9%   15.9%

Wins by strategy (per seat it occupies)
  careful_drifter            58.0%   28.5%    1.6%
  anchor                     56.0%    0.9%   27.3%
  adaptive                   38.6%    1.5%    9.2%

Vetoes
  eligible players per round  1.56
  eligible players who veto     5.5%
  rounds with a veto            7.3%
  vetoes per game             0.35
  vetoed players hit twice+    12.8%
  average drift stolen (abs)  5.7
  games a steal decided         2.4%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner behind at halfway      16.8%
  winner behind before last    22.9%
  won outright in final round   22.6%
  lead changes per game        0.48
  ending spread (0-1)          0.99

Distributions
  per-player drift  mean -0.5  sd 4.5  5/25/50/75/95%: -9 / -2 / +0 / +2 / +8
  round gap         mean -0.0  sd 10.7  5/25/50/75/95%: -17 / -8 / +0 / +8 / +17
```

## Best response

Win score of the tuned seats: 0.507 (default parameters: 0.389).

What the tuned strategy does:

- Almost never commits to a solo win before the final round.
- When chasing it, drifts up to 13 a round before round 3, then up to 9.
- Keeps 15 of room between the projected tally and a bust.
- Anchors at zero when it is closest to zero and someone is 11+ further out.
- Gives 49% weight to closing the group's gap (80% in the final round).
- Lies on 95% of clues, by 2 bands.
- Believes others' clues 25%.
- Vetoes when the steal is worth 0+ to its goal (7+ in the final round); counts blocking a leader at 142% of its size.
- Prefers playing many cards.
- Also blocks any player it expects to end the round within 8 of the solo threshold, leader or not.
- In the final round, goes for the solo win if its track is 0+ from zero, keeping -1 of tally room.

Parameters:

```
{
 "solo_at": 30,
 "anchor_margin": 11,
 "aggr_early": 12.776,
 "aggr_late": 8.598,
 "late_round": 3,
 "room_margin": 15.0,
 "help_weight": 0.492,
 "lie_rate": 0.947,
 "lie_size": 2,
 "veto_threshold": 0.0,
 "deny_weight": 1.419,
 "trust": 0.254,
 "card_cost": -1.138,
 "extreme_cost": 1.489,
 "final_solo_at": 0,
 "final_room_margin": -0.872,
 "final_help_weight": 0.797,
 "final_veto_threshold": 6.524,
 "danger_margin": 8
}
```

Search progress (generation, best, mean): (1, 0.422, 0.348), (2, 0.422, 0.369), (3, 0.417, 0.378), (4, 0.398, 0.376), (5, 0.453, 0.405), (6, 0.470, 0.415), (7, 0.480, 0.450), (8, 0.512, 0.453), (9, 0.516, 0.456), (10, 0.526, 0.486)

```
Best response
=============
Games: 6000    Table: 1:careful_drifter, 2:anchor, 3:tuned, 4:tuned

How games end
  solo win         37.9%
  bust win         28.1%
  shared win       34.0%
  average length  4.55 rounds; 76% reach round 5

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         47.2%   11.2%    2.0%   34.0%   21.3%
  2: anchor                  57.4%    1.7%   21.8%   34.0%   30.7%
  3: tuned                   50.9%   13.3%    3.6%   34.0%   24.6%
  4: tuned                   49.5%   12.1%    3.4%   34.0%   23.3%

Wins by strategy (per seat it occupies)
  careful_drifter            47.2%   11.2%    2.0%
  anchor                     57.4%    1.7%   21.8%
  tuned                      50.2%   12.7%    3.5%

Vetoes
  eligible players per round  1.26
  eligible players who veto    44.2%
  rounds with a veto           38.6%
  vetoes per game             2.52
  vetoed players hit twice+    22.1%
  average drift stolen (abs)  6.7
  games a steal decided        11.3%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 5 games (0.1%)

Tension
  winner behind at halfway      46.2%
  winner behind before last    49.2%
  won outright in final round   42.5%
  lead changes per game        1.54
  ending spread (0-1)          0.99

Distributions
  per-player drift  mean -0.4  sd 5.7  5/25/50/75/95%: -10 / -4 / +0 / +3 / +9
  round gap         mean -0.0  sd 10.7  5/25/50/75/95%: -17 / -8 / +0 / +8 / +17
```

```
Decisive rounds (largest swing toward the winner)

Seat 1 (careful_drifter), bust wins: 118
  round of the swing     r1: 1%, r2: 8%, r3: 9%, r4: 26%, r5: 55%
  swing size             mean 12.1
  was also the last      86%
  own drift              mean -4.4, mean |drift| 6.6
  cards played           mean 1.27
  clue was a lie         0%
  vetoed someone         3% (mean stolen when it did: -0.8)
  was vetoed             5%
  in plain words: kept its own drift to about 7 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 1 (careful_drifter), solo wins: 674
  round of the swing     r1: 11%, r2: 9%, r3: 6%, r4: 25%, r5: 50%
  swing size             mean 15.5
  was also the last      73%
  own drift              mean -3.1, mean |drift| 10.1
  cards played           mean 1.46
  clue was a lie         0%
  vetoed someone         10% (mean stolen when it did: +2.3)
  was vetoed             1%
  in plain words: pushed its own track by about 10; mostly told the truth; usually in the round the game ended.

Seat 2 (anchor), bust wins: 1306
  round of the swing     r1: 31%, r2: 25%, r3: 17%, r4: 14%, r5: 13%
  swing size             mean 5.5
  was also the last      43%
  own drift              mean -0.3, mean |drift| 1.2
  cards played           mean 1.74
  clue was a lie         99%
  vetoed someone         0% (mean stolen when it did: +11.2)
  was vetoed             9%
  in plain words: kept its own drift to about 1 while others moved away from zero; lied.

Seat 2 (anchor), solo wins: 99
  round of the swing     r3: 2%, r4: 3%, r5: 95%
  swing size             mean 25.7
  was also the last      98%
  own drift              mean -10.8, mean |drift| 11.5
  cards played           mean 1.16
  clue was a lie         90%
  vetoed someone         28% (mean stolen when it did: +5.8)
  was vetoed             4%
  in plain words: pushed its own track by about 12; vetoed in 28% of them; lied; usually in the round the game ended.

Seat 3 (tuned), bust wins: 215
  round of the swing     r1: 4%, r2: 29%, r3: 14%, r4: 23%, r5: 30%
  swing size             mean 7.6
  was also the last      81%
  own drift              mean -1.5, mean |drift| 5.8
  cards played           mean 1.78
  clue was a lie         95%
  vetoed someone         15% (mean stolen when it did: +1.0)
  was vetoed             7%
  in plain words: kept its own drift to about 6 while others moved away from zero; lied; usually in the round the game ended.

Seat 3 (tuned), solo wins: 799
  round of the swing     r2: 2%, r3: 8%, r4: 4%, r5: 86%
  swing size             mean 27.0
  was also the last      92%
  own drift              mean +3.5, mean |drift| 11.8
  cards played           mean 1.75
  clue was a lie         93%
  vetoed someone         53% (mean stolen when it did: -1.6)
  was vetoed             4%
  in plain words: pushed its own track by about 12; vetoed in 53% of them; lied; usually in the round the game ended.

Seat 4 (tuned), bust wins: 205
  round of the swing     r1: 1%, r2: 29%, r3: 15%, r4: 33%, r5: 22%
  swing size             mean 7.6
  was also the last      74%
  own drift              mean +0.9, mean |drift| 5.4
  cards played           mean 1.80
  clue was a lie         95%
  vetoed someone         25% (mean stolen when it did: -2.5)
  was vetoed             6%
  in plain words: kept its own drift to about 5 while others moved away from zero; vetoed in 25% of them; lied; usually in the round the game ended.

Seat 4 (tuned), solo wins: 726
  round of the swing     r1: 0%, r2: 1%, r3: 6%, r4: 7%, r5: 86%
  swing size             mean 28.7
  was also the last      92%
  own drift              mean +2.4, mean |drift| 11.0
  cards played           mean 1.70
  clue was a lie         96%
  vetoed someone         59% (mean stolen when it did: +1.2)
  was vetoed             5%
  in plain words: pushed its own track by about 11; vetoed in 59% of them; lied; usually in the round the game ended.

```

```
Sensitivity (each parameter moved to its bounds; base score 0.512; differences under ~0.022 are noise)

  parameter                tuned          at low         at high  matters?
  trust                    0.254      0 -0.031       1 -0.159  yes
  final_help_weight        0.797      0 -0.103       1 -0.006  yes
  help_weight              0.492      0 -0.096       1 -0.094  yes
  solo_at                     30      0 -0.091      30 +0.000  yes
  veto_threshold             0.0      0 +0.000      20 -0.076  yes
  deny_weight              1.419      0 -0.069     1.5 +0.001  yes
  lie_rate                 0.947      0 -0.020       1 +0.001  no
  danger_margin                8      0 -0.006      30 -0.019  no
  extreme_cost             1.489      0 -0.005       4 -0.013  no
  card_cost               -1.138     -3 -0.012       3 -0.009  no
  final_solo_at                0      0 +0.000      30 +0.009  no
  lie_size                     2      1 -0.008       3 +0.002  no
  final_veto_threshold     6.524      0 +0.007      20 -0.008  no
  anchor_margin               11      2 +0.003      30 +0.002  no
  final_room_margin       -0.872    -10 +0.002      15 +0.002  no
  aggr_early              12.776      0 +0.000      20 +0.000  no
  aggr_late                8.598      0 +0.000      30 +0.000  no
  late_round                   3      1 +0.000       7 +0.000  no
  room_margin               15.0    -10 +0.000      15 +0.000  no
```

## Self-play

Cycling: earlier champions beat later ones on their own ground (C0 beats C2's field, C0 beats C3's field, C1 beats C3's field). No single strategy dominates; expect the meta to rotate.

Per iteration (champion in own field -> best challenger): 0.553 -> 0.615 (new), 0.594 -> 0.614 (new), 0.551 -> 0.665 (new)

Cross-play: row = strategy in one seat, column = strategy in the other seats; value = row's win score. C0 is the best-response strategy.

```
  C0: 0.542  0.558  0.659  0.589
  C1: 0.636  0.583  0.493  0.607
  C2: 0.622  0.625  0.583  0.569
  C3: 0.438  0.574  0.681  0.511
```

What the final champion does:

- Commits to a solo win once its track is 25+ from zero.
- When chasing it, drifts up to 7 a round before round 1, then up to 21.
- Will drift 7 past the point where the tally is projected to bust.
- Rarely plays as an anchor.
- Gives 100% weight to closing the group's gap (100% in the final round).
- Lies on 12% of clues, by 1 band.
- Believes others' clues 39%.
- Vetoes when the steal is worth 7+ to its goal (3+ in the final round); counts blocking a leader at 29% of its size.
- Prefers playing many cards.
- Hoards very high and very low cards.
- Also blocks any player it expects to end the round within 23 of the solo threshold, leader or not.
- In the final round, goes for the solo win if its track is 9+ from zero, keeping -8 of tally room.

```
Self-play champion, all seats
=============================
Games: 6000    Table: 1:champion, 2:champion, 3:champion, 4:champion

How games end
  solo win         43.7%
  bust win         18.8%
  shared win       37.6%
  average length  4.49 rounds; 75% reach round 5

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: champion                58.2%   15.6%    5.1%   37.6%   29.5%
  2: champion                54.4%   11.5%    5.4%   37.6%   25.7%
  3: champion                52.0%    9.8%    4.7%   37.6%   23.3%
  4: champion                50.2%    7.3%    5.3%   37.6%   21.5%

Wins by strategy (per seat it occupies)
  champion                   53.7%   11.0%    5.1%

Vetoes
  eligible players per round  1.06
  eligible players who veto    10.6%
  rounds with a veto            8.7%
  vetoes per game             0.50
  vetoed players hit twice+     9.0%
  average drift stolen (abs)  10.7
  games a steal decided         5.1%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 1 games (0.0%)

Tension
  winner behind at halfway      49.9%
  winner behind before last    63.6%
  won outright in final round   37.8%
  lead changes per game        2.09
  ending spread (0-1)          0.95

Distributions
  per-player drift  mean -0.1  sd 7.3  5/25/50/75/95%: -11 / -4 / -1 / +3 / +14
  round gap         mean +0.1  sd 10.7  5/25/50/75/95%: -17 / -8 / +0 / +8 / +17
```

```
Decisive rounds (largest swing toward the winner)

Seat 1 (champion), bust wins: 306
  round of the swing     r1: 19%, r2: 30%, r3: 23%, r4: 15%, r5: 13%
  swing size             mean 7.7
  was also the last      77%
  own drift              mean -1.1, mean |drift| 5.4
  cards played           mean 1.83
  clue was a lie         11%
  vetoed someone         1% (mean stolen when it did: -1.8)
  was vetoed             2%
  in plain words: kept its own drift to about 5 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 1 (champion), solo wins: 934
  round of the swing     r1: 16%, r2: 0%, r3: 1%, r4: 5%, r5: 77%
  swing size             mean 24.8
  was also the last      84%
  own drift              mean +0.7, mean |drift| 14.6
  cards played           mean 1.69
  clue was a lie         11%
  vetoed someone         16% (mean stolen when it did: -1.8)
  was vetoed             1%
  in plain words: pushed its own track by about 15; mostly told the truth; usually in the round the game ended.

Seat 2 (champion), bust wins: 322
  round of the swing     r1: 17%, r2: 21%, r3: 31%, r4: 14%, r5: 16%
  swing size             mean 8.5
  was also the last      81%
  own drift              mean -3.0, mean |drift| 5.8
  cards played           mean 1.79
  clue was a lie         14%
  vetoed someone         3% (mean stolen when it did: +0.4)
  was vetoed             2%
  in plain words: kept its own drift to about 6 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 2 (champion), solo wins: 688
  round of the swing     r1: 2%, r2: 27%, r3: 2%, r4: 5%, r5: 64%
  swing size             mean 24.5
  was also the last      81%
  own drift              mean +5.3, mean |drift| 15.8
  cards played           mean 1.87
  clue was a lie         11%
  vetoed someone         18% (mean stolen when it did: -0.4)
  was vetoed             2%
  in plain words: pushed its own track by about 16; mostly told the truth; usually in the round the game ended.

Seat 3 (champion), bust wins: 284
  round of the swing     r1: 19%, r2: 21%, r3: 18%, r4: 24%, r5: 18%
  swing size             mean 8.2
  was also the last      79%
  own drift              mean -1.9, mean |drift| 6.1
  cards played           mean 1.85
  clue was a lie         18%
  vetoed someone         2% (mean stolen when it did: +5.3)
  was vetoed             2%
  in plain words: kept its own drift to about 6 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 3 (champion), solo wins: 585
  round of the swing     r1: 0%, r2: 3%, r3: 25%, r4: 4%, r5: 68%
  swing size             mean 24.6
  was also the last      85%
  own drift              mean +4.2, mean |drift| 15.0
  cards played           mean 1.79
  clue was a lie         13%
  vetoed someone         18% (mean stolen when it did: +1.8)
  was vetoed             2%
  in plain words: pushed its own track by about 15; mostly told the truth; usually in the round the game ended.

Seat 4 (champion), bust wins: 317
  round of the swing     r1: 26%, r2: 22%, r3: 21%, r4: 12%, r5: 20%
  swing size             mean 7.7
  was also the last      74%
  own drift              mean +0.3, mean |drift| 5.6
  cards played           mean 1.74
  clue was a lie         17%
  vetoed someone         3% (mean stolen when it did: -0.6)
  was vetoed             5%
  in plain words: kept its own drift to about 6 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 4 (champion), solo wins: 440
  round of the swing     r1: 1%, r2: 1%, r3: 6%, r4: 20%, r5: 73%
  swing size             mean 24.4
  was also the last      91%
  own drift              mean +4.2, mean |drift| 14.2
  cards played           mean 1.82
  clue was a lie         12%
  vetoed someone         23% (mean stolen when it did: +1.5)
  was vetoed             4%
  in plain words: pushed its own track by about 14; mostly told the truth; usually in the round the game ended.

```

```
Self-play champion against the fixed bots
=========================================
Games: 6000    Table: 1:careful_drifter, 2:anchor, 3:champion, 4:champion

How games end
  solo win         55.3%
  bust win         26.4%
  shared win       18.3%
  average length  3.89 rounds; 41% reach round 5

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         54.6%   35.5%    0.9%   18.3%   40.6%
  2: anchor                  40.9%    0.6%   22.1%   18.3%   26.0%
  3: champion                33.3%   11.9%    3.1%   18.3%   18.7%
  4: champion                29.2%    7.7%    3.2%   18.3%   14.7%

Wins by strategy (per seat it occupies)
  careful_drifter            54.6%   35.5%    0.9%
  anchor                     40.9%    0.6%   22.1%
  champion                   31.2%    9.8%    3.1%

Vetoes
  eligible players per round  1.37
  eligible players who veto     9.9%
  rounds with a veto           11.6%
  vetoes per game             0.53
  vetoed players hit twice+     5.1%
  average drift stolen (abs)  8.8
  games a steal decided         4.8%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner behind at halfway      21.9%
  winner behind before last    30.2%
  won outright in final round   22.4%
  lead changes per game        1.05
  ending spread (0-1)          0.90

Distributions
  per-player drift  mean -0.3  sd 6.8  5/25/50/75/95%: -11 / -5 / +0 / +3 / +11
  round gap         mean -0.0  sd 10.7  5/25/50/75/95%: -17 / -8 / +0 / +8 / +17

Flags
  ! 'careful_drifter' wins 36% of games outright, at least twice the others' average (18%).
```
