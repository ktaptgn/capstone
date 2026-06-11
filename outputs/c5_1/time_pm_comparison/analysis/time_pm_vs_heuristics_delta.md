# Time-Periodic PM vs H0-H4 Comparison

Baseline `H_TIME` triggers `PM_VEHICLE` only when `pm_due_hours <= pm_due_threshold_hours`; it does not use HI, queue, cost, or flow heuristics.

## Mean KPI Summary

| Policy | Total Cost | PM Cost | Unmet Demand | Fulfillment | Completed Loads | Avg Queue | Availability |
|---|---:|---:|---:|---:|---:|---:|---:|
| H_TIME | 1020.2817 | 325.5000 | 121.3333 | 0.981602 | 6469.6667 | 2.546726 | 0.894164 |
| H0 | 1858.6480 | 520.8333 | 347.6667 | 0.947260 | 6243.3333 | 2.276808 | 0.820819 |
| H1 | 7062.5313 | 200.6667 | 3306.0000 | 0.498415 | 3285.0000 | 2.215000 | 0.965168 |
| H2 | 3339.3740 | 402.6667 | 1219.3333 | 0.814993 | 5371.6667 | 2.324171 | 0.888342 |
| H3 | 1724.7487 | 605.8333 | 192.6667 | 0.970774 | 6398.3333 | 2.726007 | 0.920291 |
| H4 | 7062.5313 | 200.6667 | 3306.0000 | 0.498415 | 3285.0000 | 2.215000 | 0.965168 |

## H0-H4 Improvement vs H_TIME

| Policy | Total Cost Improvement % | Unmet Demand Improvement % | Fulfillment Delta | PM Cost Improvement % | Queue Improvement % | Availability Delta |
|---|---:|---:|---:|---:|---:|---:|
| H0 | -82.170075 | -186.538462 | -0.034341 | -60.010241 | 10.598614 | -0.073345 |
| H1 | -592.213837 | -2624.725275 | -0.483186 | 38.351254 | 13.025587 | 0.071005 |
| H2 | -227.299205 | -904.945055 | -0.166609 | -23.707117 | 8.738854 | -0.005822 |
| H3 | -69.046314 | -58.791209 | -0.010827 | -86.123912 | -7.039666 | 0.026128 |
| H4 | -592.213837 | -2624.725275 | -0.483186 | 38.351254 | 13.025587 | 0.071005 |

## Interpretation

- In this generated run, `H_TIME` has the lowest mean total cost and highest mean demand fulfillment among the compared policies.
- `H3` is the closest heuristic competitor on production KPIs, but it uses higher PM cost and has higher total cost than `H_TIME` in this experiment.
- This result means the current C5.1 parameterization strongly rewards simple due-hour PM; it should be presented as an experimental finding, not as proof that time-periodic PM is universally superior.
