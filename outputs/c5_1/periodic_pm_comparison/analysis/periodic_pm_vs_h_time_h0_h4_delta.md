# Pure Periodic PM vs PM Due-Time and H0-H4 Comparison

`H_PERIODIC` is the pure periodic PM baseline: fixed truck calendar slots every `periodic_pm_interval_days`, independent of PM due time, HI, queue, cost, or flow.
`H_TIME` is the PM due-time baseline: it triggers PM from `pm_due_hours <= pm_due_threshold_hours`.

## Mean KPI Summary

| Policy | Total Cost | PM Cost | Unmet Demand | Fulfillment | Completed Loads | Avg Queue | Availability |
|---|---:|---:|---:|---:|---:|---:|---:|
| H_PERIODIC | 4283.0580 | 1095.0000 | 856.0000 | 0.870132 | 5735.0000 | 1.786884 | 0.630608 |
| H_TIME | 1020.2817 | 325.5000 | 121.3333 | 0.981602 | 6469.6667 | 2.546726 | 0.894164 |
| H0 | 1858.6480 | 520.8333 | 347.6667 | 0.947260 | 6243.3333 | 2.276808 | 0.820819 |
| H1 | 7062.5313 | 200.6667 | 3306.0000 | 0.498415 | 3285.0000 | 2.215000 | 0.965168 |
| H2 | 3339.3740 | 402.6667 | 1219.3333 | 0.814993 | 5371.6667 | 2.324171 | 0.888342 |
| H3 | 1724.7487 | 605.8333 | 192.6667 | 0.970774 | 6398.3333 | 2.726007 | 0.920291 |
| H4 | 7062.5313 | 200.6667 | 3306.0000 | 0.498415 | 3285.0000 | 2.215000 | 0.965168 |

## Improvement vs H_PERIODIC

| Policy | Total Cost Improvement % | Unmet Demand Improvement % | Fulfillment Delta | PM Cost Improvement % | Queue Improvement % | Availability Delta |
|---|---:|---:|---:|---:|---:|---:|
| H_TIME | 76.178662 | 85.825545 | 0.111470 | 70.273973 | -42.523298 | 0.263556 |
| H0 | 56.60465 | 59.384735 | 0.077129 | 52.435312 | -27.417803 | 0.190211 |
| H1 | -64.894599 | -286.214953 | -0.371716 | 81.674277 | -23.958802 | 0.334560 |
| H2 | 22.032949 | -42.445483 | -0.055139 | 63.226788 | -30.068395 | 0.257734 |
| H3 | 59.730906 | 77.492212 | 0.100643 | 44.672755 | -52.556461 | 0.289683 |
| H4 | -64.894599 | -286.214953 | -0.371716 | 81.674277 | -23.958802 | 0.334560 |

## Interpretation

- `H_PERIODIC` has the lowest average queue time, but it over-schedules PM under the current 3-day cycle and reduces availability/production.
- `H_TIME` performs best on mean total cost, unmet demand, and demand fulfillment in this generated C5.1 run.
- `H3` is the closest H0-H4 heuristic competitor on production and cost, but it still trails `H_TIME` under the current parameters.
- This experiment separates pure calendar PM from PM due-time PM; the result should be presented as parameter-sensitive, not universal.
