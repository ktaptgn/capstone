# C5.55 H5 Policy Benchmark

## Why C5.55 Was Created

C5.55 freezes the C5.54 H5 candidate decision into a separate official benchmark module. It does not replace C5.4; it is a personal follow-up benchmark that preserves prior C5 modules and compares H5 against H0-H4 plus audit/sensitivity comparators.

## H5 Freeze Decision Recap

- Default H5: `H4_BALANCED_RR_GUARD`, `soft_utilization_threshold = 0.90`, `risk_guard_level = base`.
- Aggressive alternative: `H5_AGGRESSIVE`, `soft_utilization_threshold = 0.85`, `risk_guard_level = strict`.
- `BALANCED_RR_H4_PM` remains audit-only and is not official.
- `H5_AGGRESSIVE` remains a sensitivity comparator and is not the default.

## Benchmark Scope

- Raw summary rows: 270. Aggregated policy x regime rows: 27.
- Horizon: 90 days.
- Seeds: 101-110.
- Regimes: heterogeneous_condition, high_stress, high_demand_high_stress.
- Event log: disabled.

## Policy x Regime Soft TCO Ranking

| regime | rank | policy | soft TCO v4 | eff fulfillment | hard h | soft h | failure | CM | downtime h | fallback/load | dominant guard |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| heterogeneous_condition | 1 | H5 | 5454.5 | 0.990 | 0.00 | 0.64 | 0.0 | 0.0 | 2455.5 | 0.360 | risk |
| heterogeneous_condition | 2 | H5_AGGRESSIVE | 5478.6 | 0.991 | 0.00 | 0.45 | 0.0 | 0.0 | 2477.4 | 0.730 | risk |
| heterogeneous_condition | 3 | BALANCED_RR_H4_PM | 5570.9 | 1.000 | 0.10 | 5.04 | 0.0 | 0.0 | 2691.7 | 0.000 | none |
| heterogeneous_condition | 4 | H4 | 5775.0 | 0.993 | 0.00 | 0.35 | 0.0 | 0.0 | 2659.5 | 0.000 | none |
| heterogeneous_condition | 5 | H3 | 7973.1 | 0.981 | 575.13 | 3838.34 | 0.0 | 0.0 | 2583.1 | 0.000 | none |
| heterogeneous_condition | 6 | H1 | 9136.5 | 0.912 | 512.95 | 3447.62 | 0.0 | 0.0 | 1977.4 | 0.000 | none |
| heterogeneous_condition | 7 | H_TIME | 9276.7 | 1.027 | 1.51 | 27.48 | 29.8 | 29.8 | 4570.6 | 0.000 | none |
| heterogeneous_condition | 8 | H2 | 9300.0 | 0.912 | 575.13 | 3838.34 | 0.0 | 0.0 | 1970.7 | 0.000 | none |
| heterogeneous_condition | 9 | H0 | 9783.6 | 1.027 | 1.51 | 27.51 | 45.2 | 45.2 | 4805.9 | 0.000 | none |
| high_demand_high_stress | 1 | H5_AGGRESSIVE | 8817.6 | 0.993 | 0.07 | 8.33 | 14.1 | 14.1 | 4069.3 | 0.843 | shovel |
| high_demand_high_stress | 2 | H5 | 8883.4 | 0.992 | 0.12 | 9.17 | 15.3 | 15.3 | 4075.3 | 0.566 | shovel |
| high_demand_high_stress | 3 | BALANCED_RR_H4_PM | 8905.0 | 1.000 | 1.22 | 24.27 | 20.4 | 20.4 | 4242.3 | 0.000 | none |
| high_demand_high_stress | 4 | H4 | 9069.2 | 0.994 | 0.02 | 7.35 | 17.6 | 17.6 | 4201.7 | 0.000 | none |
| high_demand_high_stress | 5 | H_TIME | 11525.3 | 1.011 | 3.59 | 52.28 | 105.4 | 105.4 | 5419.1 | 0.000 | none |
| high_demand_high_stress | 6 | H0 | 11877.1 | 1.011 | 3.59 | 52.33 | 111.6 | 111.6 | 5585.5 | 0.000 | none |
| high_demand_high_stress | 7 | H3 | 13128.7 | 0.967 | 1072.34 | 6900.39 | 5.8 | 5.8 | 3974.2 | 0.000 | none |
| high_demand_high_stress | 8 | H1 | 13851.2 | 0.923 | 1000.13 | 6459.77 | 0.7 | 0.7 | 3522.3 | 0.000 | none |
| high_demand_high_stress | 9 | H2 | 14038.3 | 0.923 | 1071.61 | 6896.03 | 0.7 | 0.7 | 3509.2 | 0.000 | none |
| high_stress | 1 | H5 | 7616.7 | 0.991 | 0.00 | 0.62 | 0.0 | 0.0 | 3501.8 | 0.353 | risk |
| high_stress | 2 | H5_AGGRESSIVE | 7623.9 | 0.991 | 0.00 | 0.44 | 0.0 | 0.0 | 3511.9 | 0.714 | risk |
| high_stress | 3 | BALANCED_RR_H4_PM | 7767.4 | 1.000 | 0.11 | 5.09 | 0.4 | 0.4 | 3736.7 | 0.000 | none |
| high_stress | 4 | H4 | 7964.3 | 0.993 | 0.00 | 0.35 | 0.4 | 0.4 | 3709.3 | 0.000 | none |
| high_stress | 5 | H3 | 10106.7 | 0.981 | 575.13 | 3838.34 | 0.0 | 0.0 | 3607.5 | 0.000 | none |
| high_stress | 6 | H_TIME | 10596.8 | 1.027 | 1.54 | 27.84 | 71.4 | 71.4 | 5033.6 | 0.000 | none |
| high_stress | 7 | H0 | 11025.0 | 1.027 | 1.53 | 27.72 | 82.2 | 82.2 | 5226.6 | 0.000 | none |
| high_stress | 8 | H1 | 11221.0 | 0.912 | 530.47 | 3558.51 | 0.0 | 0.0 | 2955.1 | 0.000 | none |
| high_stress | 9 | H2 | 11338.5 | 0.912 | 575.13 | 3838.34 | 0.0 | 0.0 | 2947.5 | 0.000 | none |

