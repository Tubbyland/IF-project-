# Strategy search

Table: seat 1 careful_drifter, seat 2 anchor, seat 3 adaptive, seat 4 adaptive

Rules: n_players=4, hand_size=5, rounds=7, hand_lo=1, hand_hi=20, hand_copies=4, hand_copies_auto=True, personal_lo=15, personal_hi=30, personal_copies=2, collective_mode=split, collective_split=((70, 82), (98, 110)), collective_continuous=(75, 105), win_threshold=30, track_cap=None, bust_limit=20, min_cards=1, max_cards=3, draw_per_round=2, clue_close=2, clue_much=8, vetoes_enabled=True, veto_gap=10, veto_target=any, double_veto_at=2, veto_mode=choose, veto_cost=0, final_multiplier=2, final_doubles_stolen=True, bust_win_requires_near_zero=False, bust_near_zero=5

Win score: solo/bust win 1, shared win 1.0.

## Baseline (adaptive seats on default parameters)

```
Baseline (default adaptive)
===========================
Games: 10000    Table: 1:careful_drifter, 2:anchor, 3:adaptive, 4:adaptive

How games end
  solo win         27.7%
  bust win         60.6%
  shared win       11.7%
  average length  4.55 rounds; 21% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         35.8%   22.9%    1.2%   11.7%   26.6%
  2: anchor                  62.1%    0.4%   50.0%   11.7%   49.7%
  3: adaptive                22.7%    2.5%    8.5%   11.7%   11.6%
  4: adaptive                23.3%    2.2%    9.3%   11.7%   12.0%

Wins by strategy (per seat it occupies)
  careful_drifter            35.8%   22.9%    1.2%
  anchor                     62.1%    0.4%   50.0%
  adaptive                   23.0%    2.4%    8.9%

Vetoes
  eligible players per round  1.47
  eligible players who veto    23.0%
  rounds with a veto           22.5%
  vetoes per game             1.54
  vetoed players hit twice+    43.9%
  average drift stolen (abs)  6.6
  games a steal decided         3.0%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner came from behind       18.5%
  lead changes per game        0.58
  ending spread (0-1)          0.83

Distributions
  per-player drift  mean -0.6  sd 5.5  5/25/50/75/95%: -10 / -3 / +0 / +2 / +9
  round gap         mean +0.1  sd 16.9  5/25/50/75/95%: -26 / -14 / +0 / +14 / +27

Flags
  ! 'anchor' wins 50% of games outright, at least twice the others' average (18%).
```

## Best response

Win score of the tuned seats: 0.486 (default parameters: 0.240).

What the tuned strategy does:

- Commits to a solo win once its track is 25+ from zero.
- When chasing it, drifts up to 13 a round before round 3, then up to 3.
- Keeps 10 of room between the projected tally and a bust.
- Anchors at zero when it is closest to zero and someone is 14+ further out.
- Gives 0% weight to closing the group's gap (32% in the final round).
- Lies on 67% of clues, by 1 band.
- Believes others' clues 100%.
- Vetoes when the steal is worth 0+ to its goal (0+ in the final round); counts blocking a leader at 150% of its size.
- In the final round, goes for the solo win if its track is 27+ from zero, keeping -10 of tally room.

Parameters:

```
{
 "solo_at": 25,
 "anchor_margin": 14,
 "aggr_early": 13.267,
 "aggr_late": 3.334,
 "late_round": 3,
 "room_margin": 9.832,
 "help_weight": 0.0,
 "lie_rate": 0.674,
 "lie_size": 1,
 "veto_threshold": 0.0,
 "deny_weight": 1.5,
 "trust": 1.0,
 "card_cost": 0.29,
 "extreme_cost": 0.194,
 "final_solo_at": 27,
 "final_room_margin": -10.0,
 "final_help_weight": 0.322,
 "final_veto_threshold": 0.0
}
```

Search progress (generation, best, mean): (1, 0.314, 0.206), (2, 0.360, 0.258), (3, 0.419, 0.324), (4, 0.407, 0.344), (5, 0.429, 0.369), (6, 0.433, 0.377), (7, 0.443, 0.397), (8, 0.449, 0.398), (9, 0.473, 0.416), (10, 0.451, 0.409), (11, 0.487, 0.440), (12, 0.490, 0.456), (13, 0.474, 0.439), (14, 0.488, 0.456), (15, 0.497, 0.456), (16, 0.490, 0.461), (17, 0.517, 0.474), (18, 0.494, 0.461), (19, 0.494, 0.464), (20, 0.510, 0.486)

```
Best response
=============
Games: 10000    Table: 1:careful_drifter, 2:anchor, 3:tuned, 4:tuned

How games end
  solo win          1.5%
  bust win         88.8%
  shared win        9.8%
  average length  3.72 rounds; 12% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         11.8%    0.9%    1.2%    9.8%    4.0%
  2: anchor                  67.9%    0.2%   57.9%    9.8%   42.9%
  3: tuned                   49.4%    0.2%   39.4%    9.8%   26.8%
  4: tuned                   49.2%    0.1%   39.3%    9.8%   26.3%

Wins by strategy (per seat it occupies)
  careful_drifter            11.8%    0.9%    1.2%
  anchor                     67.9%    0.2%   57.9%
  tuned                      49.3%    0.2%   39.4%

Vetoes
  eligible players per round  1.33
  eligible players who veto    65.5%
  rounds with a veto           52.7%
  vetoes per game             3.24
  vetoed players hit twice+    40.4%
  average drift stolen (abs)  2.9
  games a steal decided        10.8%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 1 games (0.0%)

Tension
  winner came from behind       13.9%
  lead changes per game        0.29
  ending spread (0-1)          0.36

Distributions
  per-player drift  mean -0.7  sd 4.8  5/25/50/75/95%: -10 / -1 / +0 / +1 / +9
  round gap         mean +0.2  sd 16.9  5/25/50/75/95%: -26 / -14 / +0 / +14 / +27

Flags
  ! bust win ends 89% of games.
  ! 'anchor' wins 58% of games outright, at least twice the others' average (21%).
```

