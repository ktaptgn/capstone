# RSW 90-Day Horizon Sanity Report

These additional runs are sanity checks, not real factory validation.
 The 90-day run was added because the original failure path was sparse.

## Results

| regime | policy | TCO mean | PMvisits mean | CM mean | failure mean | fulfillment mean |
|---|---|---:|---:|---:|---:|---:|
| heterogeneous_condition | H4 | 448.745 | 46.400 | 0.000 | 0.000 | 1.000 |
| heterogeneous_condition | H3 | 479.067 | 43.300 | 0.000 | 0.000 | 1.000 |
| heterogeneous_condition | H1 | 538.162 | 41.300 | 0.000 | 0.000 | 1.000 |
| heterogeneous_condition | H2 | 548.851 | 41.200 | 0.000 | 0.000 | 1.000 |
| heterogeneous_condition | H_TIME | 1239.651 | 62.000 | 0.300 | 0.300 | 1.000 |
| heterogeneous_condition | H0 | 5742.482 | 300.000 | 0.000 | 0.000 | 1.000 |
| high_demand_high_stress | H4 | 734.391 | 81.200 | 0.000 | 0.000 | 1.000 |
| high_demand_high_stress | H3 | 761.575 | 79.300 | 0.000 | 0.000 | 1.000 |
| high_demand_high_stress | H2 | 826.591 | 74.600 | 0.000 | 0.000 | 1.000 |
| high_demand_high_stress | H1 | 829.752 | 75.200 | 0.000 | 0.000 | 1.000 |
| high_demand_high_stress | H_TIME | 1468.760 | 70.200 | 1.300 | 1.300 | 1.000 |
| high_demand_high_stress | H0 | 5760.966 | 300.000 | 0.000 | 0.000 | 1.000 |
| high_stress | H3 | 611.485 | 65.900 | 0.000 | 0.000 | 1.000 |
| high_stress | H4 | 612.335 | 68.300 | 0.000 | 0.000 | 1.000 |
| high_stress | H1 | 716.838 | 63.400 | 0.000 | 0.000 | 1.000 |
| high_stress | H2 | 721.482 | 62.400 | 0.000 | 0.000 | 1.000 |
| high_stress | H_TIME | 1300.897 | 61.500 | 1.200 | 1.200 | 1.000 |
| high_stress | H0 | 5754.747 | 300.000 | 0.000 | 0.000 | 1.000 |

## Findings

- Failure/CM mean totals increased from 1.2 at 30 days to 2.8 at 90 days.
- Observed 90-day failure/CM events remained concentrated in H_TIME.
- Lowest-TCO policies by regime were heterogeneous_condition: H4, high_demand_high_stress: H4, high_stress: H3.
- H1-H4 retained component-targeted PM; no policy ranking was forced.

Results are reported as-is and not tuned to reproduce the C5.4 mining ranking.
