# C5.52 Grade-Aware Objective Test

## 데이터 범위

- 입력 파일: `outputs/c5_52/summary/c5_52_policy_comparison.csv`
- 행 수: 900
- 실행 범위: 90 days x 10 seeds x 3 regimes x 10 policies x 3 shortfall sensitivities
- Regimes: `heterogeneous_condition`, `high_stress`, `high_demand_high_stress`
- Sensitivity: `low`, `base`, `high`
- 주요 해석은 `base` sensitivity 기준이며, sensitivity 변화는 별도 표로 정리했다.

## 1. C5.51에서 발견된 문제 요약

C5.51 audit에서 확인된 핵심 문제는 objective mismatch다. `demand_fulfillment_rate`는 `completed_loads / total_demand` 기준이었고, `effective_output`은 KPI로만 저장되며 TCO에는 직접 반영되지 않았다. 그 결과 H1/H2는 Shovel C 중심의 low-risk / low-grade route를 많이 선택하면서도 load fulfillment 1.000과 낮은 TCO를 동시에 달성했다.

C5.52는 C5.51을 수정하지 않고 별도 실험 모듈로 생성했다. C5.52는 기존 load-based fulfillment를 유지하면서 grade-adjusted production target과 shortfall cost를 추가한다.

## 2. Fulfillment 기준 차이

| Metric | 정의 | 목적 |
|---|---|---|
| `demand_fulfillment_rate` | `completed_loads / total_demand` | 기존 C5.51 load count fulfillment 유지 |
| `target_effective_output` | `total_demand x payload_ton x target_effective_grade_index` | balanced Shovel B-equivalent output target, target grade index = 0.80 |
| `effective_fulfillment_rate` | `effective_output / target_effective_output` | grade-adjusted production fulfillment |
| `total_tco_v1` | 기존 C5.51 TCO | reliability-cost objective |
| `total_tco_v2` | `total_tco_v1 + effective_output_shortfall_cost` | grade-aware objective variant |

## 3. Base Sensitivity 결과: Policy x Regime KPI

### Regime: `heterogeneous_condition`
| Policy | Load fulfill | Effective fulfill | Avg grade/load | Effective output | TCO v1 | Shortfall cost | TCO v2 |
|---|---|---|---|---|---|---|---|
| H0 | 1.000 | 1.027 | 0.822 | 5,433,967.0 | 9,769.8 | 0.0 | 9,769.8 |
| H_TIME | 1.000 | 1.027 | 0.821 | 5,433,662.5 | 9,262.9 | 0.0 | 9,262.9 |
| H1_original | 1.000 | 0.912 | 0.730 | 4,826,381.0 | 4,086.8 | 3,325.9 | 7,412.7 |
| H1_value_guard | 1.000 | 0.912 | 0.730 | 4,828,208.0 | 4,080.9 | 3,312.9 | 7,393.8 |
| H2_original | 1.000 | 0.912 | 0.730 | 4,828,775.0 | 4,072.0 | 3,308.8 | 7,380.8 |
| H2_value_guard | 1.000 | 0.913 | 0.730 | 4,830,091.0 | 4,068.8 | 3,299.4 | 7,368.3 |
| H3 | 1.000 | 0.981 | 0.785 | 5,191,200.0 | 5,333.9 | 720.0 | 6,053.9 |
| H4 | 1.000 | 0.993 | 0.794 | 5,254,200.0 | 5,504.8 | 270.0 | 5,774.8 |

### Regime: `high_stress`
| Policy | Load fulfill | Effective fulfill | Avg grade/load | Effective output | TCO v1 | Shortfall cost | TCO v2 |
|---|---|---|---|---|---|---|---|
| H0 | 1.000 | 1.027 | 0.821 | 5,433,218.0 | 11,011.1 | 0.0 | 11,011.1 |
| H_TIME | 1.000 | 1.027 | 0.821 | 5,433,001.0 | 10,582.9 | 0.0 | 10,582.9 |
| H1_original | 1.000 | 0.912 | 0.730 | 4,826,314.5 | 6,115.4 | 3,326.4 | 9,441.8 |
| H1_value_guard | 1.000 | 0.912 | 0.730 | 4,827,060.0 | 6,131.8 | 3,321.1 | 9,452.9 |
| H2_original | 1.000 | 0.912 | 0.730 | 4,827,382.0 | 6,100.5 | 3,318.8 | 9,419.3 |
| H2_value_guard | 1.000 | 0.913 | 0.730 | 4,829,251.0 | 6,106.4 | 3,305.4 | 9,411.8 |
| H3 | 1.000 | 0.981 | 0.785 | 5,191,200.0 | 7,467.5 | 720.0 | 8,187.5 |
| H4 | 1.000 | 0.993 | 0.794 | 5,254,182.5 | 7,694.0 | 270.1 | 7,964.2 |

