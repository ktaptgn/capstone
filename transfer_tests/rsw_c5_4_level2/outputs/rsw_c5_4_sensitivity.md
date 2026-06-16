# RSW C5.4 Level 2 Sensitivity Analysis

- Synthetic reduced-scale analysis: 10 seeds x 30 days.
- Lower TCO is better. Rankings below are actual mini-test outputs.

## frailty_cv

| setting | regime | policy | TCO | PM visits | CM | failures | defects | fulfillment |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 0.1 | heterogeneous_condition | H0 | 1914.33 | 100.0 | 0.00 | 0.00 | 0.10 | 1.000 |
| 0.1 | heterogeneous_condition | H_TIME | 359.54 | 18.0 | 0.00 | 0.00 | 1.00 | 1.000 |
| 0.1 | heterogeneous_condition | H1 | 79.82 | 2.4 | 0.00 | 0.00 | 6.80 | 1.000 |
| 0.1 | heterogeneous_condition | H2 | 81.03 | 2.3 | 0.00 | 0.00 | 7.00 | 1.000 |
| 0.1 | heterogeneous_condition | H3 | 81.14 | 6.5 | 0.00 | 0.00 | 4.40 | 1.000 |
| 0.1 | heterogeneous_condition | H4 | 84.04 | 7.4 | 0.00 | 0.00 | 4.20 | 1.000 |
| 0.3 | heterogeneous_condition | H0 | 1914.45 | 100.0 | 0.00 | 0.00 | 0.10 | 1.000 |
| 0.3 | heterogeneous_condition | H_TIME | 361.21 | 18.0 | 0.00 | 0.00 | 1.20 | 1.000 |
| 0.3 | heterogeneous_condition | H1 | 84.75 | 3.7 | 0.00 | 0.00 | 6.60 | 1.000 |
| 0.3 | heterogeneous_condition | H2 | 86.49 | 3.7 | 0.00 | 0.00 | 6.80 | 1.000 |
| 0.3 | heterogeneous_condition | H3 | 76.42 | 6.0 | 0.00 | 0.00 | 4.10 | 1.000 |
| 0.3 | heterogeneous_condition | H4 | 74.52 | 6.6 | 0.00 | 0.00 | 3.50 | 1.000 |
| 0.5 | heterogeneous_condition | H0 | 1914.44 | 100.0 | 0.00 | 0.00 | 0.10 | 1.000 |
| 0.5 | heterogeneous_condition | H_TIME | 365.16 | 18.0 | 0.20 | 0.20 | 1.20 | 1.000 |
| 0.5 | heterogeneous_condition | H1 | 80.90 | 3.7 | 0.00 | 0.00 | 6.10 | 1.000 |
| 0.5 | heterogeneous_condition | H2 | 83.18 | 4.0 | 0.00 | 0.00 | 6.20 | 1.000 |
| 0.5 | heterogeneous_condition | H3 | 77.94 | 6.2 | 0.00 | 0.00 | 4.10 | 1.000 |
| 0.5 | heterogeneous_condition | H4 | 82.44 | 6.8 | 0.00 | 0.00 | 4.30 | 1.000 |
| 0.8 | heterogeneous_condition | H0 | 1914.15 | 100.0 | 0.00 | 0.00 | 0.00 | 1.000 |
| 0.8 | heterogeneous_condition | H_TIME | 375.27 | 18.0 | 0.20 | 0.20 | 2.40 | 1.000 |
| 0.8 | heterogeneous_condition | H1 | 75.54 | 4.8 | 0.00 | 0.00 | 4.60 | 1.000 |
| 0.8 | heterogeneous_condition | H2 | 83.17 | 5.1 | 0.00 | 0.00 | 5.30 | 1.000 |
| 0.8 | heterogeneous_condition | H3 | 82.67 | 6.7 | 0.00 | 0.00 | 4.20 | 1.000 |
| 0.8 | heterogeneous_condition | H4 | 81.49 | 7.5 | 0.00 | 0.00 | 3.50 | 1.000 |

## cbm_threshold_scale

