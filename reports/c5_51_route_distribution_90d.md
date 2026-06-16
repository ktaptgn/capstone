# C5.51 90-Day Route Distribution Audit

## 데이터 범위

- 입력 파일: `outputs/c5_51/summary/c5_51_policy_comparison.csv`
- 행 수: 180
- 범위: 90 days, 3 regimes, 6 policies, seeds 101-110 (10 seeds)
- 아래 share는 각 policy x regime 그룹 안에서 10개 seed의 completed load를 합산한 load-weighted share다.

## 핵심 결론

- H1/H2는 모든 regime에서 low-risk / low-grade 계열인 C route로 강하게 몰린다. Shovel C share가 대체로 약 70% 수준이다.
- H2는 특히 집중도가 높다. R_C1/R_C2와 R_B1을 거의 대부분 사용하고, R_A2/R_B2는 사실상 사용하지 않는다.
- H1도 C route 중심이지만 H2보다 B2를 약간 더 사용한다.
- 이 route mix 때문에 H1/H2는 fulfillment를 유지하더라도 평균 grade/load와 `effective_output`이 H0/H_TIME/H3/H4보다 낮다.
- 현재 C5.51 TCO에는 `effective_output` 손실이 직접 반영되지 않는다. 따라서 TCO 순위와 grade-adjusted production 성과를 분리해서 해석해야 한다.

## Regime: `heterogeneous_condition`

### 1. Policy별 Route Share
| Policy | R_A1 | R_A2 | R_B1 | R_B2 | R_C1 | R_C2 |
|---|---|---|---|---|---|---|
| H0 | 22.0% | 21.9% | 21.9% | 11.8% | 11.6% | 10.7% |
| H_TIME | 21.9% | 22.0% | 22.0% | 11.7% | 11.7% | 10.8% |
| H1 | 0.1% | 0.0% | 18.8% | 10.6% | 31.4% | 39.0% |
| H2 | 0.2% | 0.0% | 29.5% | 0.0% | 31.4% | 38.8% |
| H3 | 27.6% | 0.0% | 29.5% | 0.0% | 31.4% | 11.4% |
| H4 | 12.9% | 17.1% | 12.9% | 21.4% | 14.3% | 21.4% |

### 2. Policy별 Shovel Share
| Policy | A | B | C |
|---|---|---|---|
| H0 | 43.9% | 33.7% | 22.4% |
| H_TIME | 43.9% | 33.7% | 22.5% |
| H1 | 0.1% | 29.4% | 70.5% |
| H2 | 0.2% | 29.5% | 70.3% |
| H3 | 27.6% | 29.5% | 42.9% |
| H4 | 30.0% | 34.3% | 35.7% |

### 3. Policy별 Crusher Share
| Policy | Crusher1 | Crusher2 |
|---|---|---|
| H0 | 55.5% | 44.5% |
| H_TIME | 55.6% | 44.4% |
| H1 | 50.3% | 49.7% |
| H2 | 61.2% | 38.8% |
| H3 | 88.6% | 11.4% |
| H4 | 40.0% | 60.0% |

### Effective Output 연결 지표
| Policy | Fulfillment | Mean effective_output | Avg grade/load | Shovel C share | Mean TCO |
|---|---|---|---|---|---|
| H0 | 1.000 | 5,433,967.0 | 0.822 | 22.4% | 9,769.8 |
| H_TIME | 1.000 | 5,433,662.5 | 0.821 | 22.5% | 9,262.9 |
| H1 | 1.000 | 4,826,381.0 | 0.730 | 70.5% | 4,086.8 |
| H2 | 1.000 | 4,828,775.0 | 0.730 | 70.3% | 4,072.0 |
| H3 | 1.000 | 5,191,200.0 | 0.785 | 42.9% | 5,333.9 |
| H4 | 1.000 | 5,254,200.0 | 0.794 | 35.7% | 5,504.8 |

## Regime: `high_stress`

### 1. Policy별 Route Share
| Policy | R_A1 | R_A2 | R_B1 | R_B2 | R_C1 | R_C2 |
|---|---|---|---|---|---|---|
| H0 | 21.9% | 21.9% | 21.9% | 11.9% | 11.6% | 10.8% |
| H_TIME | 21.9% | 21.9% | 22.0% | 11.7% | 11.7% | 10.8% |
| H1 | 0.1% | 0.0% | 18.6% | 10.8% | 31.4% | 39.0% |
| H2 | 0.1% | 0.0% | 29.5% | 0.0% | 31.4% | 38.9% |
| H3 | 27.6% | 0.0% | 29.5% | 0.0% | 31.4% | 11.4% |
| H4 | 12.9% | 17.1% | 12.9% | 21.4% | 14.3% | 21.4% |

