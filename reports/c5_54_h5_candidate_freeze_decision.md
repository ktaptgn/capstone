# C5.54 H5 Candidate Freeze Decision

## Why This Decision Is Needed

C5.54 sensitivity narrowed `H4_BALANCED_RR_GUARD` to two viable settings. The remaining decision is not whether the policy can beat H4, but which setting should become the default H5 candidate without hiding fallback dependence.

## Sensitivity Recap

- `0.90/base` beat H4 and `BALANCED_RR_H4_PM` in all S2 regimes.
- `0.85/strict` also beat H4 and `BALANCED_RR_H4_PM` in all S2 regimes.
- `0.85/strict` has better high-demand TCO, but materially higher guard skips and fallback-to-H4.
- Route guard violations remained zero, so the route guard is non-binding under current regimes.

## Candidate Comparison Table

| threshold | risk | regime | soft TCO v4 | hard TCO v3 | eff fulfillment | eff output | HHI | max route share | hard h | soft h | failure | CM | downtime h | PM | skips/load | fallback/load | route viol/load | shovel viol/load | crusher viol/load | risk viol/load | dominant |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 0.90 | base | heterogeneous_condition | 5454.5 | 5454.2 | 0.990 | 5240914.0 | 0.174 | 0.224 | 0.00 | 0.64 | 0.0 | 0.0 | 2455.5 | 705.0 | 4.427 | 0.360 | 0.000 | 1.873 | 1.085 | 2.192 | risk |
| 0.90 | base | high_stress | 7616.7 | 7616.4 | 0.991 | 5241929.0 | 0.174 | 0.224 | 0.00 | 0.62 | 0.0 | 0.0 | 3501.8 | 865.7 | 4.338 | 0.353 | 0.000 | 1.839 | 1.062 | 2.145 | risk |
| 0.90 | base | high_demand_high_stress | 8883.4 | 8878.9 | 0.992 | 6023433.5 | 0.174 | 0.229 | 0.12 | 9.17 | 15.3 | 15.3 | 4075.3 | 805.0 | 4.983 | 0.566 | 0.000 | 3.143 | 2.530 | 1.841 | shovel |
| 0.85 | strict | heterogeneous_condition | 5478.6 | 5478.4 | 0.991 | 5243924.0 | 0.174 | 0.226 | 0.00 | 0.45 | 0.0 | 0.0 | 2477.4 | 710.8 | 7.481 | 0.730 | 0.000 | 3.282 | 0.643 | 4.380 | risk |
| 0.85 | strict | high_stress | 7623.9 | 7623.7 | 0.991 | 5244095.5 | 0.174 | 0.226 | 0.00 | 0.44 | 0.0 | 0.0 | 3511.9 | 864.0 | 7.323 | 0.714 | 0.000 | 3.213 | 0.625 | 4.288 | risk |
| 0.85 | strict | high_demand_high_stress | 8817.6 | 8813.5 | 0.993 | 6030202.5 | 0.175 | 0.228 | 0.07 | 8.33 | 14.1 | 14.1 | 4069.3 | 807.9 | 7.204 | 0.843 | 0.000 | 4.016 | 2.557 | 3.682 | shovel |

## Pairwise Differences

`strict - base` is shown below. Negative TCO means `0.85/strict` is lower cost; positive fallback means more fallback dependence.

| regime | TCO v4 diff | eff fulfillment diff | failure diff | CM diff | downtime h diff | hard h diff | soft h diff | fallback/load diff | H4 TCO margin, base | RR TCO margin, base | H4 TCO margin, strict | RR TCO margin, strict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| heterogeneous_condition | 24.1 | 0.0006 | 0.0 | 0.0 | 21.9 | 0.00 | -0.19 | 0.369 | 320.5 | 116.4 | 296.3 | 92.3 |
| high_stress | 7.1 | 0.0004 | 0.0 | 0.0 | 10.1 | -0.00 | -0.18 | 0.361 | 347.6 | 150.6 | 340.5 | 143.5 |
| high_demand_high_stress | -65.8 | 0.0011 | -1.2 | -1.2 | -6.0 | -0.05 | -0.84 | 0.277 | 185.7 | 21.6 | 251.6 | 87.4 |

## Decision

- Recommended default H5 candidate setting: `H4_BALANCED_RR_GUARD`, `soft_utilization_threshold = 0.90`, `risk_guard_level = base`.
- Recommended aggressive alternative: `soft_utilization_threshold = 0.85`, `risk_guard_level = strict`.
- Reason: `0.85/strict` is lower TCO in `high_demand_high_stress`, but it is not consistently lower TCO in the two lower-stress regimes and it roughly doubles fallback/load versus `0.90/base` in normal regimes.
- `0.90/base` keeps the all-regime win over both H4 and the audit comparator while preserving cleaner interpretability and lower fallback dependence.
- Route violation equals zero for both settings in all regimes. This means the route guard is not currently binding; the active decision surface is shovel/risk/crusher guard plus fallback.

## H5 Naming

H5 naming is now justified as a next implementation step, with `0.90/base` as the default candidate. This report does not create H5 and does not modify prior C5 modules.

## Next Command

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; python -B scripts\run_c5_54_guard_sensitivity.py --stage s2 --s2-settings 0.90:base,0.85:strict
```
