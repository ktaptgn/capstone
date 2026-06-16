# RSW Demand Pressure Stress Sanity Report

These additional runs are sanity checks, not real factory validation.
 Demand stress was added because the original base demand had too much slack.

## Results

| policy | TCO mean | fulfillment mean | unmet welds mean | PMvisits mean | CM mean | failure mean |
|---|---:|---:|---:|---:|---:|---:|
| H3 | 2293.828 | 1.000 | 0.000 | 219.500 | 0.000 | 0.000 |
| H4 | 2468.887 | 1.000 | 0.000 | 206.500 | 0.000 | 0.000 |
| H1 | 2585.733 | 1.000 | 0.000 | 216.300 | 0.000 | 0.000 |
| H2 | 2668.470 | 1.000 | 0.000 | 216.300 | 0.000 | 0.000 |
| H0 | 3076.012 | 1.000 | 0.000 | 100.000 | 20.000 | 20.000 |
| H_TIME | 3511.069 | 1.000 | 1.500 | 163.500 | 4.200 | 4.200 |

## Findings

- H3 had the lowest stress TCO (2293.83 synthetic CU).
- Mean unmet demand appeared only for H_TIME; most policies still retained enough production slack for fulfillment = 1.000.
- H4 did not win the stress run; results are retained without post-hoc tuning.

Results are reported as-is and not tuned to reproduce the C5.4 mining ranking.
