# Strategy search

Table: seat 1 careful_drifter, seat 2 anchor, seat 3 adaptive, seat 4 adaptive

Rules: n_players=4, hand_size=5, rounds=6, hand_lo=1, hand_hi=18, hand_copies=4, hand_copies_auto=True, personal_lo=10, personal_hi=20, personal_copies=2, personal_copies_auto=True, collective_mode=continuous, collective_split=((70, 82), (98, 110)), collective_continuous=(54, 66), win_threshold=25, track_cap=None, bust_limit=18, min_cards=1, max_cards=3, draw_per_round=1, clue_close=2, clue_much=8, vetoes_enabled=True, veto_gap=8, veto_target=any, double_veto_at=2, veto_mode=take, veto_cost=0, final_multiplier=2, final_doubles_stolen=True, bust_win_requires_near_zero=False, bust_near_zero=5

Win score: solo/bust win 1, shared win 1.0.

## Baseline (adaptive seats on default parameters)

```
Baseline (default adaptive)
===========================
Games: 6000    Table: 1:careful_drifter, 2:anchor, 3:adaptive, 4:adaptive

How games end
  solo win         31.0%
  bust win         49.7%
  shared win       19.4%
  average length  4.57 rounds; 41% reach round 6

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         48.0%   26.6%    2.1%   19.4%   33.2%
  2: anchor                  50.4%    0.8%   30.2%   19.4%   32.1%
  3: adaptive                35.1%    1.8%   14.0%   19.4%   17.8%
  4: adaptive                34.6%    1.9%   13.4%   19.4%   17.0%

Wins by strategy (per seat it occupies)
  careful_drifter            48.0%   26.6%    2.1%
  anchor                     50.4%    0.8%   30.2%
  adaptive                   34.8%    1.8%   13.7%

Vetoes
  eligible players per round  1.62
  eligible players who veto     6.8%
  rounds with a veto            9.0%
  vetoes per game             0.50
  vetoed players hit twice+    15.9%
  average drift stolen (abs)  6.0
  games a steal decided         2.9%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner behind at halfway      21.7%
  winner behind before last    26.1%
  won outright in final round   21.6%
  lead changes per game        0.60
  ending spread (0-1)          0.94

Distributions
  per-player drift  mean -0.6  sd 4.6  5/25/50/75/95%: -9 / -3 / +0 / +2 / +8
  round gap         mean -0.1  sd 7.0  5/25/50/75/95%: -12 / -5 / +0 / +5 / +12
```

## Best response

Win score of the tuned seats: 0.459 (default parameters: 0.334).

What the tuned strategy does:

- Commits to a solo win once its track is 23+ from zero.
- When chasing it, drifts up to 9 a round before round 6, then up to 12.
- Keeps 2 of room between the projected tally and a bust.
- Anchors at zero when it is closest to zero and someone is 9+ further out.
- Gives 37% weight to closing the group's gap (24% in the final round).
- Lies on 88% of clues, by 2 bands.
- Believes others' clues 29%.
- Vetoes when the steal is worth 0+ to its goal (1+ in the final round); counts blocking a leader at 142% of its size.
- Prefers playing many cards.
- Hoards very high and very low cards.
- In the final round, goes for the solo win if its track is 16+ from zero, keeping 9 of tally room.

Parameters:

```
{
 "solo_at": 23,
 "anchor_margin": 9,
 "aggr_early": 9.471,
 "aggr_late": 12.197,
 "late_round": 6,
 "room_margin": 2.104,
 "help_weight": 0.367,
 "lie_rate": 0.885,
 "lie_size": 2,
 "veto_threshold": 0.229,
 "deny_weight": 1.416,
 "trust": 0.294,
 "card_cost": -2.007,
 "extreme_cost": 2.65,
 "final_solo_at": 16,
 "final_room_margin": 9.232,
 "final_help_weight": 0.243,
 "final_veto_threshold": 1.485,
 "danger_margin": 0
}
```

