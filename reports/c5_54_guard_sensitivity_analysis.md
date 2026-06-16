# C5.54 Guard Sensitivity Analysis

## Why This Sensitivity Was Needed

`H4_BALANCED_RR_GUARD` won the Stage 2 base run, but guard skips and H4 fallback were active. This analysis checks whether that win is robust to utilization threshold and risk-guard settings before any H5 naming.

## Stage 2 Base Recap

- Base setting: `soft_utilization_threshold = 0.90`, `risk_guard_level = base`, percentile `0.90`.
- Stage 2 base ranking was `H4_BALANCED_RR_GUARD`, then `BALANCED_RR_H4_PM`, then `H4` in all regimes.
- Base guard behavior had high skip/fallback activity, route violations at zero, and risk/shovel guard dominance.

## Execution Scope

- Raw sensitivity summary rows found: 441.
- S1 aggregated rows: 27.
- S2 aggregated rows: 36.

## S1 Threshold and Risk-Guard Screening

| threshold | risk | guard soft TCO | eff fulfillment | rank | guard skips/load | fallback/load | dominant guard |
|---:|---|---:|---:|---:|---:|---:|---|
| 0.85 | base | 1288.0 | 0.995 | 1 | 4.986 | 0.452 | shovel |
| 0.85 | relaxed | 1288.0 | 0.995 | 1 | 4.986 | 0.452 | shovel |
| 0.85 | strict | 1351.5 | 0.991 | 1 | 7.560 | 0.737 | risk |
| 0.90 | base | 1328.3 | 0.990 | 1 | 4.463 | 0.361 | risk |
| 0.90 | relaxed | 1328.3 | 0.990 | 1 | 4.463 | 0.361 | risk |
| 0.90 | strict | 1370.2 | 0.988 | 1 | 7.259 | 0.678 | risk |
| 0.95 | base | 1388.7 | 0.983 | 1 | 3.970 | 0.267 | risk |
| 0.95 | relaxed | 1388.7 | 0.983 | 1 | 3.970 | 0.267 | risk |
| 0.95 | strict | 1417.1 | 0.983 | 1 | 6.937 | 0.607 | risk |

## S2 TCO v4 Ranking by Setting and Regime