## H5 Pairwise Comparisons

| regime | H5 vs H4 TCO margin | H5 vs BALANCED_RR_H4_PM margin | H5_AGGRESSIVE vs H5 margin | H5 eff fulfillment | H5 failure/CM | H5 downtime h | H5 hard/soft h | H5 fallback/load |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| heterogeneous_condition | 320.5 | 116.4 | -24.1 | 0.990 | 0.0/0.0 | 2455.5 | 0.00/0.64 | 0.360 |
| high_demand_high_stress | 185.7 | 21.6 | 65.8 | 0.992 | 15.3/15.3 | 4075.3 | 0.12/9.17 | 0.566 |
| high_stress | 347.6 | 150.6 | -7.1 | 0.991 | 0.0/0.0 | 3501.8 | 0.00/0.62 | 0.353 |

## H5 vs H1/H2 Reliability Frontier

| regime | H1 failure/CM | H2 failure/CM | H5 failure/CM | H1 soft TCO | H2 soft TCO | H5 soft TCO |
|---|---:|---:|---:|---:|---:|---:|
| heterogeneous_condition | 0.0/0.0 | 0.0/0.0 | 0.0/0.0 | 9136.5 | 9300.0 | 5454.5 |
| high_demand_high_stress | 0.7/0.7 | 0.7/0.7 | 15.3/15.3 | 13851.2 | 14038.3 | 8883.4 |
| high_stress | 0.0/0.0 | 0.0/0.0 | 0.0/0.0 | 11221.0 | 11338.5 | 7616.7 |

## Interpretation

- H5 beats H4 in all regimes: yes.
- H5 beats `BALANCED_RR_H4_PM` in all regimes: yes.
- H5_AGGRESSIVE beats H5 in: high_demand_high_stress.
- H5 minimum effective fulfillment across regimes: 0.990.
- Route guard violation remains zero for H5/H5_AGGRESSIVE: yes.
- H5 has explicit guard/fallback behavior; fallback dependence should be presented as part of the policy, not hidden as a pure route-balancing win.
- H1/H2 can still be interpreted as reliability-focused policies when their failure/CM profile is competitive, but H5 is the production-congestion benchmark in this experiment.

## Presentation Readiness

H5 is robust enough for the personal presentation under this 90-day benchmark, with the limitation that C5.55 is a follow-up experiment and does not replace the team C5.4 result.

## Limitations

- The route guard remains non-binding in these regimes, so shovel/risk/crusher guards and fallback drive most H5 behavior.
- The benchmark uses the C5.53 proxy cycle-time and soft-congestion model, not calibrated site measurements.
- `H5_AGGRESSIVE` is useful for stress sensitivity but should not be treated as the default policy.
