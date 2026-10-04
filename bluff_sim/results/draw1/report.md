# Strategy search

Table: seat 1 careful_drifter, seat 2 anchor, seat 3 adaptive, seat 4 adaptive

Rules: n_players=4, hand_size=5, rounds=7, hand_lo=1, hand_hi=20, hand_copies=4, hand_copies_auto=True, personal_lo=15, personal_hi=30, personal_copies=2, collective_mode=split, collective_split=((70, 82), (98, 110)), collective_continuous=(75, 105), win_threshold=30, track_cap=None, bust_limit=20, min_cards=1, max_cards=3, draw_per_round=1, clue_close=2, clue_much=8, veto_gap=10, veto_target=any, double_veto_at=2, final_multiplier=2, final_doubles_stolen=True, bust_win_requires_near_zero=False, bust_near_zero=5

Win score: solo/bust win 1, shared win 1.0.

## Baseline (adaptive seats on default parameters)

```
Baseline (default adaptive)
===========================
Games: 10000    Table: 1:careful_drifter, 2:anchor, 3:adaptive, 4:adaptive

How games end
  solo win         12.1%
  bust win         87.9%
  shared win        0.0%
  average length  3.22 rounds; 0% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         17.4%   10.4%    7.0%    0.0%   16.4%
  2: anchor                  48.3%    0.5%   47.8%    0.0%   44.0%
  3: adaptive                22.2%    0.7%   21.6%    0.0%   18.9%
  4: adaptive                24.4%    0.6%   23.8%    0.0%   20.7%

Wins by strategy (per seat it occupies)
  careful_drifter            17.4%   10.4%    7.0%
  anchor                     48.3%    0.5%   47.8%
  adaptive                   23.3%    0.6%   22.7%

Vetoes
  eligible players per round  1.13
  eligible players who veto     7.0%
  rounds with a veto            6.7%
  vetoes per game             0.25
  vetoed players hit twice+     9.7%
  average drift stolen (abs)  7.6
  games a steal decided         1.4%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Distributions
  per-player drift  mean -2.2  sd 6.9  5/25/50/75/95%: -15 / -6 / -1 / +1 / +9
  round gap         mean +0.1  sd 17.0  5/25/50/75/95%: -26 / -14 / +0 / +14 / +27

Flags
  ! bust win ends 88% of games.
  ! 'anchor' wins 48% of games outright, at least twice the others' average (20%).
```

## Best response

Win score of the tuned seats: 0.368 (default parameters: 0.232).

What the tuned strategy does:

- Commits to a solo win once its track is 5+ from zero.
- When chasing it, drifts up to 9 a round before round 2, then up to 30.
- Will drift 9 past the point where the tally is projected to bust.
- Anchors at zero when it is closest to zero and someone is 16+ further out.
- Gives 0% weight to closing the group's gap (64% in the final round).
- Lies on 8% of clues, by 3 bands.
- Believes others' clues 100%.
- Vetoes when the steal is worth 6+ to its goal (0+ in the final round); counts blocking a leader at 120% of its size.
- In the final round, goes for the solo win if its track is 11+ from zero, keeping 15 of tally room.

Parameters:

```
{
 "solo_at": 5,
 "anchor_margin": 16,
 "aggr_early": 8.825,
 "aggr_late": 30.0,
 "late_round": 2,
 "room_margin": -8.777,
 "help_weight": 0.0,
 "lie_rate": 0.081,
 "lie_size": 3,
 "veto_threshold": 6.17,
 "deny_weight": 1.198,
 "trust": 1.0,
 "card_cost": 0.446,
 "extreme_cost": 0.14,
 "final_solo_at": 11,
 "final_room_margin": 15.0,
 "final_help_weight": 0.638,
 "final_veto_threshold": 0.0
}
```

Search progress (generation, best, mean): (1, 0.284, 0.216), (2, 0.333, 0.249), (3, 0.328, 0.273), (4, 0.352, 0.302), (5, 0.347, 0.321), (6, 0.363, 0.331), (7, 0.363, 0.343), (8, 0.368, 0.333), (9, 0.359, 0.339), (10, 0.362, 0.340), (11, 0.378, 0.353), (12, 0.362, 0.343), (13, 0.365, 0.336), (14, 0.378, 0.343), (15, 0.351, 0.333), (16, 0.384, 0.366), (17, 0.369, 0.343), (18, 0.369, 0.344), (19, 0.367, 0.342), (20, 0.362, 0.330)

