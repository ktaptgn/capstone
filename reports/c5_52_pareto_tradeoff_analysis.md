# C5.52 Pareto Tradeoff Analysis

## Scope

- Source CSV: `outputs/c5_52/summary/c5_52_policy_comparison.csv`
- Reference report: `reports/c5_52_grade_aware_objective_test.md`
- Grain: 90 days x 10 seeds, aggregated by policy x regime x shortfall sensitivity.
- Pareto flags are computed within each regime x sensitivity group.

## Interpretation Summary

- H1/H2 are reliability-cost optimal: they minimize legacy `total_tco_v1`, failures, CM, and downtime by concentrating on low-risk routes.
- H4 is production-value-aware optimal under base/high shortfall sensitivity: it keeps effective fulfillment high and minimizes `total_tco_v2` once output shortfall is priced.
- H3 is a middle trade-off: more production value than H1/H2, less flow balance than H4, and usually lower grade-aware value than H4 under base sensitivity.
- H0/H_TIME have high effective output, but they are dominated by their high failure/CM/downtime burden.
- C5.52 proves policy ranking depends on objective definition: v1 favors H1/H2, while v2 base/high favors H4.

## 1. Policy x Regime Mean KPI Table (Base Sensitivity)

### `heterogeneous_condition`
| Policy | TCO v1 | TCO v2 | Effective output | Eff fulfill | Avg grade | Failures | CM | Downtime | PM visits | Shovel C |
|---|---|---|---|---|---|---|---|---|---|---|
| H0 | 9,769.8 | 9,769.8 | 5,433,967.0 | 1.027 | 0.822 | 45.2 | 45.2 | 4,805.9 | 394.0 | 22.4% |
| H_TIME | 9,262.9 | 9,262.9 | 5,433,662.5 | 1.027 | 0.821 | 29.8 | 29.8 | 4,570.6 | 388.0 | 22.5% |
| H1_original | 4,086.8 | 7,412.7 | 4,826,381.0 | 0.912 | 0.730 | 0.0 | 0.0 | 1,977.4 | 567.7 | 70.5% |
| H1_value_guard | 4,080.9 | 7,393.8 | 4,828,208.0 | 0.912 | 0.730 | 0.0 | 0.0 | 1,976.8 | 566.0 | 70.3% |
| H2_original | 4,072.0 | 7,380.8 | 4,828,775.0 | 0.912 | 0.730 | 0.0 | 0.0 | 1,970.7 | 564.1 | 70.3% |
| H2_value_guard | 4,068.8 | 7,368.3 | 4,830,091.0 | 0.913 | 0.730 | 0.1 | 0.1 | 1,968.4 | 563.6 | 70.2% |
| H3 | 5,333.9 | 6,053.9 | 5,191,200.0 | 0.981 | 0.785 | 0.0 | 0.0 | 2,583.1 | 736.6 | 42.9% |
| H4 | 5,504.8 | 5,774.8 | 5,254,200.0 | 0.993 | 0.794 | 0.0 | 0.0 | 2,659.5 | 757.9 | 35.7% |