Search progress (generation, best, mean): (1, 0.347, 0.274), (2, 0.396, 0.309), (3, 0.381, 0.329), (4, 0.386, 0.348), (5, 0.404, 0.363), (6, 0.415, 0.352), (7, 0.444, 0.410), (8, 0.442, 0.404), (9, 0.467, 0.422), (10, 0.497, 0.453)

```
Best response
=============
Games: 6000    Table: 1:careful_drifter, 2:anchor, 3:tuned, 4:tuned

How games end
  solo win         17.6%
  bust win         47.8%
  shared win       34.6%
  average length  5.34 rounds; 67% reach round 6

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         45.6%    7.8%    3.1%   34.6%   19.2%
  2: anchor                  68.3%    2.2%   31.5%   34.6%   40.3%
  3: tuned                   48.1%    3.9%    9.6%   34.6%   20.8%
  4: tuned                   47.0%    3.9%    8.5%   34.6%   19.8%

Wins by strategy (per seat it occupies)
  careful_drifter            45.6%    7.8%    3.1%
  anchor                     68.3%    2.2%   31.5%
  tuned                      47.5%    3.9%    9.1%

Vetoes
  eligible players per round  1.33
  eligible players who veto    43.4%
  rounds with a veto           39.8%
  vetoes per game             3.09
  vetoed players hit twice+    26.1%
  average drift stolen (abs)  5.5
  games a steal decided         6.7%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner behind at halfway      38.5%
  winner behind before last    40.5%
  won outright in final round   32.7%
  lead changes per game        1.61
  ending spread (0-1)          0.93

Distributions
  per-player drift  mean -0.7  sd 5.0  5/25/50/75/95%: -9 / -3 / +0 / +2 / +8
  round gap         mean -0.0  sd 7.1  5/25/50/75/95%: -12 / -5 / +0 / +5 / +12

Flags
  ! 'anchor' wins 34% of games outright, at least twice the others' average (12%).
```

