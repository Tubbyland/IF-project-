# Strategy search

Table: seat 1 careful_drifter, seat 2 anchor, seat 3 adaptive, seat 4 adaptive

Rules: n_players=4, hand_size=5, rounds=5, hand_lo=1, hand_hi=15, hand_copies=4, hand_copies_auto=True, personal_lo=10, personal_hi=20, personal_copies=2, personal_copies_auto=True, collective_mode=continuous, collective_split=((70, 82), (98, 110)), collective_continuous=(45, 75), win_threshold=25, track_cap=None, bust_limit=14, min_cards=1, max_cards=3, draw_per_round=2, clue_close=2, clue_much=8, vetoes_enabled=True, veto_gap=8, veto_target=any, double_veto_at=2, veto_mode=take, veto_cost=0, final_multiplier=2, final_doubles_stolen=True, bust_win_requires_near_zero=False, bust_near_zero=5

Win score: solo/bust win 1, shared win 1.0.

## Baseline (adaptive seats on default parameters)

```
Baseline (default adaptive)
===========================
Games: 6000    Table: 1:careful_drifter, 2:anchor, 3:adaptive, 4:adaptive

How games end
  solo win         33.3%
  bust win         38.2%
  shared win       28.4%
  average length  3.83 rounds; 45% reach round 5

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         61.0%   32.2%    0.3%   28.4%   39.5%
  2: anchor                  62.5%    0.0%   34.0%   28.4%   36.9%
  3: adaptive                35.4%    0.4%    6.5%   28.4%   11.4%
  4: adaptive                36.4%    0.8%    7.2%   28.4%   12.1%

Wins by strategy (per seat it occupies)
  careful_drifter            61.0%   32.2%    0.3%
  anchor                     62.5%    0.0%   34.0%
  adaptive                   35.9%    0.6%    6.9%

Vetoes
  eligible players per round  1.56
  eligible players who veto     3.7%
  rounds with a veto            4.8%
  vetoes per game             0.22
  vetoed players hit twice+    17.0%
  average drift stolen (abs)  4.8
  games a steal decided         2.4%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner behind at halfway       3.5%
  winner behind before last    10.5%
  won outright in final round   16.4%
  lead changes per game        0.23
  ending spread (0-1)          0.99

Distributions
  per-player drift  mean -0.1  sd 3.8  5/25/50/75/95%: -8 / -2 / +0 / +1 / +8
  round gap         mean +0.0  sd 10.7  5/25/50/75/95%: -17 / -8 / +0 / +8 / +18
```

## Best response

Win score of the tuned seats: 0.625 (default parameters: 0.350).

What the tuned strategy does:

- Almost never commits to a solo win before the final round.
- When chasing it, drifts up to 2 a round before round 3, then up to 0.
- Will drift 3 past the point where the tally is projected to bust.
- Anchors at zero when it is closest to zero and someone is 18+ further out.
- Gives 37% weight to closing the group's gap (54% in the final round).
- Lies on 68% of clues, by 2 bands.
- Believes others' clues 19%.
- Vetoes when the steal is worth 0+ to its goal (0+ in the final round); counts blocking a leader at 103% of its size.
- Also blocks any player it expects to end the round within 6 of the solo threshold, leader or not.
- In the final round, goes for the solo win if its track is 25+ from zero, keeping 15 of tally room.

Parameters:

```
{
 "solo_at": 30,
 "anchor_margin": 18,
 "aggr_early": 1.576,
 "aggr_late": 0.0,
 "late_round": 3,
 "room_margin": -2.512,
 "help_weight": 0.373,
 "lie_rate": 0.677,
 "lie_size": 2,
 "veto_threshold": 0.0,
 "deny_weight": 1.03,
 "trust": 0.188,
 "card_cost": 0.412,
 "extreme_cost": 0.924,
 "final_solo_at": 25,
 "final_room_margin": 15.0,
 "final_help_weight": 0.543,
 "final_veto_threshold": 0.0,
 "danger_margin": 6
}
```

Search progress (generation, best, mean): (1, 0.423, 0.325), (2, 0.464, 0.375), (3, 0.463, 0.391), (4, 0.488, 0.420), (5, 0.494, 0.420), (6, 0.511, 0.418), (7, 0.557, 0.472), (8, 0.563, 0.518), (9, 0.582, 0.514), (10, 0.625, 0.513)

