# Strategy search

Table: seat 1 careful_drifter, seat 2 anchor, seat 3 adaptive, seat 4 adaptive

Rules: n_players=4, hand_size=5, rounds=7, hand_lo=1, hand_hi=20, hand_copies=4, hand_copies_auto=True, personal_lo=15, personal_hi=30, personal_copies=2, collective_mode=split, collective_split=((70, 82), (98, 110)), collective_continuous=(75, 105), win_threshold=30, track_cap=None, bust_limit=20, min_cards=1, max_cards=3, draw_per_round=2, clue_close=2, clue_much=8, vetoes_enabled=True, veto_gap=10, veto_target=any, double_veto_at=2, veto_mode=block, veto_cost=0, final_multiplier=2, final_doubles_stolen=True, bust_win_requires_near_zero=False, bust_near_zero=5

Win score: solo/bust win 1, shared win 1.0.

## Baseline (adaptive seats on default parameters)

```
Baseline (default adaptive)
===========================
Games: 10000    Table: 1:careful_drifter, 2:anchor, 3:adaptive, 4:adaptive

How games end
  solo win         31.6%
  bust win         58.7%
  shared win        9.6%
  average length  4.47 rounds; 18% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         37.7%   26.8%    1.2%    9.6%   30.1%
  2: anchor                  58.5%    0.3%   48.6%    9.6%   47.8%
  3: adaptive                20.5%    2.6%    8.3%    9.6%   11.1%
  4: adaptive                20.7%    2.2%    8.8%    9.6%   11.1%

Wins by strategy (per seat it occupies)
  careful_drifter            37.7%   26.8%    1.2%
  anchor                     58.5%    0.3%   48.6%
  adaptive                   20.6%    2.4%    8.5%

Vetoes
  eligible players per round  1.44
  eligible players who veto    15.6%
  rounds with a veto           13.7%
  vetoes per game             1.01
  vetoed players hit twice+    64.5%
  average drift stolen (abs)  0.0
  games a steal decided         1.1%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 0 games (0.0%)

Tension
  winner came from behind       17.2%
  lead changes per game        0.58
  ending spread (0-1)          0.82

Distributions
  per-player drift  mean -0.6  sd 5.5  5/25/50/75/95%: -10 / -3 / +0 / +2 / +9
  round gap         mean +0.1  sd 16.9  5/25/50/75/95%: -26 / -14 / +0 / +14 / +27

Flags
  ! 'anchor' wins 49% of games outright, at least twice the others' average (19%).
```

## Best response

Win score of the tuned seats: 0.474 (default parameters: 0.214).

What the tuned strategy does:

- Commits to a solo win once its track is 27+ from zero.
- When chasing it, drifts up to 0 a round before round 5, then up to 26.
- Keeps 9 of room between the projected tally and a bust.
- Anchors at zero when it is closest to zero and someone is 3+ further out.
- Gives 0% weight to closing the group's gap (39% in the final round).
- Lies on 45% of clues, by 1 band.
- Believes others' clues 100%.
- Vetoes when the steal is worth 0+ to its goal (0+ in the final round); counts blocking a leader at 112% of its size.
- In the final round, goes for the solo win if its track is 30+ from zero, keeping -10 of tally room.

Parameters:

```
{
 "solo_at": 27,
 "anchor_margin": 3,
 "aggr_early": 0.0,
 "aggr_late": 25.882,
 "late_round": 5,
 "room_margin": 9.36,
 "help_weight": 0.0,
 "lie_rate": 0.454,
 "lie_size": 1,
 "veto_threshold": 0.0,
 "deny_weight": 1.115,
 "trust": 1.0,
 "card_cost": 0.17,
 "extreme_cost": 0.225,
 "final_solo_at": 30,
 "final_room_margin": -10.0,
 "final_help_weight": 0.393,
 "final_veto_threshold": 0.0
}
```

Search progress (generation, best, mean): (1, 0.310, 0.199), (2, 0.343, 0.260), (3, 0.444, 0.288), (4, 0.430, 0.338), (5, 0.469, 0.372), (6, 0.459, 0.404), (7, 0.465, 0.422), (8, 0.477, 0.427), (9, 0.480, 0.449), (10, 0.470, 0.441), (11, 0.499, 0.463), (12, 0.479, 0.457), (13, 0.457, 0.437), (14, 0.482, 0.461), (15, 0.484, 0.452), (16, 0.477, 0.451), (17, 0.512, 0.472), (18, 0.477, 0.448), (19, 0.479, 0.447), (20, 0.494, 0.470)

```
Best response
=============
Games: 10000    Table: 1:careful_drifter, 2:anchor, 3:tuned, 4:tuned

How games end
  solo win          1.8%
  bust win         88.5%
  shared win        9.7%
  average length  3.72 rounds; 12% reach round 7

Wins by seat (share = ties split evenly; shared wins count for everyone)
  seat                     any win    solo    bust  shared   share
  1: careful_drifter         11.9%    0.9%    1.2%    9.7%    4.0%
  2: anchor                  68.4%    0.2%   58.4%    9.7%   43.7%
  3: tuned                   48.4%    0.4%   38.2%    9.7%   26.3%
  4: tuned                   48.2%    0.2%   38.3%    9.7%   25.9%

Wins by strategy (per seat it occupies)
  careful_drifter            11.9%    0.9%    1.2%
  anchor                     68.4%    0.2%   58.4%
  tuned                      48.3%    0.3%   38.3%

Vetoes
  eligible players per round  1.33
  eligible players who veto    65.0%
  rounds with a veto           52.8%
  vetoes per game             3.22
  vetoed players hit twice+    40.5%
  average drift stolen (abs)  0.0
  games a steal decided         8.5%
  kingmaking (20+ dump double-vetoed into a vetoer's win): 1 games (0.0%)

Tension
  winner came from behind       13.1%
  lead changes per game        0.30
  ending spread (0-1)          0.37

Distributions
  per-player drift  mean -0.7  sd 4.8  5/25/50/75/95%: -10 / -1 / +0 / +1 / +9
  round gap         mean +0.2  sd 16.9  5/25/50/75/95%: -26 / -14 / +0 / +14 / +27

Flags
  ! bust win ends 88% of games.
  ! 'anchor' wins 59% of games outright, at least twice the others' average (20%).
```

