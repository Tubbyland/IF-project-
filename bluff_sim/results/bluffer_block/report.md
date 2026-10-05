# The Bluffer against three tuned players (draw 2, block)

Every measure uses the same 2500 deals, each played with the Bluffer in all four seats. "Ordinary player" is a tuned player sitting in the Bluffer's seat instead (the reference). Wins count ties and shared wins for every winner.

| Stage | Bluffer solo wins | Same plan, no lies | Value of lying | Ordinary player solo | Bluffer any win | Ordinary player any win | Each opponent any win |
|---|---|---|---|---|---|---|---|
| start (untuned Bluffer) | 7.3% | 7.6% | -0.3% | 0.1% | 17.8% | 49.5% | 48.3% |
| B1 | 21.2% | 6.9% | +14.3% | 0.1% | 29.4% | 49.5% | 41.8% |
| O1 | 24.8% | 19.9% | +4.9% | 2.4% | 58.7% | 82.2% | 47.0% |
| B2 | 45.2% | 45.5% | -0.3% | 2.4% | 75.7% | 82.2% | 33.0% |
| O2 | 19.0% | 19.2% | -0.2% | 4.1% | 69.8% | 76.9% | 55.5% |
| B3 | 49.6% | 17.5% | +32.0% | 4.1% | 62.3% | 76.9% | 24.5% |

## Final Bluffer

- Creeps up to 5 a round toward its side, staying 1 behind whoever is furthest from zero and never past 16 before its burst.
- Bursts for the threshold from round 3 (always in the final round), accepting 3 of tally room.
- While creeping, says "close" 0% of the time whatever it played.
- When bursting, lies 100% of the time, claiming "lower" (or "higher") in the opposite direction.
- Gives 96% weight to closing the group gap while creeping.
- Does not save extreme cards for the burst.
- Blocks threats when worth 20+ (weight 1.09, watching anyone within 11 of the threshold).

## Final opponents

- Commits to a solo win once its track is 21+ from zero.
- When chasing it, drifts up to 1 a round before round 6, then up to 28.
- Will drift 2 past the point where the tally is projected to bust.
- Anchors at zero when it is closest to zero and someone is 17+ further out.
- Gives 47% weight to closing the group's gap (42% in the final round).
- Lies on 51% of clues, by 1 band.
- Believes others' clues 77%.
- Vetoes when the steal is worth 1+ to its goal (2+ in the final round); counts blocking a leader at 107% of its size.
- Prefers playing few cards.
- Hoards very high and very low cards.
- Also blocks any player it expects to end the round within 15 of the solo threshold, leader or not.
- In the final round, goes for the solo win if its track is 19+ from zero, keeping -4 of tally room.

## How the final Bluffer's games go (Bluffer in seat 1, 6000 games)

- Solo win rate: 50.2%
- Share of its clues that are lies: 53%
- Burst rounds per game: 2.65; blocked in 3% of them

Search log:

```
Rule: draw 2, block. Opponents start from results/veto_block.
  start (untuned Bluffer): bluffer solo 0.073 (no-lie twin 0.076, ordinary player 0.002); bluffer any win 0.178; opponents 0.483
B1: tuning the Bluffer
  generation 1/10: best 0.145  mean 0.087
  generation 2/10: best 0.179  mean 0.122
  generation 3/10: best 0.188  mean 0.146
  generation 4/10: best 0.182  mean 0.147
  generation 5/10: best 0.178  mean 0.155
  generation 6/10: best 0.181  mean 0.159
  generation 7/10: best 0.210  mean 0.185
  generation 8/10: best 0.187  mean 0.170
  generation 9/10: best 0.203  mean 0.188
  generation 10/10: best 0.211  mean 0.198
  validated on 1250 new games: best 0.190 (default parameters 0.073)
  B1: bluffer solo 0.212 (no-lie twin 0.069, ordinary player 0.002); bluffer any win 0.294; opponents 0.418
O1: re-tuning the three opponents
  generation 1/10: best 0.433  mean 0.289
  generation 2/10: best 0.432  mean 0.334
  generation 3/10: best 0.462  mean 0.382
  generation 4/10: best 0.472  mean 0.409
  generation 5/10: best 0.457  mean 0.440
  generation 6/10: best 0.472  mean 0.439
  generation 7/10: best 0.487  mean 0.455
  generation 8/10: best 0.490  mean 0.451
  generation 9/10: best 0.502  mean 0.464
  generation 10/10: best 0.483  mean 0.428
  validated on 1250 new games: best 0.469 (default parameters 0.209)
  O1: bluffer solo 0.248 (no-lie twin 0.199, ordinary player 0.024); bluffer any win 0.587; opponents 0.470
B2: tuning the Bluffer
  generation 1/10: best 0.388  mean 0.224
  generation 2/10: best 0.425  mean 0.299
  generation 3/10: best 0.425  mean 0.362
  generation 4/10: best 0.417  mean 0.348
  generation 5/10: best 0.432  mean 0.394
  generation 6/10: best 0.421  mean 0.380
  generation 7/10: best 0.462  mean 0.399
  generation 8/10: best 0.467  mean 0.420
  generation 9/10: best 0.472  mean 0.426
  generation 10/10: best 0.490  mean 0.426
  validated on 1250 new games: best 0.458 (default parameters 0.374)
  B2: bluffer solo 0.453 (no-lie twin 0.455, ordinary player 0.024); bluffer any win 0.757; opponents 0.330
O2: re-tuning the three opponents
  generation 1/10: best 0.399  mean 0.300
  generation 2/10: best 0.427  mean 0.348
  generation 3/10: best 0.493  mean 0.392
  generation 4/10: best 0.481  mean 0.416
  generation 5/10: best 0.503  mean 0.429
  generation 6/10: best 0.541  mean 0.458
  generation 7/10: best 0.507  mean 0.475
  generation 8/10: best 0.534  mean 0.495
  generation 9/10: best 0.536  mean 0.508
  generation 10/10: best 0.544  mean 0.504
  validated on 1250 new games: best 0.567 (default parameters 0.304)
  O2: bluffer solo 0.190 (no-lie twin 0.192, ordinary player 0.041); bluffer any win 0.699; opponents 0.555
B3: tuning the Bluffer
  generation 1/10: best 0.388  mean 0.234
  generation 2/10: best 0.412  mean 0.297
  generation 3/10: best 0.462  mean 0.364
  generation 4/10: best 0.453  mean 0.403
  generation 5/10: best 0.463  mean 0.426
  generation 6/10: best 0.475  mean 0.432
  generation 7/10: best 0.490  mean 0.475
  generation 8/10: best 0.474  mean 0.451
  generation 9/10: best 0.509  mean 0.478
  generation 10/10: best 0.460  mean 0.446
  validated on 1250 new games: best 0.490 (default parameters 0.298)
  B3: bluffer solo 0.496 (no-lie twin 0.175, ordinary player 0.041); bluffer any win 0.623; opponents 0.245
done in 18 min
```
