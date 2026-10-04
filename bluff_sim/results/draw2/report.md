# Strategy search

Table: seat 1 careful_drifter, seat 2 anchor, seat 3 adaptive, seat 4 adaptive

Rules: n_players=4, hand_size=5, rounds=7, hand_lo=1, hand_hi=20, hand_copies=4, hand_copies_auto=True, personal_lo=15, personal_hi=30, personal_copies=2, collective_mode=split, collective_split=((70, 82), (98, 110)), collective_continuous=(75, 105), win_threshold=30, track_cap=None, bust_limit=20, min_cards=1, max_cards=3, draw_per_round=2, clue_close=2, clue_much=8, veto_gap=10, veto_target=any, double_veto_at=2, final_multiplier=2, final_doubles_stolen=True, bust_win_requires_near_zero=False, bust_near_zero=5

Win score: solo/bust win 1, shared win 1.0.

## Baseline (adaptive seats on default parameters)

```
Baseline (default adaptive)
===========================
Games: 10000    Table: 1:careful_drifter, 2:anchor, 3:adaptive, 4:adaptive

How games end
  solo win         43.7%
  bust win         49.6%
  shared win        6.8%
  average length  4.06 rounds; 13% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         47.5%   39.9%    0.9%    6.8%   42.1%
  2: anchor                  47.3%    0.2%   40.4%    6.8%   39.1%
  3: adaptive                15.8%    1.9%    7.2%    6.8%    8.9%
  4: adaptive                17.4%    1.9%    8.7%    6.8%    9.9%

Wins by strategy (per seat it occupies)
  careful_drifter            47.5%   39.9%    0.9%
  anchor                     47.3%    0.2%   40.4%
  adaptive                   16.6%    1.9%    8.0%

Vetoes
  eligible players per round  1.45
  eligible players who veto     8.5%
  rounds with a veto           10.0%
  vetoes per game             0.50
  vetoed players hit twice+    15.8%
  average drift stolen (abs)  5.0
  games a steal decided         1.4%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Distributions
  per-player drift  mean -0.5  sd 5.4  5/25/50/75/95%: -10 / -3 / +0 / +2 / +9
  round gap         mean +0.0  sd 16.9  5/25/50/75/95%: -26 / -14 / +0 / +14 / +26
```

## Best response

Win score of the tuned seats: 0.374 (default parameters: 0.169).

What the tuned strategy does:

- Commits to a solo win once its track is 4+ from zero.
- When chasing it, drifts up to 18 a round before round 6, then up to 0.
- Keeps 14 of room between the projected tally and a bust.
- Anchors at zero when it is closest to zero and someone is 9+ further out.
- Gives 0% weight to closing the group's gap (35% in the final round).
- Lies on 60% of clues, by 2 bands.
- Believes others' clues 35%.
- Vetoes when the steal is worth 4+ to its goal (1+ in the final round); counts blocking a leader at 108% of its size.
- In the final round, goes for the solo win if its track is 18+ from zero, keeping 15 of tally room.

Parameters:

```
{
 "solo_at": 4,
 "anchor_margin": 9,
 "aggr_early": 18.318,
 "aggr_late": 0.0,
 "late_round": 6,
 "room_margin": 14.441,
 "help_weight": 0.0,
 "lie_rate": 0.602,
 "lie_size": 2,
 "veto_threshold": 4.116,
 "deny_weight": 1.075,
 "trust": 0.346,
 "card_cost": 0.288,
 "extreme_cost": 0.1,
 "final_solo_at": 18,
 "final_room_margin": 15.0,
 "final_help_weight": 0.354,
 "final_veto_threshold": 0.678
}
```

Search progress (generation, best, mean): (1, 0.254, 0.190), (2, 0.331, 0.225), (3, 0.350, 0.249), (4, 0.352, 0.269), (5, 0.348, 0.293), (6, 0.353, 0.306), (7, 0.370, 0.324), (8, 0.371, 0.335), (9, 0.370, 0.331), (10, 0.367, 0.324), (11, 0.370, 0.318), (12, 0.378, 0.320), (13, 0.365, 0.326), (14, 0.370, 0.325), (15, 0.388, 0.326), (16, 0.381, 0.323), (17, 0.381, 0.329), (18, 0.372, 0.299), (19, 0.389, 0.324), (20, 0.382, 0.321)