### 2. Policy별 Shovel Share
| Policy | A | B | C |
|---|---|---|---|
| H0 | 43.8% | 33.8% | 22.4% |
| H_TIME | 43.8% | 33.7% | 22.5% |
| H1 | 0.1% | 29.4% | 70.5% |
| H2 | 0.1% | 29.5% | 70.4% |
| H3 | 27.6% | 29.5% | 42.9% |
| H4 | 30.0% | 34.3% | 35.7% |

### 3. Policy별 Crusher Share
| Policy | Crusher1 | Crusher2 |
|---|---|---|
| H0 | 55.5% | 44.5% |
| H_TIME | 55.6% | 44.4% |
| H1 | 50.1% | 49.9% |
| H2 | 61.1% | 38.9% |
| H3 | 88.6% | 11.4% |
| H4 | 40.0% | 60.0% |

### Effective Output 연결 지표
| Policy | Fulfillment | Mean effective_output | Avg grade/load | Shovel C share | Mean TCO |
|---|---|---|---|---|---|
| H0 | 1.000 | 5,433,218.0 | 0.821 | 22.4% | 11,011.1 |
| H_TIME | 1.000 | 5,433,001.0 | 0.821 | 22.5% | 10,582.9 |
| H1 | 1.000 | 4,826,314.5 | 0.730 | 70.5% | 6,115.4 |
| H2 | 1.000 | 4,827,382.0 | 0.730 | 70.4% | 6,100.5 |
| H3 | 1.000 | 5,191,200.0 | 0.785 | 42.9% | 7,467.5 |
| H4 | 1.000 | 5,254,182.5 | 0.794 | 35.7% | 7,694.0 |

## Regime: `high_demand_high_stress`

### 1. Policy별 Route Share
| Policy | R_A1 | R_A2 | R_B1 | R_B2 | R_C1 | R_C2 |
|---|---|---|---|---|---|---|
| H0 | 18.8% | 17.9% | 17.9% | 18.0% | 17.8% | 9.7% |
| H_TIME | 18.7% | 17.9% | 17.9% | 17.9% | 17.8% | 9.7% |
| H1 | 0.1% | 0.0% | 22.5% | 16.0% | 27.4% | 34.0% |
| H2 | 0.1% | 0.0% | 25.7% | 12.7% | 27.4% | 34.0% |
| H3 | 24.1% | 0.0% | 25.7% | 0.0% | 27.4% | 22.8% |
| H4 | 13.7% | 17.9% | 13.7% | 18.2% | 13.7% | 22.8% |

### 2. Policy별 Shovel Share
| Policy | A | B | C |
|---|---|---|---|
| H0 | 36.7% | 35.9% | 27.5% |
| H_TIME | 36.7% | 35.8% | 27.5% |
| H1 | 0.1% | 38.5% | 61.4% |
| H2 | 0.1% | 38.4% | 61.4% |
| H3 | 24.1% | 25.7% | 50.2% |
| H4 | 31.6% | 31.9% | 36.5% |

### 3. Policy별 Crusher Share
| Policy | Crusher1 | Crusher2 |
|---|---|---|
| H0 | 54.5% | 45.5% |
| H_TIME | 54.5% | 45.5% |
| H1 | 50.0% | 50.0% |
| H2 | 53.3% | 46.7% |
| H3 | 77.2% | 22.8% |
| H4 | 41.1% | 58.9% |

### Effective Output 연결 지표
| Policy | Fulfillment | Mean effective_output | Avg grade/load | Shovel C share | Mean TCO |
|---|---|---|---|---|---|
| H0 | 1.000 | 6,142,843.0 | 0.809 | 27.5% | 11,851.0 |
| H_TIME | 1.000 | 6,142,479.0 | 0.809 | 27.5% | 11,499.2 |
| H1 | 1.000 | 5,607,395.5 | 0.739 | 61.4% | 7,294.1 |
| H2 | 1.000 | 5,608,085.0 | 0.739 | 61.4% | 7,267.9 |
| H3 | 1.000 | 5,874,750.0 | 0.774 | 50.2% | 8,261.0 |
| H4 | 1.000 | 6,035,568.0 | 0.795 | 36.5% | 8,796.7 |

## 4. Regime별 변화