```
Decisive rounds (largest swing toward the winner)

Seat 1 (careful_drifter), bust wins: 120
  round of the swing     r1: 8%, r2: 25%, r3: 22%, r4: 24%, r5: 15%, r6: 3%, r7: 2%
  swing size             mean 7.9
  was also the last      72%
  own drift              mean -6.6, mean |drift| 7.8
  cards played           mean 2.53
  clue was a lie         0%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: kept its own drift to about 8 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 1 (careful_drifter), solo wins: 90
  round of the swing     r1: 8%, r2: 2%, r3: 2%, r4: 2%, r5: 2%, r6: 26%, r7: 58%
  swing size             mean 22.5
  was also the last      88%
  own drift              mean -6.3, mean |drift| 13.9
  cards played           mean 1.69
  clue was a lie         0%
  vetoed someone         14% (mean stolen when it did: -5.6)
  was vetoed             0%
  in plain words: pushed its own track by about 14; mostly told the truth; usually in the round the game ended.

Seat 2 (anchor), bust wins: 5790
  round of the swing     r1: 31%, r2: 38%, r3: 17%, r4: 8%, r5: 4%, r6: 2%, r7: 1%
  swing size             mean 1.5
  was also the last      39%
  own drift              mean +0.2, mean |drift| 0.9
  cards played           mean 2.03
  clue was a lie         99%
  vetoed someone         0% (mean stolen when it did: +1.2)
  was vetoed             0%
  in plain words: kept its own drift to about 1 while others moved away from zero; lied.

Seat 2 (anchor), solo wins: 24
  round of the swing     r2: 8%, r3: 8%, r4: 4%, r5: 4%, r6: 8%, r7: 67%
  swing size             mean 22.6
  was also the last      83%
  own drift              mean -14.5, mean |drift| 14.5
  cards played           mean 2.29
  clue was a lie         83%
  vetoed someone         8% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 15; lied; usually in the round the game ended.

Seat 3 (tuned), bust wins: 3944
  round of the swing     r1: 48%, r2: 24%, r3: 14%, r4: 8%, r5: 4%, r6: 2%, r7: 0%
  swing size             mean 1.0
  was also the last      37%
  own drift              mean -0.0, mean |drift| 0.4
  cards played           mean 2.02
  clue was a lie         68%
  vetoed someone         28% (mean stolen when it did: +0.1)
  was vetoed             7%
  in plain words: kept its own drift to about 0 while others moved away from zero; vetoed in 28% of them; lied.

Seat 3 (tuned), solo wins: 22
  round of the swing     r3: 9%, r4: 5%, r5: 23%, r6: 5%, r7: 59%
  swing size             mean 25.3
  was also the last      82%
  own drift              mean -16.7, mean |drift| 16.7
  cards played           mean 2.09
  clue was a lie         64%
  vetoed someone         50% (mean stolen when it did: -0.9)
  was vetoed             0%
  in plain words: pushed its own track by about 17; vetoed in 50% of them; lied; usually in the round the game ended.

Seat 4 (tuned), bust wins: 3930
  round of the swing     r1: 46%, r2: 24%, r3: 15%, r4: 8%, r5: 4%, r6: 2%, r7: 0%
  swing size             mean 1.0
  was also the last      38%
  own drift              mean -0.0, mean |drift| 0.3
  cards played           mean 2.02
  clue was a lie         67%
  vetoed someone         30% (mean stolen when it did: +0.1)
  was vetoed             7%
  in plain words: kept its own drift to about 0 while others moved away from zero; vetoed in 30% of them; lied.

Seat 4 (tuned), solo wins: 11
  round of the swing     r4: 9%, r5: 18%, r7: 73%
  swing size             mean 21.8
  was also the last      91%
  own drift              mean -13.4, mean |drift| 13.4
  cards played           mean 2.27
  clue was a lie         73%
  vetoed someone         27% (mean stolen when it did: -2.0)
  was vetoed             0%
  in plain words: pushed its own track by about 13; vetoed in 27% of them; lied; usually in the round the game ended.

```

```
Sensitivity (each parameter moved to its bounds; base score 0.490; differences under ~0.018 are noise)

  parameter                tuned          at low         at high  matters?
  solo_at                     25      0 -0.412      30 +0.000  yes
  help_weight                0.0      0 +0.000       1 -0.239  yes
  card_cost                 0.29     -3 -0.109       3 -0.142  yes
  extreme_cost             0.194      0 +0.003       4 -0.117  yes
  veto_threshold             0.0      0 +0.000      20 -0.093  yes
  final_solo_at               27      0 -0.032      30 +0.000  a little
  deny_weight                1.5      0 -0.027     1.5 +0.000  a little
  final_veto_threshold       0.0      0 +0.000      20 -0.022  a little
  final_help_weight        0.322      0 -0.013       1 -0.016  no
  trust                      1.0      0 -0.014       1 +0.000  no
  lie_size                     1      1 +0.000       3 -0.004  no
  anchor_margin               14      2 +0.003      30 -0.003  no
  lie_rate                 0.674      0 +0.002       1 +0.002  no
  room_margin              9.832    -10 -0.000      15 -0.000  no
  aggr_early              13.267      0 +0.000      20 +0.000  no
  aggr_late                3.334      0 +0.000      30 +0.000  no
  late_round                   3      1 +0.000       7 +0.000  no
  final_room_margin        -10.0    -10 +0.000      15 +0.000  no
```