### `high_stress`
| Policy | TCO v1 | TCO v2 | Effective output | Eff fulfill | Avg grade | Failures | CM | Downtime | PM visits | Shovel C |
|---|---|---|---|---|---|---|---|---|---|---|
| H0 | 11,011.1 | 11,011.1 | 5,433,218.0 | 1.027 | 0.821 | 82.2 | 82.2 | 5,226.6 | 360.0 | 22.4% |
| H_TIME | 10,582.9 | 10,582.9 | 5,433,001.0 | 1.027 | 0.821 | 71.4 | 71.4 | 5,033.6 | 356.0 | 22.5% |
| H1_original | 6,115.4 | 9,441.8 | 4,826,314.5 | 0.912 | 0.730 | 0.0 | 0.0 | 2,955.1 | 752.5 | 70.5% |
| H1_value_guard | 6,131.8 | 9,452.9 | 4,827,060.0 | 0.912 | 0.730 | 0.0 | 0.0 | 2,963.4 | 754.3 | 70.4% |
| H2_original | 6,100.5 | 9,419.3 | 4,827,382.0 | 0.912 | 0.730 | 0.0 | 0.0 | 2,947.5 | 749.7 | 70.4% |
| H2_value_guard | 6,106.4 | 9,411.8 | 4,829,251.0 | 0.913 | 0.730 | 0.1 | 0.1 | 2,950.6 | 750.9 | 70.2% |
| H3 | 7,467.5 | 8,187.5 | 5,191,200.0 | 0.981 | 0.785 | 0.0 | 0.0 | 3,607.5 | 873.0 | 42.9% |
| H4 | 7,694.0 | 7,964.2 | 5,254,182.5 | 0.993 | 0.794 | 0.4 | 0.4 | 3,709.3 | 867.5 | 35.7% |

### `high_demand_high_stress`
| Policy | TCO v1 | TCO v2 | Effective output | Eff fulfill | Avg grade | Failures | CM | Downtime | PM visits | Shovel C |
|---|---|---|---|---|---|---|---|---|---|---|
| H0 | 11,851.0 | 11,851.0 | 6,142,843.0 | 1.011 | 0.809 | 111.6 | 111.6 | 5,585.5 | 360.0 | 27.5% |
| H_TIME | 11,499.2 | 11,499.2 | 6,142,479.0 | 1.011 | 0.809 | 105.4 | 105.4 | 5,419.1 | 356.0 | 27.5% |
| H1_original | 7,294.1 | 10,621.3 | 5,607,395.5 | 0.923 | 0.739 | 0.7 | 0.7 | 3,522.3 | 874.0 | 61.4% |
| H1_value_guard | 7,275.4 | 10,598.2 | 5,608,008.0 | 0.923 | 0.739 | 0.1 | 0.1 | 3,514.1 | 876.4 | 61.4% |
| H2_original | 7,267.9 | 10,590.2 | 5,608,085.0 | 0.923 | 0.739 | 0.7 | 0.7 | 3,509.2 | 872.0 | 61.4% |
| H2_value_guard | 7,277.2 | 10,587.2 | 5,609,807.0 | 0.924 | 0.739 | 1.4 | 1.4 | 3,513.1 | 868.9 | 61.3% |
| H3 | 8,261.0 | 9,678.5 | 5,874,750.0 | 0.967 | 0.774 | 5.8 | 5.8 | 3,974.2 | 852.7 | 50.2% |
| H4 | 8,796.7 | 9,065.5 | 6,035,568.0 | 0.994 | 0.795 | 17.6 | 17.6 | 4,201.7 | 787.2 | 36.5% |

## 2. TCO v1 Ranking vs TCO v2 Ranking

| Regime | TCO v1 top 5 | TCO v2 base top 5 |
|---|---|---|
| heterogeneous_condition | H2_value_guard (4068.8) < H2_original (4072.0) < H1_value_guard (4080.9) < H1_original (4086.8) < H3 (5333.9) | H4 (5774.8) < H3 (6053.9) < H2_value_guard (7368.3) < H2_original (7380.8) < H1_value_guard (7393.8) |
| high_stress | H2_original (6100.5) < H2_value_guard (6106.4) < H1_original (6115.4) < H1_value_guard (6131.8) < H3 (7467.5) | H4 (7964.2) < H3 (8187.5) < H2_value_guard (9411.8) < H2_original (9419.3) < H1_original (9441.8) |
| high_demand_high_stress | H2_original (7267.9) < H1_value_guard (7275.4) < H2_value_guard (7277.2) < H1_original (7294.1) < H3 (8261.0) | H4 (9065.5) < H3 (9678.5) < H2_value_guard (10587.2) < H2_original (10590.2) < H1_value_guard (10598.2) |

## 3. Effective Output Ranking