| Policy | Shovel C share 변화 | Avg grade/load 변화 | Mean effective_output 변화 |
|---|---|---|---|
| H0 | 22.4% -> 22.4% -> 27.5% | 0.822 -> 0.821 -> 0.809 | 5,433,967.0 -> 5,433,218.0 -> 6,142,843.0 |
| H_TIME | 22.5% -> 22.5% -> 27.5% | 0.821 -> 0.821 -> 0.809 | 5,433,662.5 -> 5,433,001.0 -> 6,142,479.0 |
| H1 | 70.5% -> 70.5% -> 61.4% | 0.730 -> 0.730 -> 0.739 | 4,826,381.0 -> 4,826,314.5 -> 5,607,395.5 |
| H2 | 70.3% -> 70.4% -> 61.4% | 0.730 -> 0.730 -> 0.739 | 4,828,775.0 -> 4,827,382.0 -> 5,608,085.0 |
| H3 | 42.9% -> 42.9% -> 50.2% | 0.785 -> 0.785 -> 0.774 | 5,191,200.0 -> 5,191,200.0 -> 5,874,750.0 |
| H4 | 35.7% -> 35.7% -> 36.5% | 0.794 -> 0.794 -> 0.795 | 5,254,200.0 -> 5,254,182.5 -> 6,035,568.0 |

해석: route 선택 분포는 regime이 바뀌어도 크게 흔들리지 않는다. High-stress 계열은 비용, failure, downtime에는 영향을 주지만, 현재 C5.51 정책 scoring과 route capacity 구조에서는 route preference 자체를 크게 바꾸지는 않는다.

## 5. H1/H2가 Low-Risk, Low-Grade Route로 과도하게 몰리는지

| Regime | Policy | R_C1+R_C2 | B/C routes | A routes | Avg grade/load | Mean effective_output | 과도 집중 여부 |
|---|---|---|---|---|---|---|---|
| heterogeneous_condition | H1 | 70.5% | 99.9% | 0.1% | 0.730 | 4,826,381.0 | Yes |
| heterogeneous_condition | H2 | 70.3% | 99.8% | 0.2% | 0.730 | 4,828,775.0 | Yes |
| high_stress | H1 | 70.5% | 99.9% | 0.1% | 0.730 | 4,826,314.5 | Yes |
| high_stress | H2 | 70.4% | 99.9% | 0.1% | 0.730 | 4,827,382.0 | Yes |
| high_demand_high_stress | H1 | 61.4% | 99.9% | 0.1% | 0.739 | 5,607,395.5 | Partial |
| high_demand_high_stress | H2 | 61.4% | 99.9% | 0.1% | 0.739 | 5,608,085.0 | Partial |

판정: H1/H2는 low-risk, low-grade route로 명확하게 몰린다. 모든 regime에서 C route share가 약 69-70%이고, B/C route까지 합치면 거의 전체 load를 차지한다. 특히 H2는 A route를 약 1% 미만으로만 사용한다.

## 6. Route Share와 Effective Output의 관계

C5.51의 `effective_output`은 completed load마다 다음 방식으로 계산된다.

```text
effective_output += payload_ton * route.grade_index
```

payload가 350으로 고정이므로 route grade mix가 effective_output을 결정한다.

- A route: 350 x 0.90 = 315 effective units/load
- B route: 350 x 0.80 = 280 effective units/load
- C route: 350 x 0.70 = 245 effective units/load

| Policy | A share | B share | C share | Avg grade/load | Mean effective_output | Mean TCO |
|---|---|---|---|---|---|---|
| H0 | 41.2% | 34.5% | 24.3% | 0.817 | 5,670,009.3 | 10,877.3 |
| H_TIME | 41.2% | 34.5% | 24.3% | 0.817 | 5,669,714.2 | 10,448.3 |
| H1 | 0.1% | 32.8% | 67.2% | 0.733 | 5,086,697.0 | 5,832.1 |
| H2 | 0.2% | 32.8% | 67.1% | 0.733 | 5,088,080.7 | 5,813.5 |
| H3 | 26.3% | 28.1% | 45.5% | 0.781 | 5,419,050.0 | 7,020.8 |
| H4 | 30.6% | 33.4% | 36.0% | 0.795 | 5,514,650.2 | 7,331.8 |

관계: A share가 높을수록 평균 grade/load와 effective_output이 올라간다. C share가 높을수록 effective_output은 낮아진다. H1/H2는 failure, CM, downtime, degradation을 낮춰 TCO에서 유리하지만, route mix 관점에서는 grade-adjusted output을 희생한다.

## 최종 진단

C5.51 90-day intermediate run에서 H1/H2는 load-count fulfillment를 유지하지만, route 선택은 low-risk / low-grade C route에 강하게 집중된다. 따라서 H1/H2의 낮은 TCO를 해석할 때 `effective_output`을 반드시 병렬 KPI로 봐야 한다. 현재 objective에는 effective_output 손실이 직접 들어가지 않으므로, TCO 단독 순위는 production quality/grade trade-off를 충분히 설명하지 못한다.

추천 후속 작업: C5.51 코드를 바로 수정하기보다, 먼저 TCO 순위와 effective_output 순위를 나란히 보여주는 comparison report 또는 output-adjusted objective sensitivity를 별도 실험으로 추가하는 것이 좋다.