```
Best response
=============
Games: 10000    Table: 1:careful_drifter, 2:anchor, 3:tuned, 4:tuned

How games end
  solo win         21.3%
  bust win         75.1%
  shared win        3.5%
  average length  3.37 rounds; 6% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         22.0%   17.8%    0.7%    3.5%   18.9%
  2: anchor                  53.4%    0.2%   49.6%    3.5%   36.2%
  3: tuned                   37.2%    2.0%   31.7%    3.5%   22.5%
  4: tuned                   37.0%    1.6%   31.9%    3.5%   22.3%

Wins by strategy (per seat it occupies)
  careful_drifter            22.0%   17.8%    0.7%
  anchor                     53.4%    0.2%   49.6%
  tuned                      37.1%    1.8%   31.8%

Vetoes
  eligible players per round  1.43
  eligible players who veto     7.3%
  rounds with a veto            9.2%
  vetoes per game             0.35
  vetoed players hit twice+     6.9%
  average drift stolen (abs)  5.8
  games a steal decided         1.8%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Distributions
  per-player drift  mean -0.6  sd 4.9  5/25/50/75/95%: -10 / -1 / +0 / +1 / +9
  round gap         mean +0.1  sd 16.9  5/25/50/75/95%: -26 / -14 / +0 / +14 / +26

Flags
  ! bust win ends 75% of games.
```

```
Decisive rounds (largest swing toward the winner)

Seat 1 (careful_drifter), bust wins: 66
  round of the swing     r1: 6%, r2: 24%, r3: 35%, r4: 12%, r5: 9%, r6: 12%, r7: 2%
  swing size             mean 9.6
  was also the last      70%
  own drift              mean -8.8, mean |drift| 9.2
  cards played           mean 2.56
  clue was a lie         0%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: kept its own drift to about 9 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 1 (careful_drifter), solo wins: 1776
  round of the swing     r1: 51%, r2: 22%, r3: 17%, r4: 4%, r5: 1%, r6: 2%, r7: 2%
  swing size             mean 11.4
  was also the last      18%
  own drift              mean -4.1, mean |drift| 11.1
  cards played           mean 1.74
  clue was a lie         0%
  vetoed someone         1% (mean stolen when it did: -1.9)
  was vetoed             0%
  in plain words: pushed its own track by about 11; mostly told the truth.

Seat 2 (anchor), bust wins: 4964
  round of the swing     r1: 32%, r2: 38%, r3: 18%, r4: 7%, r5: 3%, r6: 1%, r7: 0%
  swing size             mean 1.5
  was also the last      44%
  own drift              mean +0.1, mean |drift| 0.9
  cards played           mean 2.04
  clue was a lie         99%
  vetoed someone         1% (mean stolen when it did: +2.6)
  was vetoed             1%
  in plain words: kept its own drift to about 1 while others moved away from zero; lied.

Seat 2 (anchor), solo wins: 24
  round of the swing     r2: 4%, r3: 8%, r4: 33%, r5: 17%, r7: 38%
  swing size             mean 22.8
  was also the last      71%
  own drift              mean -16.3, mean |drift| 16.3
  cards played           mean 2.33
  clue was a lie         71%
  vetoed someone         21% (mean stolen when it did: -2.6)
  was vetoed             0%
  in plain words: pushed its own track by about 16; lied; usually in the round the game ended.

Seat 3 (tuned), bust wins: 3166
  round of the swing     r1: 49%, r2: 27%, r3: 14%, r4: 6%, r5: 3%, r6: 1%, r7: 0%
  swing size             mean 1.1
  was also the last      42%
  own drift              mean +0.0, mean |drift| 0.4
  cards played           mean 2.04
  clue was a lie         61%
  vetoed someone         1% (mean stolen when it did: +0.3)
  was vetoed             0%
  in plain words: kept its own drift to about 0 while others moved away from zero; lied.

Seat 3 (tuned), solo wins: 198
  round of the swing     r2: 10%, r3: 35%, r4: 25%, r5: 11%, r6: 1%, r7: 19%
  swing size             mean 21.2
  was also the last      61%
  own drift              mean -9.7, mean |drift| 15.4
  cards played           mean 1.77
  clue was a lie         55%
  vetoed someone         49% (mean stolen when it did: -4.5)
  was vetoed             0%
  in plain words: pushed its own track by about 15; vetoed in 49% of them; lied; usually in the round the game ended.

Seat 4 (tuned), bust wins: 3188
  round of the swing     r1: 49%, r2: 27%, r3: 15%, r4: 6%, r5: 3%, r6: 1%, r7: 0%
  swing size             mean 1.0
  was also the last      42%
  own drift              mean +0.0, mean |drift| 0.3
  cards played           mean 2.02
  clue was a lie         59%
  vetoed someone         1% (mean stolen when it did: +0.4)
  was vetoed             0%
  in plain words: kept its own drift to about 0 while others moved away from zero; lied.

Seat 4 (tuned), solo wins: 158
  round of the swing     r2: 12%, r3: 25%, r4: 38%, r5: 13%, r6: 1%, r7: 11%
  swing size             mean 22.0
  was also the last      59%
  own drift              mean -10.8, mean |drift| 16.4
  cards played           mean 1.73
  clue was a lie         55%
  vetoed someone         58% (mean stolen when it did: -3.8)
  was vetoed             0%
  in plain words: pushed its own track by about 16; vetoed in 58% of them; lied.

```

