# Shortlisted rule sets with tuned players

Rule files: configs/candidates/A-D.yaml. Personal targets 10-20 throughout. Output of scripts comparing each report:

```
== A: tuned 0.459 default 0.334 | Converging: champions changed 1 time(s) and the last challenger could 
  1_best_response  17.6/47.8/34.6 len 5.34 reach 67% half 38.5% last 32.7% lead 1.61
  2_self_play      13.6/36.4/50.0 len 5.68 reach 79% half 51.9% last 29.1% lead 2.99
  matters: solo_at, help_weight, trust, veto_threshold, deny_weight, card_cost, final_solo_at, danger_margin, final_veto_threshold, lie_size, lie_rate
  fixed bots: [('careful_drifter', '45.6%'), ('anchor', '68.3%')]
== B: tuned 0.507 default 0.389 | Cycling: earlier champions beat later ones on their own ground (C0 bea
  1_best_response  37.9/28.1/34.0 len 4.55 reach 76% half 46.2% last 42.5% lead 1.54
  2_self_play      43.7/18.8/37.6 len 4.49 reach 75% half 49.9% last 37.8% lead 2.09
  matters: trust, final_help_weight, help_weight, solo_at, veto_threshold, deny_weight
  fixed bots: [('careful_drifter', '47.2%'), ('anchor', '57.4%')]
== C: tuned 0.339 default 0.246 | Converging: champions changed 1 time(s) and the last challenger could 
  1_best_response  43.2/44.5/12.2 len 4.49 reach 63% half 47.6% last 50.7% lead 1.86
  2_self_play      56.3/24.9/18.8 len 4.86 reach 88% half 70.3% last 69.4% lead 2.76
  matters: card_cost, veto_threshold, trust, deny_weight, final_help_weight, lie_rate, lie_size
  fixed bots: [('careful_drifter', '30.1%'), ('anchor', '43.4%')]
== D: tuned 0.625 default 0.350 | Still moving: the last iteration was accepted with parameter moves 0.1
  1_best_response  29.8/15.9/54.3 len 4.59 reach 80% half 30.1% last 25.2% lead 1.20
  2_self_play      1.1/2.3/96.5 len 4.96 reach 98% half 23.2% last 1.2% lead 2.51
  matters: help_weight, trust, deny_weight, final_veto_threshold, veto_threshold, final_help_weight, lie_rate, final_solo_at, card_cost, danger_margin, solo_at, extreme_cost
  fixed bots: [('careful_drifter', '72.3%'), ('anchor', '68.7%')]
```

Columns: solo/bust/shared %, average length, % reaching the last round, % of outright wins by a player behind at halfway, % of games won outright in the last round, lead changes per game. "matters" lists parameters whose bounds move the win score beyond noise.