```
Best response
=============
Games: 10000    Table: 1:careful_drifter, 2:anchor, 3:tuned, 4:tuned

How games end
  solo win          8.4%
  bust win         91.6%
  shared win        0.0%
  average length  2.92 rounds; 0% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter          9.7%    5.4%    4.2%    0.0%    8.8%
  2: anchor                  43.7%    0.5%   43.2%    0.0%   34.7%
  3: tuned                   36.6%    1.3%   35.3%    0.0%   28.3%
  4: tuned                   36.6%    1.2%   35.4%    0.0%   28.1%

Wins by strategy (per seat it occupies)
  careful_drifter             9.7%    5.4%    4.2%
  anchor                     43.7%    0.5%   43.2%
  tuned                      36.6%    1.3%   35.3%

Vetoes
  eligible players per round  1.21
  eligible players who veto     6.9%
  rounds with a veto            7.3%
  vetoes per game             0.24
  vetoed players hit twice+     6.2%
  average drift stolen (abs)  10.2
  games a steal decided         1.3%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 2 games (0.0%)

Distributions
  per-player drift  mean -2.2  sd 6.4  5/25/50/75/95%: -14 / -5 / +0 / +1 / +9
  round gap         mean +0.2  sd 16.9  5/25/50/75/95%: -26 / -14 / +0 / +14 / +27

Flags
  ! bust win ends 92% of games.
```

```
Decisive rounds (largest swing toward the winner)

Seat 1 (careful_drifter), bust wins: 424
  round of the swing     r1: 2%, r2: 16%, r3: 35%, r4: 36%, r5: 11%
  swing size             mean 14.1
  was also the last      84%
  own drift              mean -11.0, mean |drift| 11.5
  cards played           mean 1.61
  clue was a lie         0%
  vetoed someone         2% (mean stolen when it did: -6.6)
  was vetoed             4%
  in plain words: kept its own drift to about 11 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 1 (careful_drifter), solo wins: 541
  round of the swing     r1: 40%, r2: 23%, r3: 32%, r4: 4%, r5: 1%
  swing size             mean 12.2
  was also the last      36%
  own drift              mean -10.2, mean |drift| 12.1
  cards played           mean 1.48
  clue was a lie         0%
  vetoed someone         2% (mean stolen when it did: -6.4)
  was vetoed             0%
  in plain words: pushed its own track by about 12; mostly told the truth.

Seat 2 (anchor), bust wins: 4324
  round of the swing     r1: 27%, r2: 35%, r3: 23%, r4: 11%, r5: 2%, r6: 0%
  swing size             mean 2.8
  was also the last      61%
  own drift              mean -0.3, mean |drift| 1.3
  cards played           mean 1.89
  clue was a lie         100%
  vetoed someone         1% (mean stolen when it did: -0.2)
  was vetoed             1%
  in plain words: kept its own drift to about 1 while others moved away from zero; lied; usually in the round the game ended.

Seat 2 (anchor), solo wins: 48
  round of the swing     r2: 15%, r3: 50%, r4: 31%, r5: 4%
  swing size             mean 19.8
  was also the last      79%
  own drift              mean -19.8, mean |drift| 19.8
  cards played           mean 1.46
  clue was a lie         81%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 20; lied; usually in the round the game ended.

Seat 3 (tuned), bust wins: 3527
  round of the swing     r1: 32%, r2: 29%, r3: 24%, r4: 12%, r5: 2%, r6: 0%
  swing size             mean 2.7
  was also the last      63%
  own drift              mean -0.5, mean |drift| 1.1
  cards played           mean 1.89
  clue was a lie         7%
  vetoed someone         1% (mean stolen when it did: -2.8)
  was vetoed             2%
  in plain words: kept its own drift to about 1 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 3 (tuned), solo wins: 130
  round of the swing     r1: 1%, r2: 18%, r3: 51%, r4: 26%, r5: 2%, r6: 1%, r7: 1%
  swing size             mean 24.3
  was also the last      85%
  own drift              mean -17.8, mean |drift| 19.2
  cards played           mean 1.25
  clue was a lie         13%
  vetoed someone         50% (mean stolen when it did: -10.4)
  was vetoed             0%
  in plain words: pushed its own track by about 19; vetoed in 50% of them; mostly told the truth; usually in the round the game ended.

Seat 4 (tuned), bust wins: 3536
  round of the swing     r1: 33%, r2: 29%, r3: 23%, r4: 12%, r5: 3%, r6: 0%
  swing size             mean 2.7
  was also the last      61%
  own drift              mean -0.5, mean |drift| 1.1
  cards played           mean 1.88
  clue was a lie         8%
  vetoed someone         1% (mean stolen when it did: -4.4)
  was vetoed             2%
  in plain words: kept its own drift to about 1 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 4 (tuned), solo wins: 124
  round of the swing     r2: 19%, r3: 46%, r4: 31%, r5: 4%
  swing size             mean 23.9
  was also the last      82%
  own drift              mean -18.1, mean |drift| 18.6
  cards played           mean 1.25
  clue was a lie         9%
  vetoed someone         49% (mean stolen when it did: -11.5)
  was vetoed             2%
  in plain words: pushed its own track by about 19; vetoed in 49% of them; mostly told the truth; usually in the round the game ended.

```