### Regime: `high_demand_high_stress`
| Policy | Load fulfill | Effective fulfill | Avg grade/load | Effective output | TCO v1 | Shortfall cost | TCO v2 |
|---|---|---|---|---|---|---|---|
| H0 | 1.000 | 1.011 | 0.809 | 6,142,843.0 | 11,851.0 | 0.0 | 11,851.0 |
| H_TIME | 1.000 | 1.011 | 0.809 | 6,142,479.0 | 11,499.2 | 0.0 | 11,499.2 |
| H1_original | 1.000 | 0.923 | 0.739 | 5,607,395.5 | 7,294.1 | 3,327.2 | 10,621.3 |
| H1_value_guard | 1.000 | 0.923 | 0.739 | 5,608,008.0 | 7,275.4 | 3,322.9 | 10,598.2 |
| H2_original | 1.000 | 0.923 | 0.739 | 5,608,085.0 | 7,267.9 | 3,322.3 | 10,590.2 |
| H2_value_guard | 1.000 | 0.924 | 0.739 | 5,609,807.0 | 7,277.2 | 3,310.0 | 10,587.2 |
| H3 | 1.000 | 0.967 | 0.774 | 5,874,750.0 | 8,261.0 | 1,417.5 | 9,678.5 |
| H4 | 1.000 | 0.994 | 0.795 | 6,035,568.0 | 8,796.7 | 268.8 | 9,065.5 |

## 4. Policy별 Route Share (Base Sensitivity)

### Regime: `heterogeneous_condition`
| Policy | R_A1 | R_A2 | R_B1 | R_B2 | R_C1 | R_C2 |
|---|---|---|---|---|---|---|
| H0 | 22.0% | 21.9% | 21.9% | 11.8% | 11.6% | 10.7% |
| H_TIME | 21.9% | 22.0% | 22.0% | 11.7% | 11.7% | 10.8% |
| H1_original | 0.1% | 0.0% | 18.8% | 10.6% | 31.4% | 39.0% |
| H1_value_guard | 0.2% | 0.0% | 29.5% | 0.0% | 31.4% | 38.9% |
| H2_original | 0.2% | 0.0% | 29.5% | 0.0% | 31.4% | 38.8% |
| H2_value_guard | 0.3% | 0.0% | 29.5% | 0.0% | 31.4% | 38.7% |
| H3 | 27.6% | 0.0% | 29.5% | 0.0% | 31.4% | 11.4% |
| H4 | 12.9% | 17.1% | 12.9% | 21.4% | 14.3% | 21.4% |

### Regime: `high_stress`
| Policy | R_A1 | R_A2 | R_B1 | R_B2 | R_C1 | R_C2 |
|---|---|---|---|---|---|---|
| H0 | 21.9% | 21.9% | 21.9% | 11.9% | 11.6% | 10.8% |
| H_TIME | 21.9% | 21.9% | 22.0% | 11.7% | 11.7% | 10.8% |
| H1_original | 0.1% | 0.0% | 18.6% | 10.8% | 31.4% | 39.0% |
| H1_value_guard | 0.1% | 0.0% | 29.5% | 0.0% | 31.4% | 39.0% |
| H2_original | 0.1% | 0.0% | 29.5% | 0.0% | 31.4% | 38.9% |
| H2_value_guard | 0.3% | 0.0% | 29.5% | 0.0% | 31.4% | 38.8% |
| H3 | 27.6% | 0.0% | 29.5% | 0.0% | 31.4% | 11.4% |
| H4 | 12.9% | 17.1% | 12.9% | 21.4% | 14.3% | 21.4% |

### Regime: `high_demand_high_stress`
| Policy | R_A1 | R_A2 | R_B1 | R_B2 | R_C1 | R_C2 |
|---|---|---|---|---|---|---|
| H0 | 18.8% | 17.9% | 17.9% | 18.0% | 17.8% | 9.7% |
| H_TIME | 18.7% | 17.9% | 17.9% | 17.9% | 17.8% | 9.7% |
| H1_original | 0.1% | 0.0% | 22.5% | 16.0% | 27.4% | 34.0% |
| H1_value_guard | 0.1% | 0.0% | 25.7% | 12.7% | 27.4% | 34.0% |
| H2_original | 0.1% | 0.0% | 25.7% | 12.7% | 27.4% | 34.0% |
| H2_value_guard | 0.3% | 0.0% | 25.7% | 12.7% | 27.4% | 33.9% |
| H3 | 24.1% | 0.0% | 25.7% | 0.0% | 27.4% | 22.8% |
| H4 | 13.7% | 17.9% | 13.7% | 18.2% | 13.7% | 22.8% |