| Regime | Effective output top 5 |
|---|---|
| heterogeneous_condition | H0 (5433967.0) < H_TIME (5433662.5) < H4 (5254200.0) < H3 (5191200.0) < H2_value_guard (4830091.0) |
| high_stress | H0 (5433218.0) < H_TIME (5433001.0) < H4 (5254182.5) < H3 (5191200.0) < H2_value_guard (4829251.0) |
| high_demand_high_stress | H0 (6142843.0) < H_TIME (6142479.0) < H4 (6035568.0) < H3 (5874750.0) < H2_value_guard (5609807.0) |

## 4. Failure / Downtime Ranking

| Regime | Best reliability/downtime top 5 |
|---|---|
| heterogeneous_condition | H2_original (fail 0.0, down 1971) < H1_value_guard (fail 0.0, down 1977) < H1_original (fail 0.0, down 1977) < H3 (fail 0.0, down 2583) < H4 (fail 0.0, down 2660) |
| high_stress | H2_original (fail 0.0, down 2948) < H1_original (fail 0.0, down 2955) < H1_value_guard (fail 0.0, down 2963) < H3 (fail 0.0, down 3608) < H2_value_guard (fail 0.1, down 2951) |
| high_demand_high_stress | H1_value_guard (fail 0.1, down 3514) < H2_original (fail 0.7, down 3509) < H1_original (fail 0.7, down 3522) < H2_value_guard (fail 1.4, down 3513) < H3 (fail 5.8, down 3974) |

## 5. Dominated / Non-Dominated Classification

Definitions: `v1_output` minimizes `total_tco_v1` and maximizes `effective_output`; `v2_failure_output` minimizes `total_tco_v2` and `failure_count`, and maximizes `effective_output`.

Important interpretation note: the CSV Pareto flags use raw `effective_output` as a maximized axis. That means H0/H_TIME can remain formally non-dominated because they produce the highest output, even though they are not attractive operating policies once failure, CM, and downtime guardrails are considered. In the practical policy interpretation below, H0/H_TIME are treated as dominated by their failure/CM/downtime burden.

### `heterogeneous_condition` / base sensitivity
| Policy | v1_output | v2_failure_output | TCO v1 | TCO v2 | Effective output | Failures |
|---|---|---|---|---|---|---|
| H0 | non-dominated | non-dominated | 9,769.8 | 9,769.8 | 5,433,967.0 | 45.2 |
| H_TIME | non-dominated | non-dominated | 9,262.9 | 9,262.9 | 5,433,662.5 | 29.8 |
| H1_original | dominated | dominated | 4,086.8 | 7,412.7 | 4,826,381.0 | 0.0 |
| H1_value_guard | dominated | dominated | 4,080.9 | 7,393.8 | 4,828,208.0 | 0.0 |
| H2_original | dominated | dominated | 4,072.0 | 7,380.8 | 4,828,775.0 | 0.0 |
| H2_value_guard | non-dominated | dominated | 4,068.8 | 7,368.3 | 4,830,091.0 | 0.1 |
| H3 | non-dominated | dominated | 5,333.9 | 6,053.9 | 5,191,200.0 | 0.0 |
| H4 | non-dominated | non-dominated | 5,504.8 | 5,774.8 | 5,254,200.0 | 0.0 |

### `high_stress` / base sensitivity
| Policy | v1_output | v2_failure_output | TCO v1 | TCO v2 | Effective output | Failures |
|---|---|---|---|---|---|---|
| H0 | non-dominated | non-dominated | 11,011.1 | 11,011.1 | 5,433,218.0 | 82.2 |
| H_TIME | non-dominated | non-dominated | 10,582.9 | 10,582.9 | 5,433,001.0 | 71.4 |
| H1_original | dominated | dominated | 6,115.4 | 9,441.8 | 4,826,314.5 | 0.0 |
| H1_value_guard | dominated | dominated | 6,131.8 | 9,452.9 | 4,827,060.0 | 0.0 |
| H2_original | non-dominated | dominated | 6,100.5 | 9,419.3 | 4,827,382.0 | 0.0 |
| H2_value_guard | non-dominated | dominated | 6,106.4 | 9,411.8 | 4,829,251.0 | 0.1 |
| H3 | non-dominated | non-dominated | 7,467.5 | 8,187.5 | 5,191,200.0 | 0.0 |
| H4 | non-dominated | non-dominated | 7,694.0 | 7,964.2 | 5,254,182.5 | 0.4 |