| threshold | risk | regime | rank | policy | soft TCO v4 | eff fulfillment | hard h | soft h | failure | CM | downtime h |
|---:|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0.85 | base | heterogeneous_condition | 1 | H4_BALANCED_RR_GUARD | 5345.7 | 0.995 | 0.00 | 0.34 | 0.0 | 0.0 | 2484.4 |
| 0.85 | base | heterogeneous_condition | 2 | BALANCED_RR_H4_PM | 5570.9 | 1.000 | 0.10 | 5.04 | 0.0 | 0.0 | 2691.7 |
| 0.85 | base | heterogeneous_condition | 3 | H4 | 5775.0 | 0.993 | 0.00 | 0.35 | 0.0 | 0.0 | 2659.5 |
| 0.85 | base | high_demand_high_stress | 1 | BALANCED_RR_H4_PM | 8905.0 | 1.000 | 1.22 | 24.27 | 20.4 | 20.4 | 4242.3 |
| 0.85 | base | high_demand_high_stress | 2 | H4_BALANCED_RR_GUARD | 8906.7 | 0.990 | 0.18 | 10.47 | 13.6 | 13.6 | 4051.1 |
| 0.85 | base | high_demand_high_stress | 3 | H4 | 9069.2 | 0.994 | 0.02 | 7.35 | 17.6 | 17.6 | 4201.7 |
| 0.85 | base | high_stress | 1 | H4_BALANCED_RR_GUARD | 7509.6 | 0.995 | 0.00 | 0.35 | 0.0 | 0.0 | 3529.9 |
| 0.85 | base | high_stress | 2 | BALANCED_RR_H4_PM | 7767.4 | 1.000 | 0.11 | 5.09 | 0.4 | 0.4 | 3736.7 |
| 0.85 | base | high_stress | 3 | H4 | 7964.3 | 0.993 | 0.00 | 0.35 | 0.4 | 0.4 | 3709.3 |
| 0.85 | relaxed | heterogeneous_condition | 1 | H4_BALANCED_RR_GUARD | 5345.7 | 0.995 | 0.00 | 0.34 | 0.0 | 0.0 | 2484.4 |
| 0.85 | relaxed | heterogeneous_condition | 2 | BALANCED_RR_H4_PM | 5570.9 | 1.000 | 0.10 | 5.04 | 0.0 | 0.0 | 2691.7 |
| 0.85 | relaxed | heterogeneous_condition | 3 | H4 | 5775.0 | 0.993 | 0.00 | 0.35 | 0.0 | 0.0 | 2659.5 |
| 0.85 | relaxed | high_demand_high_stress | 1 | BALANCED_RR_H4_PM | 8905.0 | 1.000 | 1.22 | 24.27 | 20.4 | 20.4 | 4242.3 |
| 0.85 | relaxed | high_demand_high_stress | 2 | H4_BALANCED_RR_GUARD | 8906.7 | 0.990 | 0.18 | 10.47 | 13.6 | 13.6 | 4051.1 |
| 0.85 | relaxed | high_demand_high_stress | 3 | H4 | 9069.2 | 0.994 | 0.02 | 7.35 | 17.6 | 17.6 | 4201.7 |
| 0.85 | relaxed | high_stress | 1 | H4_BALANCED_RR_GUARD | 7509.6 | 0.995 | 0.00 | 0.35 | 0.0 | 0.0 | 3529.9 |
| 0.85 | relaxed | high_stress | 2 | BALANCED_RR_H4_PM | 7767.4 | 1.000 | 0.11 | 5.09 | 0.4 | 0.4 | 3736.7 |
| 0.85 | relaxed | high_stress | 3 | H4 | 7964.3 | 0.993 | 0.00 | 0.35 | 0.4 | 0.4 | 3709.3 |
| 0.85 | strict | heterogeneous_condition | 1 | H4_BALANCED_RR_GUARD | 5478.6 | 0.991 | 0.00 | 0.45 | 0.0 | 0.0 | 2477.4 |
| 0.85 | strict | heterogeneous_condition | 2 | BALANCED_RR_H4_PM | 5570.9 | 1.000 | 0.10 | 5.04 | 0.0 | 0.0 | 2691.7 |
| 0.85 | strict | heterogeneous_condition | 3 | H4 | 5775.0 | 0.993 | 0.00 | 0.35 | 0.0 | 0.0 | 2659.5 |
| 0.85 | strict | high_demand_high_stress | 1 | H4_BALANCED_RR_GUARD | 8817.6 | 0.993 | 0.07 | 8.33 | 14.1 | 14.1 | 4069.3 |
| 0.85 | strict | high_demand_high_stress | 2 | BALANCED_RR_H4_PM | 8905.0 | 1.000 | 1.22 | 24.27 | 20.4 | 20.4 | 4242.3 |
| 0.85 | strict | high_demand_high_stress | 3 | H4 | 9069.2 | 0.994 | 0.02 | 7.35 | 17.6 | 17.6 | 4201.7 |
| 0.85 | strict | high_stress | 1 | H4_BALANCED_RR_GUARD | 7623.9 | 0.991 | 0.00 | 0.44 | 0.0 | 0.0 | 3511.9 |
| 0.85 | strict | high_stress | 2 | BALANCED_RR_H4_PM | 7767.4 | 1.000 | 0.11 | 5.09 | 0.4 | 0.4 | 3736.7 |
| 0.85 | strict | high_stress | 3 | H4 | 7964.3 | 0.993 | 0.00 | 0.35 | 0.4 | 0.4 | 3709.3 |
| 0.90 | base | heterogeneous_condition | 1 | H4_BALANCED_RR_GUARD | 5454.5 | 0.990 | 0.00 | 0.64 | 0.0 | 0.0 | 2455.5 |
| 0.90 | base | heterogeneous_condition | 2 | BALANCED_RR_H4_PM | 5570.9 | 1.000 | 0.10 | 5.04 | 0.0 | 0.0 | 2691.7 |
| 0.90 | base | heterogeneous_condition | 3 | H4 | 5775.0 | 0.993 | 0.00 | 0.35 | 0.0 | 0.0 | 2659.5 |
| 0.90 | base | high_demand_high_stress | 1 | H4_BALANCED_RR_GUARD | 8883.4 | 0.992 | 0.12 | 9.17 | 15.3 | 15.3 | 4075.3 |
| 0.90 | base | high_demand_high_stress | 2 | BALANCED_RR_H4_PM | 8905.0 | 1.000 | 1.22 | 24.27 | 20.4 | 20.4 | 4242.3 |
| 0.90 | base | high_demand_high_stress | 3 | H4 | 9069.2 | 0.994 | 0.02 | 7.35 | 17.6 | 17.6 | 4201.7 |
| 0.90 | base | high_stress | 1 | H4_BALANCED_RR_GUARD | 7616.7 | 0.991 | 0.00 | 0.62 | 0.0 | 0.0 | 3501.8 |
| 0.90 | base | high_stress | 2 | BALANCED_RR_H4_PM | 7767.4 | 1.000 | 0.11 | 5.09 | 0.4 | 0.4 | 3736.7 |
| 0.90 | base | high_stress | 3 | H4 | 7964.3 | 0.993 | 0.00 | 0.35 | 0.4 | 0.4 | 3709.3 |

