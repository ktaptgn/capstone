# C5.53 Soft-Threshold Congestion Analysis

## Why This Variant Was Needed

The H4 zero-congestion audit found no calculation bypass. H4 uses the same C5.53 congestion path as H1/H2/H3, but the hard-threshold formula only penalizes utilization above 1.0. That can under-penalize near-capacity operation, especially for capacity-aware policies that stay just below the hard cap.

## Audit Recap

- H4 route and facility load recording is valid.
- H4 route/facility utilization is calculated.
- Existing `total_tco_v3` is preserved as the hard-threshold result.
- `BALANCED_RR_H4_PM` is an audit-only synthetic comparator, not an official policy.

## Formula

Hard congestion remains:

```text
hard_queue_delay = alpha_hard * max(utilization - 1.0, 0.0) ** beta_hard
```

Soft congestion adds near-capacity pressure:

```text
soft_start = 0.85
effective_pressure = max((utilization - soft_start) / (1.0 - soft_start), 0.0)
soft_queue_delay = alpha_soft * effective_pressure ** beta_soft
queue_delay_soft_total = soft_queue_delay + hard_queue_delay
```

## Policy x Regime Ranking

| regime | policy | hard rank | soft rank | TCO v3 hard | TCO v4 soft | hard congestion h | soft congestion h | effective fulfillment | failures | downtime h |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| heterogeneous_condition | BALANCED_RR_H4_PM | 1 | 1 | 5568.5 | 5570.9 | 0.10 | 5.04 | 1.000 | 0.0 | 2691.7 |
| heterogeneous_condition | H4 | 2 | 2 | 5774.8 | 5775.0 | 0.00 | 0.35 | 0.993 | 0.0 | 2659.5 |
| heterogeneous_condition | H3 | 3 | 3 | 6341.5 | 7973.1 | 575.13 | 3838.34 | 0.981 | 0.0 | 2583.1 |
| heterogeneous_condition | H1 | 7 | 4 | 7669.2 | 9136.5 | 512.95 | 3447.62 | 0.912 | 0.0 | 1977.4 |
| heterogeneous_condition | H1_original | 8 | 5 | 7669.2 | 9136.5 | 512.95 | 3447.62 | 0.912 | 0.0 | 1977.4 |
| heterogeneous_condition | H_TIME | 10 | 6 | 9263.7 | 9276.7 | 1.51 | 27.48 | 1.027 | 29.8 | 4570.6 |
| heterogeneous_condition | H2_value_guard | 4 | 7 | 7655.8 | 9287.5 | 575.14 | 3838.43 | 0.913 | 0.1 | 1968.4 |
| heterogeneous_condition | H2 | 5 | 8 | 7668.4 | 9300.0 | 575.13 | 3838.34 | 0.912 | 0.0 | 1970.7 |
| heterogeneous_condition | H2_original | 6 | 9 | 7668.4 | 9300.0 | 575.13 | 3838.34 | 0.912 | 0.0 | 1970.7 |
| heterogeneous_condition | H1_value_guard | 9 | 10 | 7681.3 | 9312.9 | 575.13 | 3838.34 | 0.912 | 0.0 | 1976.8 |
| heterogeneous_condition | H0 | 11 | 11 | 9770.6 | 9783.6 | 1.51 | 27.51 | 1.027 | 45.2 | 4805.9 |
| high_demand_high_stress | BALANCED_RR_H4_PM | 1 | 1 | 8893.5 | 8905.0 | 1.22 | 24.27 | 1.000 | 20.4 | 4242.3 |
| high_demand_high_stress | H4 | 2 | 2 | 9065.5 | 9069.2 | 0.02 | 7.35 | 0.994 | 17.6 | 4201.7 |
| high_demand_high_stress | H_TIME | 10 | 3 | 11501.0 | 11525.3 | 3.59 | 52.28 | 1.011 | 105.4 | 5419.1 |
| high_demand_high_stress | H0 | 11 | 4 | 11852.7 | 11877.1 | 3.59 | 52.33 | 1.011 | 111.6 | 5585.5 |
| high_demand_high_stress | H3 | 3 | 5 | 10214.7 | 13128.7 | 1072.34 | 6900.39 | 0.967 | 5.8 | 3974.2 |
| high_demand_high_stress | H1 | 4 | 6 | 11121.4 | 13851.2 | 1000.13 | 6459.77 | 0.923 | 0.7 | 3522.3 |
| high_demand_high_stress | H1_original | 5 | 7 | 11121.4 | 13851.2 | 1000.13 | 6459.77 | 0.923 | 0.7 | 3522.3 |
| high_demand_high_stress | H2_value_guard | 6 | 8 | 11123.1 | 14035.6 | 1071.73 | 6896.75 | 0.924 | 1.4 | 3513.1 |
| high_demand_high_stress | H2 | 7 | 9 | 11126.0 | 14038.3 | 1071.61 | 6896.03 | 0.923 | 0.7 | 3509.2 |
| high_demand_high_stress | H2_original | 8 | 10 | 11126.0 | 14038.3 | 1071.61 | 6896.03 | 0.923 | 0.7 | 3509.2 |
| high_demand_high_stress | H1_value_guard | 9 | 11 | 11134.0 | 14045.9 | 1071.50 | 6895.39 | 0.923 | 0.1 | 3514.1 |
| high_stress | BALANCED_RR_H4_PM | 1 | 1 | 7764.9 | 7767.4 | 0.11 | 5.09 | 1.000 | 0.4 | 3736.7 |
| high_stress | H4 | 2 | 2 | 7964.2 | 7964.3 | 0.00 | 0.35 | 0.993 | 0.4 | 3709.3 |
| high_stress | H3 | 3 | 3 | 8475.1 | 10106.7 | 575.13 | 3838.34 | 0.981 | 0.0 | 3607.5 |
| high_stress | H_TIME | 10 | 4 | 10583.7 | 10596.8 | 1.54 | 27.84 | 1.027 | 71.4 | 5033.6 |
| high_stress | H0 | 11 | 5 | 11011.9 | 11025.0 | 1.53 | 27.72 | 1.027 | 82.2 | 5226.6 |
| high_stress | H1 | 7 | 6 | 9707.0 | 11221.0 | 530.47 | 3558.51 | 0.912 | 0.0 | 2955.1 |
| high_stress | H1_original | 8 | 7 | 9707.0 | 11221.0 | 530.47 | 3558.51 | 0.912 | 0.0 | 2955.1 |
| high_stress | H2_value_guard | 4 | 8 | 9699.4 | 11331.0 | 575.13 | 3838.40 | 0.913 | 0.1 | 2950.6 |
| high_stress | H2 | 5 | 9 | 9706.9 | 11338.5 | 575.13 | 3838.34 | 0.912 | 0.0 | 2947.5 |
| high_stress | H2_original | 6 | 10 | 9706.9 | 11338.5 | 575.13 | 3838.34 | 0.912 | 0.0 | 2947.5 |
| high_stress | H1_value_guard | 9 | 11 | 9740.4 | 11372.1 | 575.13 | 3838.34 | 0.912 | 0.0 | 2963.4 |

