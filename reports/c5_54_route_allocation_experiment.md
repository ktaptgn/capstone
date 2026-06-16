# C5.54 Route Allocation Experiment

## Why C5.54 Was Needed

C5.53 showed that H4 is the strongest official H0-H4 policy under hard and soft congestion, while the audit-only `BALANCED_RR_H4_PM` comparator beat H4 in all regimes. C5.54 tests whether that comparator signal can be converted into an official guarded route-allocation candidate without creating H5.

## Why H5 Is Premature

This is still a route-allocation experiment. `BALANCED_RR_H4_PM` is not a final policy, and `H4_BALANCED_RR_GUARD` must prove robustness across regimes before any H5 naming.

## C5.53 Soft-Threshold Recap

- `total_tco_v3_hard` preserves hard-threshold congestion.
- `total_tco_v4_soft_congestion` adds near-capacity pressure.
- H4 remained best among official H0-H4 policies.
- `BALANCED_RR_H4_PM` beat H4 but remained synthetic and unguarded.

## H4_BALANCED_RR_GUARD Definition

The first official C5.54 candidate keeps H4's `flow_backpressure` PM family and rotates through this balanced route order:

```text
R_A1, R_B1, R_C1, R_A2, R_B2, R_C2
```

A route is skipped if route, shovel, or crusher utilization exceeds `0.90`, or if route risk exceeds the current risk guard. If all routes violate guards, the policy falls back to existing H4 route scoring.

## Stage 2 - 90-Day Robustness Result

Command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; python scripts\run_c5_54_sweep.py --days 90 --seeds 101,102,103,104,105,106,107,108,109,110 --regimes heterogeneous_condition,high_stress,high_demand_high_stress --policies H4,BALANCED_RR_H4_PM,H4_BALANCED_RR_GUARD --no-event-log
```

Scope: 90 days, 10 seeds, 3 regimes, 3 policies. Raw summary rows: 90. Aggregated rows: 9.

### Policy x Regime Soft TCO Ranking

| regime | rank | policy | soft TCO v4 | effective fulfillment | HHI | max route share | hard congestion h | soft congestion h | failures | CM | downtime h |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| heterogeneous_condition | 1 | H4_BALANCED_RR_GUARD | 5454.5 | 0.990 | 0.174 | 0.224 | 0.00 | 0.64 | 0.0 | 0.0 | 2455.5 |
| heterogeneous_condition | 2 | BALANCED_RR_H4_PM | 5570.9 | 1.000 | 0.167 | 0.169 | 0.10 | 5.04 | 0.0 | 0.0 | 2691.7 |
| heterogeneous_condition | 3 | H4 | 5775.0 | 0.993 | 0.175 | 0.214 | 0.00 | 0.35 | 0.0 | 0.0 | 2659.5 |
| high_demand_high_stress | 1 | H4_BALANCED_RR_GUARD | 8883.4 | 0.992 | 0.174 | 0.229 | 0.12 | 9.17 | 15.3 | 15.3 | 4075.3 |
| high_demand_high_stress | 2 | BALANCED_RR_H4_PM | 8905.0 | 1.000 | 0.167 | 0.168 | 1.22 | 24.27 | 20.4 | 20.4 | 4242.3 |
| high_demand_high_stress | 3 | H4 | 9069.2 | 0.994 | 0.173 | 0.228 | 0.02 | 7.35 | 17.6 | 17.6 | 4201.7 |
| high_stress | 1 | H4_BALANCED_RR_GUARD | 7616.7 | 0.991 | 0.174 | 0.224 | 0.00 | 0.62 | 0.0 | 0.0 | 3501.8 |
| high_stress | 2 | BALANCED_RR_H4_PM | 7767.4 | 1.000 | 0.167 | 0.169 | 0.11 | 5.09 | 0.4 | 0.4 | 3736.7 |
| high_stress | 3 | H4 | 7964.3 | 0.993 | 0.175 | 0.214 | 0.00 | 0.35 | 0.4 | 0.4 | 3709.3 |

### Guard Behavior and Normalized Rates

| regime | policy | completed loads | guard skips/load | fallback/load | route viol/load | shovel viol/load | crusher viol/load | risk viol/load | dominant guard |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| heterogeneous_condition | H4 | 18900 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | none |
| heterogeneous_condition | BALANCED_RR_H4_PM | 18900 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | none |
| heterogeneous_condition | H4_BALANCED_RR_GUARD | 18900 | 4.427 | 0.360 | 0.000 | 1.873 | 1.085 | 2.192 | risk |
| high_demand_high_stress | H4 | 21690 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | none |
| high_demand_high_stress | BALANCED_RR_H4_PM | 21690 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | none |
| high_demand_high_stress | H4_BALANCED_RR_GUARD | 21690 | 4.983 | 0.566 | 0.000 | 3.143 | 2.530 | 1.841 | shovel |
| high_stress | H4 | 18900 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | none |
| high_stress | BALANCED_RR_H4_PM | 18900 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | none |
| high_stress | H4_BALANCED_RR_GUARD | 18900 | 4.338 | 0.353 | 0.000 | 1.839 | 1.062 | 2.145 | risk |

### Key Questions

1. Does `H4_BALANCED_RR_GUARD` beat H4 under soft TCO v4 in all regimes? yes.
2. Does it beat `BALANCED_RR_H4_PM` in all regimes? yes.
3. Does it avoid hard congestion spikes? yes.
4. Does it avoid failure/CM/downtime increase? Failure/CM: yes. Downtime should be read by regime in the ranking table.
5. Does it maintain effective fulfillment near or above 0.99? yes.
6. Are guard/fallback counts interpretable? They are high but interpretable: the policy actively filters route choices and falls back to H4 rather than forcing guarded routes.
7. Which guard dominates route selection? Risk and shovel guards dominate depending on regime; route guard does not bind.
8. Does route_violation = 0 remain true in Stage 2? yes.
9. If route violations remain 0, should route guard be relaxed/removed or kept? Keep it for future high-demand stress tests; it is not binding now but protects extrapolated scenarios.
10. Is H5 justified after Stage 2? close, but sensitivity validation is still required before naming H5.

## Interpretation

`H4_BALANCED_RR_GUARD` is a strong H5 candidate after Stage 2, but H5 naming still requires sensitivity validation.

## Recommended Next Step

Run a threshold/risk-guard sensitivity on `H4_BALANCED_RR_GUARD` before creating H5.