## 5. Policy별 Avg Grade/Load 및 Effective Output

| Policy | Avg grade/load | Mean effective_output | Mean effective fulfillment | Mean TCO v1 | Mean TCO v2 base |
|---|---|---|---|---|---|
| H0 | 0.817 | 5,670,009.3 | 1.022 | 10,877.3 | 10,877.3 |
| H_TIME | 0.817 | 5,669,714.2 | 1.022 | 10,448.3 | 10,448.3 |
| H1_original | 0.733 | 5,086,697.0 | 0.916 | 5,832.1 | 9,158.6 |
| H1_value_guard | 0.733 | 5,087,758.7 | 0.916 | 5,829.4 | 9,148.3 |
| H2_original | 0.733 | 5,088,080.7 | 0.916 | 5,813.5 | 9,130.1 |
| H2_value_guard | 0.733 | 5,089,716.3 | 0.916 | 5,817.5 | 9,122.4 |
| H3 | 0.781 | 5,419,050.0 | 0.976 | 7,020.8 | 7,973.3 |
| H4 | 0.795 | 5,514,650.2 | 0.993 | 7,331.8 | 7,601.5 |

## 6. 기존 TCO 순위와 Grade-Aware TCO 순위 비교

| Regime | TCO v1 ranking top 4 | TCO v2 base ranking top 4 | v1 best | v2 best |
|---|---|---|---|---|
| heterogeneous_condition | H2_value_guard (4068.8) < H2_original (4072.0) < H1_value_guard (4080.9) < H1_original (4086.8) | H4 (5774.8) < H3 (6053.9) < H2_value_guard (7368.3) < H2_original (7380.8) | H2_value_guard | H4 |
| high_stress | H2_original (6100.5) < H2_value_guard (6106.4) < H1_original (6115.4) < H1_value_guard (6131.8) | H4 (7964.2) < H3 (8187.5) < H2_value_guard (9411.8) < H2_original (9419.3) | H2_original | H4 |
| high_demand_high_stress | H2_original (7267.9) < H1_value_guard (7275.4) < H2_value_guard (7277.2) < H1_original (7294.1) | H4 (9065.5) < H3 (9678.5) < H2_value_guard (10587.2) < H2_original (10590.2) | H2_original | H4 |

Base sensitivity에서는 기존 reliability-cost objective(v1)의 최상위가 H1/H2 계열인 반면, grade-aware objective(v2)는 모든 regime에서 H4가 최상위로 올라온다. 즉 reliability-cost 최적과 production-value-aware 최적이 분리된다.

## 7. Sensitivity별 순위 변화

| Regime | Sensitivity | TCO v2 ranking top 4 | Best policy |
|---|---|---|---|
| heterogeneous_condition | low | H4 (5639.8) < H3 (5693.9) < H2_value_guard (5718.3) < H2_original (5726.2) | H4 |
| heterogeneous_condition | base | H4 (5774.8) < H3 (6053.9) < H2_value_guard (7368.3) < H2_original (7380.8) | H4 |
| heterogeneous_condition | high | H4 (6044.8) < H3 (6773.9) < H_TIME (9262.9) < H0 (9769.8) | H4 |
| high_stress | low | H2_value_guard (7758.9) < H2_original (7759.7) < H1_original (7778.4) < H1_value_guard (7792.1) | H2_value_guard |
| high_stress | base | H4 (7964.2) < H3 (8187.5) < H2_value_guard (9411.8) < H2_original (9419.3) | H4 |
| high_stress | high | H4 (8234.3) < H3 (8907.5) < H_TIME (10582.9) < H0 (11011.1) | H4 |
| high_demand_high_stress | low | H2_original (8928.9) < H4 (8931.1) < H2_value_guard (8932.0) < H1_value_guard (8936.6) | H2_original |
| high_demand_high_stress | base | H4 (9065.5) < H3 (9678.5) < H2_value_guard (10587.2) < H2_original (10590.2) | H4 |
| high_demand_high_stress | high | H4 (9334.3) < H3 (11096.1) < H_TIME (11499.2) < H0 (11851.0) | H4 |

