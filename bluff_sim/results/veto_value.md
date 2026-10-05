# Is vetoing a winning strategy? (draw 2)

20000 games per cell, same deals within each rule. Win score: share of games won by the seat (ties count for each tied winner; shared wins count).

## A. Against the fixed bots

Tuned seats 3-4 with their vetoing switched on and off. Differences under about 0.007 are noise.

| Rule | Tuned, vetoing | Same strategy, never vetoes | Value of vetoing |
|---|---|---|---|
| no veto | 0.358 | — | — |
| take (current) | 0.370 | 0.346 | +0.024 |
| block | 0.482 | 0.333 | +0.149 |
| choose | 0.485 | 0.334 | +0.151 |
| pay 1 card | 0.358 | 0.346 | +0.012 |

## B. When everyone plays the tuned strategy

Field of four copies. A positive change means the deviant gains by breaking from the field.

| Rule | Vetoing field, own score | One non-vetoer in it | Non-vetoing field, own score | One vetoer in it |
|---|---|---|---|---|
| take (current) | 0.497 | 0.496 (-0.002) | 0.494 | 0.500 (+0.006) |
| block | 0.506 | 0.506 (+0.000) | 0.496 | 0.503 (+0.007) |
| choose | 0.509 | 0.508 (-0.001) | 0.498 | 0.506 (+0.008) |
| pay 1 card | 0.486 | 0.484 (-0.002) | 0.480 | 0.486 (+0.006) |

## How the tuned seats use the veto (against the fixed bots)

| Rule | Vetoes per game (seats 3-4) | Vetoes that decided the game, per game | Targets | Careful drifter wins | Anchor wins |
|---|---|---|---|---|---|
| take (current) | 0.32 | 0.023 | anchor 11%, careful_drifter 75%, tuned 14% | 22.4% | 53.0% |
| block | 3.25 | 0.104 | anchor 1%, careful_drifter 74%, tuned 25% | 11.9% | 68.2% |
| choose | 3.26 | 0.118 | anchor 1%, careful_drifter 75%, tuned 24% | 12.1% | 68.1% |
| pay 1 card | 0.12 | 0.014 | anchor 8%, careful_drifter 85%, tuned 7% | 23.8% | 49.0% |