```
Decisive rounds (largest swing toward the winner)

Seat 1 (careful_drifter), bust wins: 123
  round of the swing     r1: 7%, r2: 25%, r3: 24%, r4: 24%, r5: 11%, r6: 4%, r7: 5%
  swing size             mean 8.1
  was also the last      72%
  own drift              mean -6.6, mean |drift| 7.7
  cards played           mean 2.55
  clue was a lie         0%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: kept its own drift to about 8 while others moved away from zero; mostly told the truth; usually in the round the game ended.

Seat 1 (careful_drifter), solo wins: 93
  round of the swing     r1: 11%, r2: 4%, r3: 2%, r4: 4%, r5: 1%, r6: 24%, r7: 54%
  swing size             mean 20.5
  was also the last      80%
  own drift              mean -5.1, mean |drift| 13.7
  cards played           mean 1.71
  clue was a lie         0%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 14; mostly told the truth; usually in the round the game ended.

Seat 2 (anchor), bust wins: 5841
  round of the swing     r1: 31%, r2: 38%, r3: 17%, r4: 8%, r5: 3%, r6: 2%, r7: 1%
  swing size             mean 1.5
  was also the last      39%
  own drift              mean +0.2, mean |drift| 0.9
  cards played           mean 2.04
  clue was a lie         99%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: kept its own drift to about 1 while others moved away from zero; lied.

Seat 2 (anchor), solo wins: 24
  round of the swing     r2: 4%, r3: 8%, r4: 8%, r5: 4%, r6: 12%, r7: 62%
  swing size             mean 23.3
  was also the last      83%
  own drift              mean -15.3, mean |drift| 15.3
  cards played           mean 2.38
  clue was a lie         83%
  vetoed someone         0% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 15; lied; usually in the round the game ended.

Seat 3 (tuned), bust wins: 3823
  round of the swing     r1: 50%, r2: 24%, r3: 13%, r4: 7%, r5: 3%, r6: 2%, r7: 0%
  swing size             mean 1.0
  was also the last      36%
  own drift              mean -0.0, mean |drift| 0.4
  cards played           mean 2.03
  clue was a lie         46%
  vetoed someone         27% (mean stolen when it did: +0.0)
  was vetoed             6%
  in plain words: kept its own drift to about 0 while others moved away from zero; vetoed in 27% of them; mostly told the truth.

Seat 3 (tuned), solo wins: 45
  round of the swing     r3: 2%, r4: 2%, r5: 7%, r6: 4%, r7: 84%
  swing size             mean 28.4
  was also the last      98%
  own drift              mean -8.1, mean |drift| 16.4
  cards played           mean 2.11
  clue was a lie         42%
  vetoed someone         60% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 16; vetoed in 60% of them; mostly told the truth; usually in the round the game ended.

Seat 4 (tuned), bust wins: 3829
  round of the swing     r1: 48%, r2: 24%, r3: 14%, r4: 8%, r5: 4%, r6: 2%, r7: 0%
  swing size             mean 1.0
  was also the last      36%
  own drift              mean +0.0, mean |drift| 0.3
  cards played           mean 2.02
  clue was a lie         45%
  vetoed someone         27% (mean stolen when it did: +0.0)
  was vetoed             5%
  in plain words: kept its own drift to about 0 while others moved away from zero; vetoed in 27% of them; mostly told the truth.

Seat 4 (tuned), solo wins: 18
  round of the swing     r4: 6%, r5: 11%, r7: 83%
  swing size             mean 23.4
  was also the last      100%
  own drift              mean -10.4, mean |drift| 13.8
  cards played           mean 2.06
  clue was a lie         28%
  vetoed someone         33% (mean stolen when it did: +0.0)
  was vetoed             0%
  in plain words: pushed its own track by about 14; vetoed in 33% of them; mostly told the truth; usually in the round the game ended.

```

```
Sensitivity (each parameter moved to its bounds; base score 0.476; differences under ~0.018 are noise)

  parameter                tuned          at low         at high  matters?
  help_weight                0.0      0 +0.000       1 -0.208  yes
  card_cost                 0.17     -3 -0.117       3 -0.143  yes
  veto_threshold             0.0      0 +0.000      20 -0.123  yes
  extreme_cost             0.225      0 +0.001       4 -0.120  yes
  solo_at                     27      0 -0.068      30 +0.000  yes
  deny_weight              1.115      0 -0.048     1.5 +0.000  yes
  final_veto_threshold       0.0      0 +0.000      20 -0.026  a little
  trust                      1.0      0 -0.015       1 +0.000  no
  final_help_weight        0.393      0 -0.014       1 -0.014  no
  final_solo_at               30      0 -0.013      30 +0.000  no
  anchor_margin                3      2 +0.000      30 -0.004  no
  lie_rate                 0.454      0 +0.004       1 +0.002  no
  lie_size                     1      1 +0.000       3 +0.000  no
  room_margin               9.36    -10 -0.000      15 +0.000  no
  aggr_early                 0.0      0 +0.000      20 +0.000  no
  aggr_late               25.882      0 +0.000      30 +0.000  no
  late_round                   5      1 +0.000       7 +0.000  no
  final_room_margin        -10.0    -10 +0.000      15 +0.000  no
```
