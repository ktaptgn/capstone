# C5.53 H4 Zero-Congestion Audit

## Scope

This audit checks whether H4 zero or near-zero congestion in C5.53 is caused by a calculation/logging omission or by the current congestion threshold. It does not modify C5.4, C5.5, C5.51, C5.52, or C5.53 simulator logic.

Current audited data sources:

- Summary CSV: `outputs\c5_53\summary\c5_53_policy_comparison.csv` (300 rows).
- Daily CSV: `outputs\c5_53\logs\c5_53_daily_summary.csv` (27000 rows).
- Dispatch event CSV: `outputs\c5_53\logs\c5_53_dispatch_events.csv` (30 day event-log scope; used only for step-level field confirmation).

## Code Path Finding

- H4 is a normal `run_policy_simulation(...)` policy path. The simulator creates `policy = create_congestion_policy(policy_id, config)` and then uses the same dispatch/congestion block for all policies.
- H4 only changes route ranking through `H4RouteFlowDispatch.route_score`, which scores capacity minus queue penalty. There is no H4-specific bypass around `_queue_delay(...)`, utilization logging, route assignment, or daily load recording.
- The active formula is a hard threshold: `_queue_delay(utilization, alpha, beta)` returns `0.0` when `utilization <= 1.0` and applies `alpha * (utilization - 1.0) ** beta` only above 1.0.
- Utilization in the event log is computed from same-day preferred-route/facility attempt counts divided by daily capacity. It is cumulative within the day, not a rolling hourly occupancy model.

## H4 90-Day Summary by Regime

| regime | mean congestion h | max seed congestion h | mean TCO v3 | mean HHI | mean max route share | mean effective fulfillment |
|---|---:|---:|---:|---:|---:|---:|
| heterogeneous_condition | 0.000 | 0.000 | 5774.8 | 0.175 | 0.214 | 0.993 |
| high_demand_high_stress | 0.023 | 0.029 | 9065.5 | 0.173 | 0.228 | 0.994 |
| high_stress | 0.000 | 0.000 | 7964.2 | 0.175 | 0.214 | 0.993 |

## H4 Daily Utilization Peaks

The table below uses daily summary loads and preferred-route/facility attempts. Assigned utilization confirms route load recording; attempt utilization is the same basis used by the congestion formula.

| regime | max assigned route util | max preferred route util | max assigned shovel util | max preferred shovel util | max assigned crusher util | max preferred crusher util | mean daily route peak attempt |
|---|---:|---:|---:|---:|---:|---:|---:|
| heterogeneous_condition | 0.600 | 0.600 | 0.960 | 0.960 | 0.900 | 0.900 | 0.600 |
| high_demand_high_stress | 0.671 | 0.671 | 1.071 | 1.083 | 1.063 | 1.074 | 0.671 |
| high_stress | 0.600 | 0.600 | 0.960 | 0.960 | 0.900 | 0.900 | 0.600 |

### H4 Preferred Attempt Utilization Detail

| regime | route attempt peaks | shovel attempt peaks | crusher attempt peaks |
|---|---|---|
| heterogeneous_condition | R_A1 0.466, R_A2 0.529, R_B1 0.435, R_B2 0.600, R_C1 0.455, R_C2 0.549 | SHOVEL_A 0.875, SHOVEL_B 0.960, SHOVEL_C 0.893 | CRUSHER_1 0.884, CRUSHER_2 0.900 |
| high_demand_high_stress | R_A1 0.569, R_A2 0.647, R_B1 0.532, R_B2 0.600, R_C1 0.545, R_C2 0.671 | SHOVEL_A 1.069, SHOVEL_B 1.040, SHOVEL_C 1.083 | CRUSHER_1 1.074, CRUSHER_2 1.029 |
| high_stress | R_A1 0.466, R_A2 0.529, R_B1 0.435, R_B2 0.600, R_C1 0.470, R_C2 0.549 | SHOVEL_A 0.875, SHOVEL_B 0.960, SHOVEL_C 0.905 | CRUSHER_1 0.895, CRUSHER_2 0.900 |

## Step-Level / Event-Log Check

The available event log covers day 1-30 for regimes `heterogeneous_condition` and policies `H0, H1, H1_original, H1_value_guard, H2, H2_original, H2_value_guard, H3, H4, H_TIME`. It is not a full 90-day event log, but it confirms that H4 event rows include route, shovel, and crusher utilization fields.

| event-log scope | H4 event rows | H4 max route util after | H4 max shovel util after | H4 max crusher util after |
|---|---:|---:|---:|---:|
| existing dispatch log | 18900 | 0.600 | 0.960 | 0.900 |

Because the simulator utilization counter is daily cumulative, the daily preferred-attempt maxima above are also the end-of-day event-level peak for a complete event log. There is no separate rolling hourly utilization state in the current C5.53 model.

## H4 Route Load Recording Check

| regime | mean H4 route loads per 90-day run | total assigned route loads | completed loads | route load match |
|---|---|---:|---:|---|
| heterogeneous_condition | R_A1 2430, R_A2 3240, R_B1 2430, R_B2 4050, R_C1 2700, R_C2 4050 | 18900 | 18900 | yes |
| high_demand_high_stress | R_A1 2967, R_A2 3878, R_B1 2968, R_B2 3957, R_C1 2974, R_C2 4946 | 21690 | 21690 | yes |
| high_stress | R_A1 2430, R_A2 3240, R_B1 2430, R_B2 4050, R_C1 2700, R_C2 4050 | 18900 | 18900 | yes |