## Self-play

Stable: no challenger beat the starting strategy in its own field, so the best-response strategy is already a self-play equilibrium at this search budget.

Per iteration (champion in own field -> best challenger): 0.399 -> 0.408, 0.411 -> 0.416, 0.392 -> 0.402, 0.390 -> 0.394, 0.394 -> 0.398

Cross-play: row = strategy in one seat, column = strategy in the other seats; value = row's win score. C0 is the best-response strategy.

```
  C0: 0.409
```

What the final champion does:

- Commits to a solo win once its track is 5+ from zero.
- When chasing it, drifts up to 9 a round before round 2, then up to 30.
- Will drift 9 past the point where the tally is projected to bust.
- Anchors at zero when it is closest to zero and someone is 16+ further out.
- Gives 0% weight to closing the group's gap (64% in the final round).
- Lies on 8% of clues, by 3 bands.
- Believes others' clues 100%.
- Vetoes when the steal is worth 6+ to its goal (0+ in the final round); counts blocking a leader at 120% of its size.
- In the final round, goes for the solo win if its track is 11+ from zero, keeping 15 of tally room.

```
Self-play champion, all seats
=============================
Games: 10000    Table: 1:champion, 2:champion, 3:champion, 4:champion

How games end
  solo win          3.6%
  bust win         96.4%
  shared win        0.0%
  average length  2.51 rounds; 0% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: champion                40.0%    0.8%   39.1%    0.0%   24.9%
  2: champion                40.4%    1.0%   39.5%    0.0%   25.2%
  3: champion                39.9%    0.9%   39.0%    0.0%   24.6%
  4: champion                40.7%    0.9%   39.7%    0.0%   25.3%

Wins by strategy (per seat it occupies)
  champion                   40.2%    0.9%   39.3%

Vetoes
  eligible players per round  0.22
  eligible players who veto    22.1%
  rounds with a veto            3.6%
  vetoes per game             0.12
  vetoed players hit twice+    23.9%
  average drift stolen (abs)  14.0
  games a steal decided         0.6%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 8 games (0.1%)

Distributions
  per-player drift  mean -1.8  sd 5.0  5/25/50/75/95%: -14 / -2 / +0 / +0 / +2
  round gap         mean +0.1  sd 16.9  5/25/50/75/95%: -26 / -14 / +0 / +14 / +26

Flags
  ! bust win ends 96% of games.
```