```
Decisive rounds (largest swing toward the winner)

Seat 1 (careful_drifter), bust wins: 189
  round of the swing     r2: 4%, r3: 5%, r4: 16%, r5: 24%, r6: 51%
  swing size             mean 13.7
  was also the last      83%
  own drift              mean -6.8, mean |drift| 7.7
  cards played           mean 1.15
  clue was a lie         0%
  vetoed someone         4% (mean stolen when it did: +3.2)
  was vetoed             7%
  in plain words: kept its own drift to about 8 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 1 (careful_drifter), solo wins: 468
  round of the swing     r1: 11%, r2: 11%, r3: 3%, r4: 10%, r5: 24%, r6: 41%
  swing size             mean 15.0
  was also the last      69%
  own drift              mean -4.6, mean |drift| 10.6
  cards played           mean 1.41
  clue was a lie         0%
  vetoed someone         10% (mean stolen when it did: -8.7)
  was vetoed             0%
  in plain words: pushed its own track by about 11; mostly told the truth; usually in the round the game ended.

Seat 2 (anchor), bust wins: 1892
  round of the swing     r1: 18%, r2: 20%, r3: 18%, r4: 16%, r5: 13%, r6: 15%
  swing size             mean 5.7
  was also the last      39%
  own drift              mean -0.4, mean |drift| 1.4
  cards played           mean 1.60
  clue was a lie         99%
  vetoed someone         1% (mean stolen when it did: -1.2)
  was vetoed             8%
  in plain words: kept its own drift to about 1 while others moved away from zero; lied.

Seat 2 (anchor), solo wins: 130
  round of the swing     r3: 5%, r4: 4%, r5: 8%, r6: 82%
  swing size             mean 24.1
  was also the last      91%
  own drift              mean -13.3, mean |drift| 13.3
  cards played           mean 1.08
  clue was a lie         85%
  vetoed someone         7% (mean stolen when it did: -4.4)
  was vetoed             0%
  in plain words: pushed its own track by about 13; lied; usually in the round the game ended.

Seat 3 (tuned), bust wins: 576
  round of the swing     r1: 2%, r2: 16%, r3: 9%, r4: 16%, r5: 24%, r6: 34%
  swing size             mean 7.9
  was also the last      70%
  own drift              mean -0.3, mean |drift| 4.3
  cards played           mean 1.54
  clue was a lie         86%
  vetoed someone         26% (mean stolen when it did: -1.7)
  was vetoed             6%
  in plain words: kept its own drift to about 4 while others moved away from zero; vetoed in 26% of them; lied; usually in the round the game ended.

Seat 3 (tuned), solo wins: 233
  round of the swing     r2: 3%, r3: 9%, r4: 9%, r5: 10%, r6: 70%
  swing size             mean 21.1
  was also the last      80%
  own drift              mean -6.4, mean |drift| 9.4
  cards played           mean 1.34
  clue was a lie         87%
  vetoed someone         52% (mean stolen when it did: -8.1)
  was vetoed             2%
  in plain words: pushed its own track by about 9; vetoed in 52% of them; lied; usually in the round the game ended.

Seat 4 (tuned), bust wins: 512
  round of the swing     r1: 2%, r2: 16%, r3: 15%, r4: 17%, r5: 23%, r6: 28%
  swing size             mean 7.4
  was also the last      65%
  own drift              mean +0.4, mean |drift| 4.0
  cards played           mean 1.54
  clue was a lie         86%
  vetoed someone         26% (mean stolen when it did: -2.5)
  was vetoed             5%
  in plain words: kept its own drift to about 4 while others moved away from zero; vetoed in 26% of them; lied; usually in the round the game ended.

Seat 4 (tuned), solo wins: 233
  round of the swing     r1: 0%, r2: 2%, r3: 7%, r4: 6%, r5: 10%, r6: 73%
  swing size             mean 21.3
  was also the last      81%
  own drift              mean -6.4, mean |drift| 9.5
  cards played           mean 1.39
  clue was a lie         90%
  vetoed someone         48% (mean stolen when it did: -11.1)
  was vetoed             1%
  in plain words: pushed its own track by about 10; vetoed in 48% of them; lied; usually in the round the game ended.

```

```
Sensitivity (each parameter moved to its bounds; base score 0.479; differences under ~0.022 are noise)

  parameter                tuned          at low         at high  matters?
  solo_at                     23      0 -0.232      30 +0.001  yes
  help_weight              0.367      0 -0.088       1 -0.117  yes
  trust                    0.294      0 -0.009       1 -0.111  yes
  veto_threshold           0.229      0 +0.002      20 -0.095  yes
  deny_weight              1.416      0 -0.083     1.5 +0.003  yes
  card_cost               -2.007     -3 -0.002       3 -0.072  yes
  final_solo_at               16      0 -0.050      30 +0.005  yes
  danger_margin                0      0 +0.000      30 -0.049  yes
  final_veto_threshold     1.485      0 +0.001      20 -0.035  a little
  lie_size                     2      1 -0.029       3 +0.008  a little
  lie_rate                 0.885      0 -0.028       1 +0.003  a little
  final_help_weight        0.243      0 -0.014       1 -0.015  no
  extreme_cost              2.65      0 -0.010       4 +0.009  no
  anchor_margin                9      2 -0.006      30 -0.009  no
  final_room_margin        9.232    -10 +0.000      15 +0.002  no
  room_margin              2.104    -10 +0.000      15 +0.001  no
  aggr_early               9.471      0 +0.001      20 +0.000  no
  aggr_late               12.197      0 +0.000      30 +0.000  no
  late_round                   6      1 +0.000       7 +0.000  no
```

## Self-play

Converging: champions changed 1 time(s) and the last challenger could not beat the champion (parameter moves: 0.10).

Per iteration (champion in own field -> best challenger): 0.665 -> 0.707 (new), 0.661 -> 0.676, 0.670 -> 0.679