| setting | regime | policy | TCO | PM visits | CM | failures | defects | fulfillment |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 0.8 | heterogeneous_condition | H1 | 79.89 | 3.5 | 0.00 | 0.00 | 6.10 | 1.000 |
| 0.9 | heterogeneous_condition | H1 | 79.89 | 3.5 | 0.00 | 0.00 | 6.10 | 1.000 |
| 1.0 | heterogeneous_condition | H1 | 80.90 | 3.7 | 0.00 | 0.00 | 6.10 | 1.000 |
| 1.1 | heterogeneous_condition | H1 | 81.42 | 4.6 | 0.00 | 0.00 | 5.60 | 1.000 |
| 1.2 | heterogeneous_condition | H1 | 79.55 | 4.7 | 0.00 | 0.00 | 5.30 | 1.000 |
| 0.8 | high_stress | H1 | 117.85 | 6.9 | 0.00 | 0.00 | 8.10 | 1.000 |
| 0.9 | high_stress | H1 | 117.85 | 6.9 | 0.00 | 0.00 | 8.10 | 1.000 |
| 1.0 | high_stress | H1 | 121.18 | 7.7 | 0.00 | 0.00 | 8.00 | 1.000 |
| 1.1 | high_stress | H1 | 118.21 | 8.3 | 0.00 | 0.00 | 7.20 | 1.000 |
| 1.2 | high_stress | H1 | 122.54 | 9.4 | 0.00 | 0.00 | 6.90 | 1.000 |
| 0.8 | high_demand_high_stress | H1 | 142.10 | 9.8 | 0.00 | 0.00 | 8.80 | 1.000 |
| 0.9 | high_demand_high_stress | H1 | 142.10 | 9.8 | 0.00 | 0.00 | 8.80 | 1.000 |
| 1.0 | high_demand_high_stress | H1 | 137.62 | 10.1 | 0.00 | 0.00 | 8.00 | 1.000 |
| 1.1 | high_demand_high_stress | H1 | 135.92 | 11.2 | 0.00 | 0.00 | 7.10 | 1.000 |
| 1.2 | high_demand_high_stress | H1 | 137.36 | 12.0 | 0.00 | 0.00 | 6.70 | 1.000 |

## maintenance_slots

| setting | regime | policy | TCO | PM visits | CM | failures | defects | fulfillment |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | heterogeneous_condition | H0 | 1732.51 | 90.0 | 0.10 | 0.10 | 1.00 | 1.000 |
| 1 | heterogeneous_condition | H_TIME | 329.55 | 16.0 | 0.00 | 0.00 | 1.50 | 1.000 |
| 1 | heterogeneous_condition | H1 | 80.90 | 3.7 | 0.00 | 0.00 | 6.10 | 1.000 |
| 1 | heterogeneous_condition | H2 | 83.18 | 4.0 | 0.00 | 0.00 | 6.20 | 1.000 |
| 1 | heterogeneous_condition | H3 | 77.94 | 6.2 | 0.00 | 0.00 | 4.10 | 1.000 |
| 1 | heterogeneous_condition | H4 | 82.44 | 6.8 | 0.00 | 0.00 | 4.30 | 1.000 |
| 2 | heterogeneous_condition | H0 | 1914.44 | 100.0 | 0.00 | 0.00 | 0.10 | 1.000 |
| 2 | heterogeneous_condition | H_TIME | 365.16 | 18.0 | 0.20 | 0.20 | 1.20 | 1.000 |
| 2 | heterogeneous_condition | H1 | 80.90 | 3.7 | 0.00 | 0.00 | 6.10 | 1.000 |
| 2 | heterogeneous_condition | H2 | 83.18 | 4.0 | 0.00 | 0.00 | 6.20 | 1.000 |
| 2 | heterogeneous_condition | H3 | 77.94 | 6.2 | 0.00 | 0.00 | 4.10 | 1.000 |
| 2 | heterogeneous_condition | H4 | 82.44 | 6.8 | 0.00 | 0.00 | 4.30 | 1.000 |
| 3 | heterogeneous_condition | H0 | 1913.58 | 100.0 | 0.00 | 0.00 | 0.00 | 1.000 |
| 3 | heterogeneous_condition | H_TIME | 397.56 | 20.0 | 0.00 | 0.00 | 1.00 | 1.000 |
| 3 | heterogeneous_condition | H1 | 80.90 | 3.7 | 0.00 | 0.00 | 6.10 | 1.000 |
| 3 | heterogeneous_condition | H2 | 83.18 | 4.0 | 0.00 | 0.00 | 6.20 | 1.000 |
| 3 | heterogeneous_condition | H3 | 77.94 | 6.2 | 0.00 | 0.00 | 4.10 | 1.000 |
| 3 | heterogeneous_condition | H4 | 82.44 | 6.8 | 0.00 | 0.00 | 4.30 | 1.000 |