## H4 Comparisons Under Soft Threshold

| regime | H4 soft TCO | H3 soft TCO | best H1/H2 variant | best H1/H2 soft TCO | Balanced RR soft TCO | H4 best official? | Balanced beats H4? |
|---|---:|---:|---|---:|---:|---|---|
| heterogeneous_condition | 5775.0 | 7973.1 | H1 | 9136.5 | 5570.9 | True | True |
| high_demand_high_stress | 9069.2 | 13128.7 | H1 | 13851.2 | 8905.0 | True | True |
| high_stress | 7964.3 | 10106.7 | H1 | 11221.0 | 7767.4 | True | True |

## Interpretation

- H4 remains best among official H0-H4 policies under soft TCO: True.
- BALANCED_RR_H4_PM beats H4 in at least one regime: True. This is not a final policy result; it is evidence that route allocation can be improved beyond current H4.
- H3 remains the value-oriented middle option when it approaches H4, but the soft-threshold comparison should be read by regime rather than as a universal replacement.
- H1/H2 variants remain structurally exposed when C-route concentration creates high soft congestion and low effective fulfillment.
- H0/H_TIME can retain high effective fulfillment but remain dominated in practice by failure, CM, and downtime.

## Design Implication

Soft thresholding changes the interpretation from pure capacity exceedance to near-capacity pressure. If the synthetic balanced comparator consistently beats H4, the next design step is a C5.54 route allocation experiment, not immediate H5 creation. H5 should only be justified after testing whether an official policy can combine H4's reliability/flow logic with a more effective route allocation rule.