Cross-play: row = strategy in one seat, column = strategy in the other seats; value = row's win score. C0 is the best-response strategy.

```
  C0: 0.690  0.661
  C1: 0.724  0.660
```

What the final champion does:

- Commits to a solo win once its track is 23+ from zero.
- When chasing it, drifts up to 12 a round before round 6, then up to 11.
- Keeps 3 of room between the projected tally and a bust.
- Anchors at zero when it is closest to zero and someone is 9+ further out.
- Gives 9% weight to closing the group's gap (12% in the final round).
- Lies on 63% of clues, by 2 bands.
- Believes others' clues 33%.
- Vetoes when the steal is worth 3+ to its goal (1+ in the final round); counts blocking a leader at 118% of its size.
- Prefers playing many cards.
- Hoards very high and very low cards.
- In the final round, goes for the solo win if its track is 30+ from zero, keeping 4 of tally room.

```
Self-play champion, all seats
=============================
Games: 6000    Table: 1:champion, 2:champion, 3:champion, 4:champion

How games end
  solo win         13.6%
  bust win         36.4%
  shared win       50.0%
  average length  5.68 rounds; 79% reach round 6

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: champion                63.6%    3.3%   10.3%   50.0%   24.5%
  2: champion                63.5%    3.3%   10.2%   50.0%   24.5%
  3: champion                64.9%    4.0%   10.9%   50.0%   25.8%
  4: champion                64.4%    3.2%   11.2%   50.0%   25.2%

Wins by strategy (per seat it occupies)
  champion                   64.1%    3.4%   10.6%

Vetoes
  eligible players per round  0.27
  eligible players who veto    41.8%
  rounds with a veto            6.6%
  vetoes per game             0.64
  vetoed players hit twice+    42.1%
  average drift stolen (abs)  11.3
  games a steal decided         4.5%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner behind at halfway      51.9%
  winner behind before last    53.8%
  won outright in final round   29.1%
  lead changes per game        2.99
  ending spread (0-1)          0.90

Distributions
  per-player drift  mean -0.5  sd 3.5  5/25/50/75/95%: -8 / -2 / +0 / +1 / +4
  round gap         mean +0.0  sd 7.1  5/25/50/75/95%: -12 / -5 / +0 / +5 / +12
```