## H1/H2/H3 vs H4 Congestion Path

| regime | policy | mean congestion h | mean HHI | mean max route share | mean TCO v3 |
|---|---|---:|---:|---:|---:|
| heterogeneous_condition | H1 | 513.0 | 0.298 | 0.390 | 7669.2 |
| heterogeneous_condition | H2 | 575.1 | 0.337 | 0.388 | 7668.4 |
| heterogeneous_condition | H3 | 575.1 | 0.275 | 0.314 | 6341.5 |
| heterogeneous_condition | H4 | 0.0 | 0.175 | 0.214 | 5774.8 |
| high_stress | H1 | 530.5 | 0.298 | 0.390 | 9707.0 |
| high_stress | H2 | 575.1 | 0.337 | 0.389 | 9706.9 |
| high_stress | H3 | 575.1 | 0.275 | 0.314 | 8475.1 |
| high_stress | H4 | 0.0 | 0.175 | 0.214 | 7964.2 |
| high_demand_high_stress | H1 | 1000.1 | 0.267 | 0.340 | 11121.4 |
| high_demand_high_stress | H2 | 1071.6 | 0.273 | 0.340 | 11126.0 |
| high_demand_high_stress | H3 | 1072.3 | 0.251 | 0.274 | 10214.7 |
| high_demand_high_stress | H4 | 0.0 | 0.173 | 0.228 | 9065.5 |

H1, H2, H3, and H4 share the same congestion calculation path in `run_policy_simulation`; differences are produced by policy route ranking and resulting preferred-attempt utilization. There is no code branch that excludes H4 from congestion.

## H4 vs Synthetic Balanced Round-Robin Comparator

The comparator below is an audit-only synthetic policy. It uses the same H4 `flow_backpressure` PM rule but rotates route preference round-robin. It was run in-memory for 90 days and seeds 101-103 under the same alpha/beta settings.

| regime | policy | seeds | mean congestion h | mean HHI | mean TCO v3 | mean effective fulfillment |
|---|---|---:|---:|---:|---:|---:|
| heterogeneous_condition | H4 existing | 3 | 0.000 | 0.175 | 5524.9 | 0.993 |
| heterogeneous_condition | Balanced RR + H4 PM | 3 | 0.098 | 0.167 | 5310.2 | 1.000 |
| high_stress | H4 existing | 3 | 0.000 | 0.175 | 7826.8 | 0.993 |
| high_stress | Balanced RR + H4 PM | 3 | 0.104 | 0.167 | 7632.9 | 1.000 |
| high_demand_high_stress | H4 existing | 3 | 0.023 | 0.173 | 8812.3 | 0.994 |
| high_demand_high_stress | Balanced RR + H4 PM | 3 | 1.202 | 0.167 | 8639.0 | 1.000 |

## Judgment

- Calculation omission: not found. H4 has route/facility utilization fields, assigned-route load records, preferred-attempt records, and uses the same `_queue_delay` path as H1/H2/H3.
- Zero-congestion reason: for regimes with exactly zero H4 congestion (heterogeneous_condition, high_stress), H4 preferred route/shovel/crusher utilization stayed at or below the hard threshold of 1.0.
- Non-zero regimes in the current audited 90-day output: high_demand_high_stress. If a previous report showed 0.0 in every regime, that was consistent with thresholding and/or rounding at the time, not with an H4 bypass.
- Modeling limitation: current C5.53 congestion is not a queueing-theory occupancy model. It only penalizes utilization above daily capacity. Therefore a policy that stays under all daily preferred-attempt capacities can show exactly zero queue delay even when it operates near capacity.

## Soft-Threshold Design Proposal

Do not change C5.53 until this audit is reviewed. A C5.53/C5.54 follow-up could replace or add a soft-threshold variant:

```text
soft_start = 0.85
effective_pressure = max((utilization - soft_start) / (1.0 - soft_start), 0.0)
soft_queue_delay_min = alpha_soft * effective_pressure ** beta_soft
hard_queue_delay_min = alpha_hard * max(utilization - 1.0, 0.0) ** beta_hard
queue_delay_min = soft_queue_delay_min + hard_queue_delay_min
```

Recommended guardrails for that variant:

- Keep the current hard-threshold metric as `congestion_delay_hours_hard` for backward comparability.
- Add `congestion_delay_hours_soft` and `total_tco_v4_soft_congestion` rather than redefining `total_tco_v3` silently.
- Calibrate `alpha_soft` so moderate utilization, for example 0.85-1.00, creates small but nonzero delay and does not swamp reliability/grade terms.
- Report daily and event-level max utilization because the current model uses daily cumulative utilization, not rolling hourly occupancy.

## Recommendation

Proceed to soft-threshold design or alpha/beta sensitivity only after deciding whether C5.53 should remain a hard-capacity exceedance model or become a near-capacity congestion surface. The audit supports that H4 zero congestion is primarily a threshold/modeling artifact, not a calculation omission.