```
Best response
=============
Games: 6000    Table: 1:careful_drifter, 2:anchor, 3:tuned, 4:tuned

How games end
  solo win         29.8%
  bust win         15.9%
  shared win       54.3%
  average length  4.59 rounds; 80% reach round 5

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         72.3%   17.8%    0.1%   54.3%   31.4%
  2: anchor                  68.7%    0.1%   14.3%   54.3%   26.8%
  3: tuned                   63.8%    7.8%    1.8%   54.3%   22.4%
  4: tuned                   61.1%    4.4%    2.4%   54.3%   19.4%

Wins by strategy (per seat it occupies)
  careful_drifter            72.3%   17.8%    0.1%
  anchor                     68.7%    0.1%   14.3%
  tuned                      62.5%    6.1%    2.1%

Vetoes
  eligible players per round  1.29
  eligible players who veto    44.0%
  rounds with a veto           37.9%
  vetoes per game             2.60
  vetoed players hit twice+    22.2%
  average drift stolen (abs)  4.9
  games a steal decided        10.3%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner behind at halfway      30.1%
  winner behind before last    36.1%
  won outright in final round   25.2%
  lead changes per game        1.20
  ending spread (0-1)          0.90

Distributions
  per-player drift  mean -0.0  sd 4.4  5/25/50/75/95%: -8 / -2 / +0 / +2 / +8
  round gap         mean +0.0  sd 10.7  5/25/50/75/95%: -17 / -8 / +0 / +8 / +17
```

```
Decisive rounds (largest swing toward the winner)

Seat 1 (careful_drifter), bust wins: 8
  round of the swing     r2: 12%, r3: 25%, r4: 12%, r5: 50%
  swing size             mean 9.1
  was also the last      75%
  own drift              mean -2.8, mean |drift| 5.0
  cards played           mean 2.38
  clue was a lie         0%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: kept its own drift to about 5 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 1 (careful_drifter), solo wins: 1069
  round of the swing     r1: 12%, r2: 8%, r3: 5%, r4: 26%, r5: 49%
  swing size             mean 13.2
  was also the last      74%
  own drift              mean -1.3, mean |drift| 9.3
  cards played           mean 1.76
  clue was a lie         0%
  vetoed someone         4% (mean stolen when it did: +1.1)
  was vetoed             0%
  in plain words: pushed its own track by about 9; mostly told the truth; usually in the round the game ended.

Seat 2 (anchor), bust wins: 856
  round of the swing     r1: 42%, r2: 34%, r3: 13%, r4: 7%, r5: 4%
  swing size             mean 3.5
  was also the last      36%
  own drift              mean -0.0, mean |drift| 0.6
  cards played           mean 1.93
  clue was a lie         99%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             3%
  in plain words: kept its own drift to about 1 while others moved away from zero; lied.

Seat 2 (anchor), solo wins: 5
  round of the swing     r5: 100%
  swing size             mean 21.2
  was also the last      100%
  own drift              mean -10.6, mean |drift| 10.6
  cards played           mean 2.40
  clue was a lie         80%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 11; lied; usually in the round the game ended.

Seat 3 (tuned), bust wins: 105
  round of the swing     r1: 19%, r2: 54%, r3: 10%, r4: 10%, r5: 6%
  swing size             mean 3.1
  was also the last      73%
  own drift              mean +0.2, mean |drift| 2.4
  cards played           mean 1.72
  clue was a lie         53%
  vetoed someone         11% (mean stolen when it did: +3.3)
  was vetoed             1%
  in plain words: kept its own drift to about 2 while others moved away from zero; lied; usually in the round the game ended.

Seat 3 (tuned), solo wins: 467
  round of the swing     r2: 2%, r3: 6%, r4: 2%, r5: 91%
  swing size             mean 22.7
  was also the last      92%
  own drift              mean +0.6, mean |drift| 9.5
  cards played           mean 1.82
  clue was a lie         69%
  vetoed someone         57% (mean stolen when it did: +0.7)
  was vetoed             0%
  in plain words: pushed its own track by about 9; vetoed in 57% of them; lied; usually in the round the game ended.

Seat 4 (tuned), bust wins: 141
  round of the swing     r1: 12%, r2: 64%, r3: 11%, r4: 9%, r5: 4%
  swing size             mean 3.0
  was also the last      82%
  own drift              mean -0.4, mean |drift| 2.4
  cards played           mean 1.70
  clue was a lie         55%
  vetoed someone         11% (mean stolen when it did: +0.8)
  was vetoed             1%
  in plain words: kept its own drift to about 2 while others moved away from zero; lied; usually in the round the game ended.

Seat 4 (tuned), solo wins: 263
  round of the swing     r2: 2%, r3: 5%, r4: 6%, r5: 87%
  swing size             mean 21.5
  was also the last      89%
  own drift              mean +2.4, mean |drift| 7.9
  cards played           mean 1.89
  clue was a lie         70%
  vetoed someone         62% (mean stolen when it did: +1.7)
  was vetoed             1%
  in plain words: pushed its own track by about 8; vetoed in 62% of them; lied; usually in the round the game ended.

```

