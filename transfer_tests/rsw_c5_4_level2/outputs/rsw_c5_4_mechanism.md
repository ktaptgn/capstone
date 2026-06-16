# RSW C5.4 Level 2 Mechanism Analysis

- Synthetic mini-test scale: 10 seeds x 30 days.
- Actual results are reported without forcing the expected C5.4 mining ranking.

## Failure timing

| regime | policy | early | mid | late | total |
|---|---|---:|---:|---:|---:|
| heterogeneous_condition | H0 | 0 | 0 | 0 | 0 |
| heterogeneous_condition | H_TIME | 0 | 0 | 2 | 2 |
| heterogeneous_condition | H1 | 0 | 0 | 0 | 0 |
| heterogeneous_condition | H2 | 0 | 0 | 0 | 0 |
| heterogeneous_condition | H3 | 0 | 0 | 0 | 0 |
| heterogeneous_condition | H4 | 0 | 0 | 0 | 0 |
| high_stress | H0 | 0 | 0 | 0 | 0 |
| high_stress | H_TIME | 0 | 1 | 3 | 4 |
| high_stress | H1 | 0 | 0 | 0 | 0 |
| high_stress | H2 | 0 | 0 | 0 | 0 |
| high_stress | H3 | 0 | 0 | 0 | 0 |
| high_stress | H4 | 0 | 0 | 0 | 0 |
| high_demand_high_stress | H0 | 0 | 0 | 0 | 0 |
| high_demand_high_stress | H_TIME | 1 | 0 | 5 | 6 |
| high_demand_high_stress | H1 | 0 | 0 | 0 | 0 |
| high_demand_high_stress | H2 | 0 | 0 | 0 | 0 |
| high_demand_high_stress | H3 | 0 | 0 | 0 | 0 |
| high_demand_high_stress | H4 | 0 | 0 | 0 | 0 |

## Causal profile

| regime | policy | TCO | PM visits | failures | defects | end HI | corr(max frailty, failure) | PM tip share | route A/B/C |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| heterogeneous_condition | H0 | 1914.44 | 100.0 | 0.00 | 0.10 | 0.831 | None | 0.333 | 0.333/0.333/0.333 |
| heterogeneous_condition | H_TIME | 365.16 | 18.0 | 0.20 | 1.20 | 0.752 | 0.618036 | 0.333 | 0.333/0.333/0.333 |
| heterogeneous_condition | H1 | 80.90 | 3.7 | 0.00 | 6.10 | 0.413 | None | 0.973 | 0.333/0.333/0.333 |
| heterogeneous_condition | H2 | 83.18 | 4.0 | 0.00 | 6.20 | 0.418 | None | 0.975 | 0.333/0.333/0.333 |
| heterogeneous_condition | H3 | 77.94 | 6.2 | 0.00 | 4.10 | 0.474 | None | 0.952 | 0.333/0.333/0.333 |
| heterogeneous_condition | H4 | 82.44 | 6.8 | 0.00 | 4.30 | 0.486 | None | 0.941 | 0.333/0.333/0.333 |
| high_stress | H0 | 1918.53 | 100.0 | 0.00 | 0.10 | 0.826 | None | 0.333 | 0.333/0.333/0.333 |
| high_stress | H_TIME | 394.93 | 17.9 | 0.40 | 4.10 | 0.695 | 0.58016 | 0.333 | 0.333/0.333/0.333 |
| high_stress | H1 | 121.18 | 7.7 | 0.00 | 8.00 | 0.405 | None | 0.922 | 0.333/0.333/0.333 |
| high_stress | H2 | 115.73 | 7.7 | 0.00 | 7.30 | 0.401 | None | 0.909 | 0.333/0.333/0.333 |
| high_stress | H3 | 112.00 | 11.6 | 0.00 | 4.30 | 0.476 | None | 0.914 | 0.333/0.333/0.333 |
| high_stress | H4 | 112.32 | 11.3 | 0.00 | 4.50 | 0.472 | None | 0.903 | 0.333/0.333/0.333 |
| high_demand_high_stress | H0 | 1920.06 | 100.0 | 0.00 | 0.00 | 0.822 | None | 0.333 | 0.333/0.333/0.333 |
| high_demand_high_stress | H_TIME | 451.21 | 21.4 | 0.60 | 2.20 | 0.720 | 0.664292 | 0.333 | 0.333/0.333/0.333 |
| high_demand_high_stress | H1 | 137.62 | 10.1 | 0.00 | 8.00 | 0.390 | None | 0.832 | 0.333/0.333/0.333 |
| high_demand_high_stress | H2 | 144.89 | 10.0 | 0.00 | 9.10 | 0.388 | None | 0.860 | 0.333/0.333/0.333 |
| high_demand_high_stress | H3 | 132.63 | 14.7 | 0.00 | 4.40 | 0.466 | None | 0.864 | 0.333/0.333/0.333 |
| high_demand_high_stress | H4 | 126.18 | 13.9 | 0.00 | 4.10 | 0.456 | None | 0.856 | 0.333/0.333/0.333 |