### `high_demand_high_stress` / base sensitivity
| Policy | v1_output | v2_failure_output | TCO v1 | TCO v2 | Effective output | Failures |
|---|---|---|---|---|---|---|
| H0 | non-dominated | non-dominated | 11,851.0 | 11,851.0 | 6,142,843.0 | 111.6 |
| H_TIME | non-dominated | non-dominated | 11,499.2 | 11,499.2 | 6,142,479.0 | 105.4 |
| H1_original | dominated | dominated | 7,294.1 | 10,621.3 | 5,607,395.5 | 0.7 |
| H1_value_guard | dominated | non-dominated | 7,275.4 | 10,598.2 | 5,608,008.0 | 0.1 |
| H2_original | non-dominated | non-dominated | 7,267.9 | 10,590.2 | 5,608,085.0 | 0.7 |
| H2_value_guard | non-dominated | non-dominated | 7,277.2 | 10,587.2 | 5,609,807.0 | 1.4 |
| H3 | non-dominated | non-dominated | 8,261.0 | 9,678.5 | 5,874,750.0 | 5.8 |
| H4 | non-dominated | non-dominated | 8,796.7 | 9,065.5 | 6,035,568.0 | 17.6 |

## 6. H1/H2 vs H3/H4 Trade-Off Summary

| Regime | Comparison | Delta TCO v1 | Delta TCO v2 | Delta effective output | Delta failures | Delta downtime |
|---|---|---|---|---|---|---|
| heterogeneous_condition | H2_value_guard vs H4 | -1,435.9 | 1,593.5 | -424,109.0 | +0.1 | -691.1 |
| heterogeneous_condition | H3 vs H4 | -170.9 | 279.1 | -63,000.0 | +0.0 | -76.4 |
| high_stress | H2_value_guard vs H4 | -1,587.6 | 1,447.6 | -424,931.5 | -0.3 | -758.7 |
| high_stress | H3 vs H4 | -226.5 | 223.3 | -62,982.5 | -0.4 | -101.8 |
| high_demand_high_stress | H2_value_guard vs H4 | -1,519.5 | 1,521.7 | -425,761.0 | -16.2 | -688.6 |
| high_demand_high_stress | H3 vs H4 | -535.7 | 613.0 | -160,818.0 | -11.8 | -227.5 |

H1/H2 variants buy lower v1 cost and lower downtime/failures by accepting lower effective output. H4 gives up some v1 cost but sharply reduces output shortfall, which makes it strongest under base/high v2. H3 sits between these modes: more output-oriented than H1/H2, less robust on v2 than H4.

## Pareto Finding

- H1/H2 are non-dominated for reliability-cost trade-offs, especially under `v1_output` where they define the low-cost frontier.
- H4 is non-dominated and usually optimal for `v2_failure_output` under base/high sensitivity because it combines high effective output with acceptable failure/downtime.
- H3 is often non-dominated or near-frontier as a value-oriented middle point, but H4 usually dominates it on grade-aware TCO in base sensitivity.
- H0/H_TIME can be formally non-dominated on raw-output Pareto axes, but they are practically dominated for the operating recommendation: high output does not compensate for high PM, CM, failure, and downtime burden.

## Exported Plot Data

- `outputs/c5_52/analysis/c5_52_pareto_points.csv`
- `outputs/c5_52/analysis/c5_52_policy_tradeoff_summary.csv`