## Self-play

Cycling: earlier champions beat later ones on their own ground (C0 beats C2's field, C0 beats C3's field, C1 beats C3's field, C0 beats C4's field). No single strategy dominates; expect the meta to rotate.

Per iteration (champion in own field -> best challenger): 0.501 -> 0.564 (new), 0.341 -> 0.616 (new), 0.466 -> 0.724 (new), 0.276 -> 0.826 (new), 0.507 -> 0.717 (new)

Cross-play: row = strategy in one seat, column = strategy in the other seats; value = row's win score. C0 is the best-response strategy.

```
  C0: 0.499  0.637  0.541  0.726  0.706  0.569
  C1: 0.575  0.332  0.671  0.343  0.645  0.319
  C2: 0.421  0.613  0.454  0.718  0.658  0.537
  C3: 0.533  0.237  0.711  0.279  0.512  0.357
  C4: 0.206  0.651  0.190  0.823  0.497  0.528
  C5: 0.554  0.376  0.654  0.350  0.712  0.308
```

What the final champion does:

- Commits to a solo win once its track is 21+ from zero.
- When chasing it, drifts up to 20 a round before round 5, then up to 8.
- Keeps 5 of room between the projected tally and a bust.
- Anchors at zero when it is closest to zero and someone is 2+ further out.
- Gives 88% weight to closing the group's gap (100% in the final round).
- Lies on 47% of clues, by 1 band.
- Believes others' clues 6%.
- Vetoes when the steal is worth 20+ to its goal (7+ in the final round); counts blocking a leader at 140% of its size.
- Prefers playing many cards.
- In the final round, goes for the solo win if its track is 10+ from zero, keeping 7 of tally room.

```
Self-play champion, all seats
=============================
Games: 10000    Table: 1:champion, 2:champion, 3:champion, 4:champion

How games end
  solo win         26.9%
  bust win         66.6%
  shared win        6.5%
  average length  3.79 rounds; 17% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: champion                31.8%    7.5%   17.8%    6.5%   25.6%
  2: champion                31.1%    6.6%   18.0%    6.5%   24.9%
  3: champion                29.8%    7.5%   15.8%    6.5%   23.3%
  4: champion                32.7%    5.4%   20.8%    6.5%   26.3%

Wins by strategy (per seat it occupies)
  champion                   31.4%    6.8%   18.1%

Vetoes
  eligible players per round  1.01
  eligible players who veto     3.3%
  rounds with a veto            2.4%
  vetoes per game             0.13
  vetoed players hit twice+    23.5%
  average drift stolen (abs)  15.4
  games a steal decided         1.6%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 8 games (0.1%)

Distributions
  per-player drift  mean -0.3  sd 9.9  5/25/50/75/95%: -16 / -7 / -1 / +6 / +17
  round gap         mean +0.0  sd 16.9  5/25/50/75/95%: -26 / -14 / +0 / +14 / +26
```