Low sensitivity에서는 high_stress와 high_demand_high_stress에서 H2 계열이 여전히 경쟁력이 있다. Base/high sensitivity에서는 output shortfall penalty가 커져 H4 또는 H3가 H1/H2보다 우위로 이동한다.

## 8. H1/H2 Original vs Value Guard

| Regime | Policy | Effective fulfill | Avg grade/load | Effective output | TCO v1 | TCO v2 base | Shovel C share |
|---|---|---|---|---|---|---|---|
| heterogeneous_condition | H1_original | 0.912 | 0.730 | 4,826,381.0 | 4,086.8 | 7,412.7 | 70.5% |
| heterogeneous_condition | H1_value_guard | 0.912 | 0.730 | 4,828,208.0 | 4,080.9 | 7,393.8 | 70.3% |
| heterogeneous_condition | H2_original | 0.912 | 0.730 | 4,828,775.0 | 4,072.0 | 7,380.8 | 70.3% |
| heterogeneous_condition | H2_value_guard | 0.913 | 0.730 | 4,830,091.0 | 4,068.8 | 7,368.3 | 70.2% |
| high_stress | H1_original | 0.912 | 0.730 | 4,826,314.5 | 6,115.4 | 9,441.8 | 70.5% |
| high_stress | H1_value_guard | 0.912 | 0.730 | 4,827,060.0 | 6,131.8 | 9,452.9 | 70.4% |
| high_stress | H2_original | 0.912 | 0.730 | 4,827,382.0 | 6,100.5 | 9,419.3 | 70.4% |
| high_stress | H2_value_guard | 0.913 | 0.730 | 4,829,251.0 | 6,106.4 | 9,411.8 | 70.2% |
| high_demand_high_stress | H1_original | 0.923 | 0.739 | 5,607,395.5 | 7,294.1 | 10,621.3 | 61.4% |
| high_demand_high_stress | H1_value_guard | 0.923 | 0.739 | 5,608,008.0 | 7,275.4 | 10,598.2 | 61.4% |
| high_demand_high_stress | H2_original | 0.923 | 0.739 | 5,608,085.0 | 7,267.9 | 10,590.2 | 61.4% |
| high_demand_high_stress | H2_value_guard | 0.924 | 0.739 | 5,609,807.0 | 7,277.2 | 10,587.2 | 61.3% |

Value-guard variant는 이 설정에서는 H1/H2의 route mix를 크게 바꾸지 못했다. H1/H2_value_guard는 original보다 약간 낮은 v1/v2를 보이는 경우가 있지만, avg grade/load와 effective fulfillment는 거의 동일하다. 현재 value_guard weight는 production-value optimum을 H3/H4 수준으로 이동시키기에는 약하다.

## 9. H1/H2가 여전히 최상위인지

- 기존 TCO v1 기준: H1/H2 계열이 여전히 최상위다. 이는 C5.51과 같은 reliability-cost 결과다.
- Grade-aware TCO v2 low sensitivity: 일부 regime에서는 H2 계열이 여전히 최상위 또는 매우 근접하다.
- Grade-aware TCO v2 base sensitivity: H4가 모든 regime에서 최상위로 이동한다.
- Grade-aware TCO v2 high sensitivity: H4가 더 명확하게 최상위가 되고, H3도 H1/H2보다 우위로 이동한다.

따라서 H1/H2의 우위는 effective output shortfall을 얼마나 강하게 비용화하느냐에 민감하다. C5.52 base/high에서는 H1/H2의 low-grade route 집중이 목적함수상 약점으로 드러난다.

## 10. 결론: Reliability-Cost 최적과 Production-Value 최적은 같은가

C5.52 결과에서는 두 최적점이 다르다.

- Reliability-cost 최적: H1/H2 계열. failure, CM, downtime을 낮추기 위해 low-risk / low-grade route를 많이 선택한다.
- Production-value-aware 최적: base/high sensitivity에서는 H4, 일부 조건에서는 H3. 더 높은 effective output 또는 더 균형 잡힌 grade mix를 확보한다.

즉 C5.51의 낮은 TCO 결론은 reliability-cost 관점에서는 타당하지만, grade-adjusted production value를 명시적으로 반영하면 정책 순위가 바뀐다. C5.52는 이 목적함수 차이를 분리해서 보여주는 실험 모듈로 유지하는 것이 적절하다.