```
Sensitivity (each parameter moved to its bounds; base score 0.640; differences under ~0.022 are noise)

  parameter                tuned          at low         at high  matters?
  help_weight              0.373      0 -0.257       1 -0.219  yes
  trust                    0.188      0 -0.038       1 -0.230  yes
  deny_weight               1.03      0 -0.134     1.5 +0.016  yes
  final_veto_threshold       0.0      0 +0.000      20 -0.107  yes
  veto_threshold             0.0      0 +0.000      20 -0.106  yes
  final_help_weight        0.543      0 -0.078       1 -0.084  yes
  lie_rate                 0.677      0 -0.065       1 +0.002  yes
  final_solo_at               25      0 -0.065      30 +0.000  yes
  card_cost                0.412     -3 -0.048       3 -0.035  yes
  danger_margin                6      0 +0.001      30 -0.043  a little
  solo_at                     30      0 -0.042      30 +0.000  a little
  extreme_cost             0.924      0 -0.001       4 -0.038  a little
  lie_size                     2      1 -0.021       3 -0.003  no
  anchor_margin               18      2 +0.003      30 +0.000  no
  aggr_early               1.576      0 +0.000      20 +0.000  no
  aggr_late                  0.0      0 +0.000      30 +0.000  no
  late_round                   3      1 +0.000       7 +0.000  no
  room_margin             -2.512    -10 +0.000      15 +0.000  no
  final_room_margin         15.0    -10 +0.000      15 +0.000  no
```

## Self-play

Still moving: the last iteration was accepted with parameter moves 0.18, 0.10; run more iterations to see whether it settles.

Per iteration (champion in own field -> best challenger): 0.922 -> 0.923, 0.907 -> 0.927 (new), 0.985 -> 0.991 (new)

Cross-play: row = strategy in one seat, column = strategy in the other seats; value = row's win score. C0 is the best-response strategy.

```
  C0: 0.904  0.985  0.983
  C1: 0.912  0.987  0.982
  C2: 0.912  0.990  0.976
```

What the final champion does:

- Almost never commits to a solo win before the final round.
- When chasing it, drifts up to 2 a round before round 5, then up to 12.
- Keeps 4 of room between the projected tally and a bust.
- Anchors at zero when it is closest to zero and someone is 25+ further out.
- Gives 22% weight to closing the group's gap (31% in the final round).
- Almost always tells the truth.
- Believes others' clues 31%.
- Vetoes when the steal is worth 3+ to its goal (5+ in the final round); counts blocking a leader at 121% of its size.
- Prefers playing few cards.
- Also blocks any player it expects to end the round within 1 of the solo threshold, leader or not.
- In the final round, goes for the solo win if its track is 25+ from zero, keeping 14 of tally room.

```
Self-play champion, all seats
=============================
Games: 6000    Table: 1:champion, 2:champion, 3:champion, 4:champion

How games end
  solo win          1.1%
  bust win          2.3%
  shared win       96.5%
  average length  4.96 rounds; 98% reach round 5

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: champion                97.7%    0.4%    0.8%   96.5%   25.1%
  2: champion                97.7%    0.3%    0.8%   96.5%   25.1%
  3: champion                97.4%    0.2%    0.7%   96.5%   24.9%
  4: champion                97.5%    0.2%    0.7%   96.5%   25.0%

Wins by strategy (per seat it occupies)
  champion                   97.6%    0.3%    0.7%

Vetoes
  eligible players per round  0.05
  eligible players who veto    11.5%
  rounds with a veto            0.4%
  vetoes per game             0.03
  vetoed players hit twice+    29.6%
  average drift stolen (abs)  4.7
  games a steal decided         0.1%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner behind at halfway      23.2%
  winner behind before last    32.9%
  won outright in final round    1.2%
  lead changes per game        2.51
  ending spread (0-1)          0.16

Distributions
  per-player drift  mean +0.1  sd 2.5  5/25/50/75/95%: -4 / -1 / +0 / +2 / +4
  round gap         mean +0.1  sd 10.7  5/25/50/75/95%: -17 / -8 / +0 / +8 / +17

Flags
  ! shared win ends 97% of games.
```