```
Decisive rounds (largest swing toward the winner)

Seat 1 (champion), bust wins: 1777
  round of the swing     r1: 20%, r2: 36%, r3: 18%, r4: 12%, r5: 8%, r6: 3%, r7: 3%
  swing size             mean 10.8
  was also the last      82%
  own drift              mean -0.6, mean |drift| 8.4
  cards played           mean 2.29
  clue was a lie         47%
  vetoed someone         0% (mean stolen when it did: +18.0)
  was vetoed             0%
  in plain words: kept its own drift to about 8 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 1 (champion), solo wins: 754
  round of the swing     r1: 50%, r2: 2%, r3: 3%, r4: 10%, r5: 18%, r6: 1%, r7: 16%
  swing size             mean 22.5
  was also the last      40%
  own drift              mean +0.2, mean |drift| 19.2
  cards played           mean 2.07
  clue was a lie         42%
  vetoed someone         6% (mean stolen when it did: -10.7)
  was vetoed             0%
  in plain words: pushed its own track by about 19; mostly told the truth.

Seat 2 (champion), bust wins: 1799
  round of the swing     r1: 20%, r2: 28%, r3: 27%, r4: 11%, r5: 7%, r6: 4%, r7: 4%
  swing size             mean 10.5
  was also the last      78%
  own drift              mean -1.7, mean |drift| 8.9
  cards played           mean 2.27
  clue was a lie         47%
  vetoed someone         0% (mean stolen when it did: -5.2)
  was vetoed             1%
  in plain words: kept its own drift to about 9 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 2 (champion), solo wins: 662
  round of the swing     r1: 11%, r2: 40%, r3: 3%, r4: 4%, r5: 9%, r6: 19%, r7: 14%
  swing size             mean 20.7
  was also the last      55%
  own drift              mean +2.0, mean |drift| 18.5
  cards played           mean 2.16
  clue was a lie         43%
  vetoed someone         6% (mean stolen when it did: +2.9)
  was vetoed             0%
  in plain words: pushed its own track by about 19; mostly told the truth.

Seat 3 (champion), bust wins: 1576
  round of the swing     r1: 28%, r2: 24%, r3: 19%, r4: 17%, r5: 7%, r6: 3%, r7: 2%
  swing size             mean 8.3
  was also the last      78%
  own drift              mean -1.4, mean |drift| 8.3
  cards played           mean 2.35
  clue was a lie         48%
  vetoed someone         1% (mean stolen when it did: +0.1)
  was vetoed             0%
  in plain words: kept its own drift to about 8 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 3 (champion), solo wins: 750
  round of the swing     r1: 1%, r2: 7%, r3: 38%, r4: 2%, r5: 2%, r6: 6%, r7: 44%
  swing size             mean 26.7
  was also the last      70%
  own drift              mean +1.9, mean |drift| 19.6
  cards played           mean 2.09
  clue was a lie         37%
  vetoed someone         11% (mean stolen when it did: -2.9)
  was vetoed             0%
  in plain words: pushed its own track by about 20; mostly told the truth; usually in the round the game ended.

Seat 4 (champion), bust wins: 2075
  round of the swing     r1: 41%, r2: 28%, r3: 11%, r4: 9%, r5: 7%, r6: 3%, r7: 2%
  swing size             mean 7.9
  was also the last      79%
  own drift              mean +0.1, mean |drift| 7.3
  cards played           mean 2.23
  clue was a lie         48%
  vetoed someone         0% (mean stolen when it did: -1.4)
  was vetoed             0%
  in plain words: kept its own drift to about 7 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 4 (champion), solo wins: 543
  round of the swing     r1: 1%, r2: 2%, r3: 14%, r4: 41%, r5: 3%, r6: 4%, r7: 36%
  swing size             mean 25.1
  was also the last      69%
  own drift              mean -0.3, mean |drift| 18.3
  cards played           mean 2.07
  clue was a lie         43%
  vetoed someone         14% (mean stolen when it did: -4.6)
  was vetoed             1%
  in plain words: pushed its own track by about 18; mostly told the truth; usually in the round the game ended.

```

```
Self-play champion against the fixed bots
=========================================
Games: 10000    Table: 1:careful_drifter, 2:anchor, 3:champion, 4:champion

How games end
  solo win         62.2%
  bust win         34.9%
  shared win        2.8%
  average length  3.74 rounds; 8% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         43.9%   40.5%    0.6%    2.8%   41.4%
  2: anchor                  34.4%    0.2%   31.4%    2.8%   31.2%
  3: champion                20.0%   14.8%    2.4%    2.8%   17.1%
  4: champion                13.1%    7.4%    2.9%    2.8%   10.3%

Wins by strategy (per seat it occupies)
  careful_drifter            43.9%   40.5%    0.6%
  anchor                     34.4%    0.2%   31.4%
  champion                   16.6%   11.1%    2.6%

Vetoes
  eligible players per round  1.28
  eligible players who veto     5.4%
  rounds with a veto            6.4%
  vetoes per game             0.26
  vetoed players hit twice+     4.9%
  average drift stolen (abs)  9.5
  games a steal decided         2.3%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 2 games (0.0%)

Distributions
  per-player drift  mean -0.4  sd 9.3  5/25/50/75/95%: -15 / -7 / +0 / +5 / +16
  round gap         mean -0.1  sd 17.0  5/25/50/75/95%: -27 / -14 / +0 / +14 / +27
```