## S2 Guard and Fallback Rates

| threshold | risk | regime | skips/load | fallback/load | route viol/load | shovel viol/load | crusher viol/load | risk viol/load | dominant guard |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 0.85 | base | heterogeneous_condition | 4.935 | 0.453 | 0.000 | 2.480 | 1.588 | 2.191 | shovel |
| 0.85 | base | high_demand_high_stress | 5.305 | 0.624 | 0.000 | 3.556 | 2.948 | 1.843 | shovel |
| 0.85 | base | high_stress | 4.829 | 0.445 | 0.000 | 2.428 | 1.551 | 2.144 | shovel |
| 0.85 | relaxed | heterogeneous_condition | 4.935 | 0.453 | 0.000 | 2.480 | 1.588 | 2.191 | shovel |
| 0.85 | relaxed | high_demand_high_stress | 5.305 | 0.624 | 0.000 | 3.556 | 2.948 | 1.843 | shovel |
| 0.85 | relaxed | high_stress | 4.829 | 0.445 | 0.000 | 2.428 | 1.551 | 2.144 | shovel |
| 0.85 | strict | heterogeneous_condition | 7.481 | 0.730 | 0.000 | 3.282 | 0.643 | 4.380 | risk |
| 0.85 | strict | high_demand_high_stress | 7.204 | 0.843 | 0.000 | 4.016 | 2.557 | 3.682 | shovel |
| 0.85 | strict | high_stress | 7.323 | 0.714 | 0.000 | 3.213 | 0.625 | 4.288 | risk |
| 0.90 | base | heterogeneous_condition | 4.427 | 0.360 | 0.000 | 1.873 | 1.085 | 2.192 | risk |
| 0.90 | base | high_demand_high_stress | 4.983 | 0.566 | 0.000 | 3.143 | 2.530 | 1.841 | shovel |
| 0.90 | base | high_stress | 4.338 | 0.353 | 0.000 | 1.839 | 1.062 | 2.145 | risk |

## Interpretation

- Best TCO-robust setting in S2: threshold `0.85`, risk `strict`.
- `0.85/base` and `0.85/relaxed` improve normal-regime TCO but are not fully robust because `BALANCED_RR_H4_PM` remains slightly lower in `high_demand_high_stress`.
- `0.90/base` remains a cleaner conservative reference: it beats both comparators in all S2 regimes with lower fallback dependence than `0.85/strict`.
- `0.85/strict` beats both comparators in all S2 regimes, but its fallback rate is materially higher, so it should not be promoted without a final fallback-dependence review.
- Route violation remains zero across analyzed guard settings: yes.
- `base` and `relaxed` risk levels often produce identical outcomes under the current route-risk surface, suggesting the percentile change does not always cross an active route-order boundary.
- Risk/shovel dominance should be read by setting in the guard table; stricter risk settings are expected to increase risk-guard binding.
- H5 naming justified now: not yet; sensitivity evidence is supportive but should be reviewed before naming H5.

## Recommended Next Step

Run a final confirmation comparing threshold `0.85`/risk `strict` against threshold `0.90`/risk `base` before creating H5.