```
Decisive rounds (largest swing toward the winner)

Seat 1 (champion), bust wins: 616
  round of the swing     r1: 3%, r2: 10%, r3: 16%, r4: 19%, r5: 21%, r6: 31%
  swing size             mean 4.7
  was also the last      58%
  own drift              mean -0.1, mean |drift| 2.1
  cards played           mean 1.40
  clue was a lie         67%
  vetoed someone         6% (mean stolen when it did: -4.7)
  was vetoed             3%
  in plain words: kept its own drift to about 2 while others moved away from zero; lied.

Seat 1 (champion), solo wins: 197
  round of the swing     r3: 3%, r4: 3%, r5: 9%, r6: 86%
  swing size             mean 24.5
  was also the last      94%
  own drift              mean -10.1, mean |drift| 10.6
  cards played           mean 1.15
  clue was a lie         65%
  vetoed someone         30% (mean stolen when it did: -21.0)
  was vetoed             1%
  in plain words: pushed its own track by about 11; vetoed in 30% of them; lied; usually in the round the game ended.

Seat 2 (champion), bust wins: 612
  round of the swing     r1: 3%, r2: 11%, r3: 13%, r4: 20%, r5: 20%, r6: 32%
  swing size             mean 4.6
  was also the last      61%
  own drift              mean -0.2, mean |drift| 2.0
  cards played           mean 1.37
  clue was a lie         63%
  vetoed someone         7% (mean stolen when it did: -1.4)
  was vetoed             2%
  in plain words: kept its own drift to about 2 while others moved away from zero; lied; usually in the round the game ended.

Seat 2 (champion), solo wins: 197
  round of the swing     r3: 1%, r4: 2%, r5: 3%, r6: 94%
  swing size             mean 26.8
  was also the last      96%
  own drift              mean -10.4, mean |drift| 10.7
  cards played           mean 1.12
  clue was a lie         59%
  vetoed someone         35% (mean stolen when it did: -22.9)
  was vetoed             1%
  in plain words: pushed its own track by about 11; vetoed in 35% of them; lied; usually in the round the game ended.

Seat 3 (champion), bust wins: 653
  round of the swing     r1: 3%, r2: 9%, r3: 16%, r4: 20%, r5: 23%, r6: 28%
  swing size             mean 4.7
  was also the last      58%
  own drift              mean +0.1, mean |drift| 2.2
  cards played           mean 1.38
  clue was a lie         63%
  vetoed someone         5% (mean stolen when it did: -0.7)
  was vetoed             3%
  in plain words: kept its own drift to about 2 while others moved away from zero; lied.

Seat 3 (champion), solo wins: 237
  round of the swing     r3: 3%, r4: 2%, r5: 5%, r6: 90%
  swing size             mean 26.4
  was also the last      96%
  own drift              mean -10.6, mean |drift| 10.8
  cards played           mean 1.17
  clue was a lie         68%
  vetoed someone         32% (mean stolen when it did: -22.0)
  was vetoed             0%
  in plain words: pushed its own track by about 11; vetoed in 32% of them; lied; usually in the round the game ended.

Seat 4 (champion), bust wins: 669
  round of the swing     r1: 3%, r2: 10%, r3: 17%, r4: 20%, r5: 18%, r6: 32%
  swing size             mean 4.8
  was also the last      58%
  own drift              mean +0.2, mean |drift| 2.2
  cards played           mean 1.39
  clue was a lie         59%
  vetoed someone         5% (mean stolen when it did: -6.0)
  was vetoed             4%
  in plain words: kept its own drift to about 2 while others moved away from zero; lied.

Seat 4 (champion), solo wins: 193
  round of the swing     r2: 2%, r3: 1%, r4: 5%, r5: 5%, r6: 88%
  swing size             mean 25.4
  was also the last      94%
  own drift              mean -10.4, mean |drift| 10.8
  cards played           mean 1.12
  clue was a lie         71%
  vetoed someone         32% (mean stolen when it did: -21.7)
  was vetoed             0%
  in plain words: pushed its own track by about 11; vetoed in 32% of them; lied; usually in the round the game ended.

```

```
Self-play champion against the fixed bots
=========================================
Games: 6000    Table: 1:careful_drifter, 2:anchor, 3:champion, 4:champion

How games end
  solo win         15.3%
  bust win         61.2%
  shared win       23.5%
  average length  4.78 rounds; 45% reach round 6

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         36.0%   10.3%    2.2%   23.5%   17.9%
  2: anchor                  62.5%    1.5%   37.5%   23.5%   39.6%
  3: champion                42.7%    2.1%   17.2%   23.5%   21.4%
  4: champion                42.4%    1.6%   17.3%   23.5%   21.1%

Wins by strategy (per seat it occupies)
  careful_drifter            36.0%   10.3%    2.2%
  anchor                     62.5%    1.5%   37.5%
  champion                   42.6%    1.8%   17.2%

Vetoes
  eligible players per round  1.54
  eligible players who veto    15.2%
  rounds with a veto           18.1%
  vetoes per game             1.12
  vetoed players hit twice+    20.4%
  average drift stolen (abs)  6.0
  games a steal decided         3.8%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner behind at halfway      26.8%
  winner behind before last    31.7%
  won outright in final round   21.8%
  lead changes per game        0.79
  ending spread (0-1)          0.84

Distributions
  per-player drift  mean -0.6  sd 4.3  5/25/50/75/95%: -9 / -2 / +0 / +1 / +7
  round gap         mean -0.1  sd 7.1  5/25/50/75/95%: -12 / -5 / +0 / +5 / +12

Flags
  ! 'anchor' wins 39% of games outright, at least twice the others' average (16%).
```