```
Decisive rounds (largest swing toward the winner)

Seat 1 (champion), bust wins: 3913
  round of the swing     r1: 55%, r2: 19%, r3: 14%, r4: 9%, r5: 3%, r6: 0%
  swing size             mean 1.5
  was also the last      74%
  own drift              mean -0.3, mean |drift| 0.7
  cards played           mean 1.97
  clue was a lie         8%
  vetoed someone         1% (mean stolen when it did: -10.5)
  was vetoed             1%
  in plain words: kept its own drift to about 1 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 1 (champion), solo wins: 83
  round of the swing     r1: 1%, r2: 31%, r3: 30%, r4: 27%, r5: 10%, r6: 1%
  swing size             mean 23.7
  was also the last      88%
  own drift              mean -19.9, mean |drift| 21.3
  cards played           mean 1.35
  clue was a lie         10%
  vetoed someone         18% (mean stolen when it did: -13.8)
  was vetoed             0%
  in plain words: pushed its own track by about 21; mostly told the truth; usually in the round the game ended.

Seat 2 (champion), bust wins: 3948
  round of the swing     r1: 55%, r2: 21%, r3: 14%, r4: 7%, r5: 3%, r6: 0%
  swing size             mean 1.5
  was also the last      74%
  own drift              mean -0.2, mean |drift| 0.7
  cards played           mean 1.96
  clue was a lie         8%
  vetoed someone         1% (mean stolen when it did: -9.8)
  was vetoed             1%
  in plain words: kept its own drift to about 1 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 2 (champion), solo wins: 96
  round of the swing     r2: 28%, r3: 45%, r4: 19%, r5: 7%, r6: 1%
  swing size             mean 23.4
  was also the last      77%
  own drift              mean -19.9, mean |drift| 21.3
  cards played           mean 1.28
  clue was a lie         9%
  vetoed someone         14% (mean stolen when it did: -17.6)
  was vetoed             0%
  in plain words: pushed its own track by about 21; mostly told the truth; usually in the round the game ended.

Seat 3 (champion), bust wins: 3900
  round of the swing     r1: 55%, r2: 19%, r3: 13%, r4: 9%, r5: 2%, r6: 0%
  swing size             mean 1.5
  was also the last      72%
  own drift              mean -0.2, mean |drift| 0.7
  cards played           mean 1.98
  clue was a lie         8%
  vetoed someone         1% (mean stolen when it did: -9.3)
  was vetoed             0%
  in plain words: kept its own drift to about 1 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 3 (champion), solo wins: 88
  round of the swing     r2: 30%, r3: 38%, r4: 23%, r5: 8%, r6: 2%
  swing size             mean 22.4
  was also the last      80%
  own drift              mean -17.7, mean |drift| 20.3
  cards played           mean 1.38
  clue was a lie         9%
  vetoed someone         12% (mean stolen when it did: -18.5)
  was vetoed             0%
  in plain words: pushed its own track by about 20; mostly told the truth; usually in the round the game ended.

Seat 4 (champion), bust wins: 3973
  round of the swing     r1: 55%, r2: 21%, r3: 13%, r4: 8%, r5: 2%, r6: 0%
  swing size             mean 1.5
  was also the last      72%
  own drift              mean -0.2, mean |drift| 0.6
  cards played           mean 1.97
  clue was a lie         8%
  vetoed someone         0% (mean stolen when it did: -9.4)
  was vetoed             1%
  in plain words: kept its own drift to about 1 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 4 (champion), solo wins: 95
  round of the swing     r1: 1%, r2: 26%, r3: 36%, r4: 26%, r5: 11%
  swing size             mean 23.2
  was also the last      86%
  own drift              mean -19.9, mean |drift| 20.8
  cards played           mean 1.32
  clue was a lie         7%
  vetoed someone         17% (mean stolen when it did: -15.0)
  was vetoed             0%
  in plain words: pushed its own track by about 21; mostly told the truth; usually in the round the game ended.

```

```
Self-play champion against the fixed bots
=========================================
Games: 10000    Table: 1:careful_drifter, 2:anchor, 3:champion, 4:champion

How games end
  solo win          8.7%
  bust win         91.3%
  shared win        0.0%
  average length  2.94 rounds; 0% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter          9.7%    5.5%    4.2%    0.0%    8.9%
  2: anchor                  43.6%    0.5%   43.1%    0.0%   34.5%
  3: champion                36.9%    1.5%   35.4%    0.0%   28.5%
  4: champion                36.6%    1.3%   35.2%    0.0%   28.1%

Wins by strategy (per seat it occupies)
  careful_drifter             9.7%    5.5%    4.2%
  anchor                     43.6%    0.5%   43.1%
  champion                   36.7%    1.4%   35.3%

Vetoes
  eligible players per round  1.22
  eligible players who veto     7.0%
  rounds with a veto            7.4%
  vetoes per game             0.25
  vetoed players hit twice+     7.9%
  average drift stolen (abs)  10.1
  games a steal decided         1.5%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 2 games (0.0%)

Distributions
  per-player drift  mean -2.2  sd 6.3  5/25/50/75/95%: -14 / -4 / +0 / +1 / +9
  round gap         mean +0.1  sd 16.9  5/25/50/75/95%: -26 / -14 / +0 / +14 / +26

Flags
  ! bust win ends 91% of games.
```