```
Decisive rounds (largest swing toward the winner)

Seat 1 (champion), bust wins: 46
  round of the swing     r1: 15%, r2: 20%, r3: 41%, r4: 20%, r5: 4%
  swing size             mean 2.3
  was also the last      57%
  own drift              mean -0.2, mean |drift| 2.0
  cards played           mean 1.59
  clue was a lie         0%
  vetoed someone         2% (mean stolen when it did: +5.0)
  was vetoed             0%
  in plain words: kept its own drift to about 2 while others moved away from zero; mostly told the truth.

Seat 1 (champion), solo wins: 24
  round of the swing     r5: 100%
  swing size             mean 20.9
  was also the last      100%
  own drift              mean -5.6, mean |drift| 10.5
  cards played           mean 1.62
  clue was a lie         0%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 10; mostly told the truth; usually in the round the game ended.

Seat 2 (champion), bust wins: 48
  round of the swing     r1: 17%, r2: 29%, r3: 29%, r4: 25%
  swing size             mean 2.6
  was also the last      52%
  own drift              mean +0.2, mean |drift| 2.4
  cards played           mean 1.81
  clue was a lie         0%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: kept its own drift to about 2 while others moved away from zero; mostly told the truth.

Seat 2 (champion), solo wins: 19
  round of the swing     r5: 100%
  swing size             mean 20.8
  was also the last      100%
  own drift              mean -8.3, mean |drift| 10.6
  cards played           mean 1.84
  clue was a lie         0%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 11; mostly told the truth; usually in the round the game ended.

Seat 3 (champion), bust wins: 41
  round of the swing     r1: 15%, r2: 24%, r3: 37%, r4: 20%, r5: 5%
  swing size             mean 3.4
  was also the last      68%
  own drift              mean +0.0, mean |drift| 2.5
  cards played           mean 1.98
  clue was a lie         0%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: kept its own drift to about 2 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 3 (champion), solo wins: 12
  round of the swing     r5: 100%
  swing size             mean 18.5
  was also the last      100%
  own drift              mean -6.2, mean |drift| 9.3
  cards played           mean 1.92
  clue was a lie         0%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 9; mostly told the truth; usually in the round the game ended.

Seat 4 (champion), bust wins: 44
  round of the swing     r1: 25%, r2: 36%, r3: 25%, r4: 9%, r5: 5%
  swing size             mean 2.4
  was also the last      64%
  own drift              mean -0.1, mean |drift| 1.8
  cards played           mean 1.73
  clue was a lie         0%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: kept its own drift to about 2 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 4 (champion), solo wins: 13
  round of the swing     r3: 8%, r4: 15%, r5: 77%
  swing size             mean 14.8
  was also the last      77%
  own drift              mean -5.8, mean |drift| 8.8
  cards played           mean 1.77
  clue was a lie         0%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 9; mostly told the truth; usually in the round the game ended.

```

```
Self-play champion against the fixed bots
=========================================
Games: 6000    Table: 1:careful_drifter, 2:anchor, 3:champion, 4:champion

How games end
  solo win         25.1%
  bust win         37.0%
  shared win       37.8%
  average length  3.95 rounds; 51% reach round 5

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         62.6%   24.6%    0.2%   37.8%   34.2%
  2: anchor                  71.0%    0.0%   33.1%   37.8%   38.8%
  3: champion                43.9%    0.3%    5.7%   37.8%   13.1%
  4: champion                44.6%    0.2%    6.6%   37.8%   13.8%

Wins by strategy (per seat it occupies)
  careful_drifter            62.6%   24.6%    0.2%
  anchor                     71.0%    0.0%   33.1%
  champion                   44.3%    0.3%    6.2%

Vetoes
  eligible players per round  1.57
  eligible players who veto    15.8%
  rounds with a veto           18.9%
  vetoes per game             0.99
  vetoed players hit twice+    26.4%
  average drift stolen (abs)  4.9
  games a steal decided         2.8%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner behind at halfway       3.1%
  winner behind before last    11.6%
  won outright in final round   13.6%
  lead changes per game        0.31
  ending spread (0-1)          0.99

Distributions
  per-player drift  mean -0.0  sd 3.8  5/25/50/75/95%: -8 / -2 / +0 / +2 / +8
  round gap         mean -0.0  sd 10.7  5/25/50/75/95%: -18 / -8 / +0 / +8 / +17

Flags
  ! 'anchor' wins 33% of games outright, at least twice the others' average (16%).
```
