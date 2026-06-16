# C5.51 90-Day TCO Breakdown Audit

## 데이터 범위

- 입력 파일: `outputs/c5_51/summary/c5_51_policy_comparison.csv`
- 행 수: 180
- 범위: 90 days, regimes `heterogeneous_condition, high_stress, high_demand_high_stress`, policies `H0, H_TIME, H1, H2, H3, H4`, seeds 101-110 (10 seeds)
- 모든 값은 policy x regime 그룹의 10개 seed 평균이다.

## 핵심 결론

- H1/H2의 낮은 TCO는 `CM cost = 0`, `failure_count = 0`, 낮은 downtime, 낮은 PM activity가 결합된 결과다.
- H3/H4도 failure/CM은 낮거나 0이지만, PM visits와 downtime이 H1/H2보다 훨씬 커서 TCO가 높다.
- H0/H_TIME은 full-service blind PM 구조 때문에 PM cost와 downtime이 크고, 여기에 CM/failure 비용이 추가되어 TCO를 끌어올린다.
- `effective_output`은 TCO 구성항목에 들어가지 않는다. 따라서 H1/H2가 낮은 grade route를 선택해 effective_output이 낮아도 TCO에는 직접 벌점이 없다.
- Unmet demand cost는 대부분 0 또는 매우 작다. 90-day 결과에서 TCO 차이는 fulfillment가 아니라 PM/CM/downtime/degradation 구조가 만든다.

## Regime: `heterogeneous_condition`

### 1. Policy별 평균 TCO Breakdown
| Policy | Total TCO | PM | CM | Downtime | Degradation | Unmet |
|---|---|---|---|---|---|---|
| H0 | 9,769.8 | 3,349.0 | 475.1 | 5,767.1 | 176.3 | 2.4 |
| H_TIME | 9,262.9 | 3,298.0 | 303.5 | 5,484.7 | 176.1 | 0.6 |
| H1 | 4,086.8 | 1,575.5 | 0.0 | 2,372.9 | 138.4 | 0.0 |
| H2 | 4,072.0 | 1,568.5 | 0.0 | 2,364.8 | 138.6 | 0.0 |
| H3 | 5,333.9 | 2,069.4 | 0.0 | 3,099.7 | 164.7 | 0.0 |
| H4 | 5,504.8 | 2,143.8 | 0.0 | 3,191.4 | 169.6 | 0.0 |

### 2. 비용항목별 TCO 비중
| Policy | PM share | CM share | Downtime share | Degradation share | Unmet share |
|---|---|---|---|---|---|
| H0 | 34.3% | 4.9% | 59.0% | 1.8% | 0.0% |
| H_TIME | 35.6% | 3.3% | 59.2% | 1.9% | 0.0% |
| H1 | 38.6% | 0.0% | 58.1% | 3.4% | 0.0% |
| H2 | 38.5% | 0.0% | 58.1% | 3.4% | 0.0% |
| H3 | 38.8% | 0.0% | 58.1% | 3.1% | 0.0% |
| H4 | 38.9% | 0.0% | 58.0% | 3.1% | 0.0% |

### 3. 원인 진단 지표
| Policy | Fulfillment | Effective output | Avg grade/load | Shovel C share | Failures | CM count | PM visits | Downtime hours |
|---|---|---|---|---|---|---|---|---|
| H0 | 1.000 | 5,433,967.0 | 0.822 | 22.4% | 45.2 | 45.2 | 394.0 | 4,805.9 |
| H_TIME | 1.000 | 5,433,662.5 | 0.821 | 22.5% | 29.8 | 29.8 | 388.0 | 4,570.6 |
| H1 | 1.000 | 4,826,381.0 | 0.730 | 70.5% | 0.0 | 0.0 | 567.7 | 1,977.4 |
| H2 | 1.000 | 4,828,775.0 | 0.730 | 70.3% | 0.0 | 0.0 | 564.1 | 1,970.7 |
| H3 | 1.000 | 5,191,200.0 | 0.785 | 42.9% | 0.0 | 0.0 | 736.6 | 2,583.1 |
| H4 | 1.000 | 5,254,200.0 | 0.794 | 35.7% | 0.0 | 0.0 | 757.9 | 2,659.5 |

## Regime: `high_stress`

### 1. Policy별 평균 TCO Breakdown
| Policy | Total TCO | PM | CM | Downtime | Degradation | Unmet |
|---|---|---|---|---|---|---|
| H0 | 11,011.1 | 3,060.0 | 935.4 | 6,794.6 | 217.8 | 3.4 |
| H_TIME | 10,582.9 | 3,026.0 | 793.9 | 6,543.7 | 217.7 | 1.6 |
| H1 | 6,115.4 | 2,096.2 | 0.0 | 3,841.6 | 177.5 | 0.0 |
| H2 | 6,100.5 | 2,090.8 | 0.0 | 3,831.8 | 177.9 | 0.0 |
| H3 | 7,467.5 | 2,575.4 | 0.0 | 4,689.8 | 202.3 | 0.0 |
| H4 | 7,694.0 | 2,659.6 | 4.3 | 4,822.1 | 208.1 | 0.0 |

### 2. 비용항목별 TCO 비중
| Policy | PM share | CM share | Downtime share | Degradation share | Unmet share |
|---|---|---|---|---|---|
| H0 | 27.8% | 8.5% | 61.7% | 2.0% | 0.0% |
| H_TIME | 28.6% | 7.5% | 61.8% | 2.1% | 0.0% |
| H1 | 34.3% | 0.0% | 62.8% | 2.9% | 0.0% |
| H2 | 34.3% | 0.0% | 62.8% | 2.9% | 0.0% |
| H3 | 34.5% | 0.0% | 62.8% | 2.7% | 0.0% |
| H4 | 34.6% | 0.1% | 62.7% | 2.7% | 0.0% |

### 3. 원인 진단 지표
| Policy | Fulfillment | Effective output | Avg grade/load | Shovel C share | Failures | CM count | PM visits | Downtime hours |
|---|---|---|---|---|---|---|---|---|
| H0 | 1.000 | 5,433,218.0 | 0.821 | 22.4% | 82.2 | 82.2 | 360.0 | 5,226.6 |
| H_TIME | 1.000 | 5,433,001.0 | 0.821 | 22.5% | 71.4 | 71.4 | 356.0 | 5,033.6 |
| H1 | 1.000 | 4,826,314.5 | 0.730 | 70.5% | 0.0 | 0.0 | 752.5 | 2,955.1 |
| H2 | 1.000 | 4,827,382.0 | 0.730 | 70.4% | 0.0 | 0.0 | 749.7 | 2,947.5 |
| H3 | 1.000 | 5,191,200.0 | 0.785 | 42.9% | 0.0 | 0.0 | 873.0 | 3,607.5 |
| H4 | 1.000 | 5,254,182.5 | 0.794 | 35.7% | 0.4 | 0.4 | 867.5 | 3,709.3 |

## Regime: `high_demand_high_stress`

### 1. Policy별 평균 TCO Breakdown
| Policy | Total TCO | PM | CM | Downtime | Degradation | Unmet |
|---|---|---|---|---|---|---|
| H0 | 11,851.0 | 3,060.0 | 1,288.4 | 7,261.1 | 241.4 | 0.0 |
| H_TIME | 11,499.2 | 3,026.0 | 1,187.0 | 7,044.8 | 241.3 | 0.0 |
| H1 | 7,294.1 | 2,500.1 | 7.3 | 4,579.0 | 207.8 | 0.0 |
| H2 | 7,267.9 | 2,491.0 | 7.3 | 4,562.0 | 207.7 | 0.0 |
| H3 | 8,261.0 | 2,803.1 | 67.5 | 5,166.5 | 224.0 | 0.0 |
| H4 | 8,796.7 | 2,911.6 | 188.0 | 5,462.2 | 234.9 | 0.0 |

### 2. 비용항목별 TCO 비중
| Policy | PM share | CM share | Downtime share | Degradation share | Unmet share |
|---|---|---|---|---|---|
| H0 | 25.8% | 10.9% | 61.3% | 2.0% | 0.0% |
| H_TIME | 26.3% | 10.3% | 61.3% | 2.1% | 0.0% |
| H1 | 34.3% | 0.1% | 62.8% | 2.8% | 0.0% |
| H2 | 34.3% | 0.1% | 62.8% | 2.9% | 0.0% |
| H3 | 33.9% | 0.8% | 62.5% | 2.7% | 0.0% |
| H4 | 33.1% | 2.1% | 62.1% | 2.7% | 0.0% |

### 3. 원인 진단 지표
| Policy | Fulfillment | Effective output | Avg grade/load | Shovel C share | Failures | CM count | PM visits | Downtime hours |
|---|---|---|---|---|---|---|---|---|
| H0 | 1.000 | 6,142,843.0 | 0.809 | 27.5% | 111.6 | 111.6 | 360.0 | 5,585.5 |
| H_TIME | 1.000 | 6,142,479.0 | 0.809 | 27.5% | 105.4 | 105.4 | 356.0 | 5,419.1 |
| H1 | 1.000 | 5,607,395.5 | 0.739 | 61.4% | 0.7 | 0.7 | 874.0 | 3,522.3 |
| H2 | 1.000 | 5,608,085.0 | 0.739 | 61.4% | 0.7 | 0.7 | 872.0 | 3,509.2 |
| H3 | 1.000 | 5,874,750.0 | 0.774 | 50.2% | 5.8 | 5.8 | 852.7 | 3,974.2 |
| H4 | 1.000 | 6,035,568.0 | 0.795 | 36.5% | 17.6 | 17.6 | 787.2 | 4,201.7 |

## H1/H2가 왜 낮은 TCO인지

| Regime | Policy | TCO | PM | CM | Downtime | Degradation | Failures | PM visits | Shovel C share | Effective output |
|---|---|---|---|---|---|---|---|---|---|---|
| heterogeneous_condition | H1 | 4,086.8 | 1,575.5 | 0.0 | 2,372.9 | 138.4 | 0.0 | 567.7 | 70.5% | 4,826,381.0 |
| heterogeneous_condition | H2 | 4,072.0 | 1,568.5 | 0.0 | 2,364.8 | 138.6 | 0.0 | 564.1 | 70.3% | 4,828,775.0 |
| high_stress | H1 | 6,115.4 | 2,096.2 | 0.0 | 3,841.6 | 177.5 | 0.0 | 752.5 | 70.5% | 4,826,314.5 |
| high_stress | H2 | 6,100.5 | 2,090.8 | 0.0 | 3,831.8 | 177.9 | 0.0 | 749.7 | 70.4% | 4,827,382.0 |
| high_demand_high_stress | H1 | 7,294.1 | 2,500.1 | 7.3 | 4,579.0 | 207.8 | 0.7 | 874.0 | 61.4% | 5,607,395.5 |
| high_demand_high_stress | H2 | 7,267.9 | 2,491.0 | 7.3 | 4,562.0 | 207.7 | 0.7 | 872.0 | 61.4% | 5,608,085.0 |

진단: H1/H2는 C route 중심의 low-risk dispatch 때문에 component wear와 failure exposure를 줄인다. 그 결과 CM cost가 0이고 downtime도 낮다. 또한 H3/H4보다 PM visits가 적어 PM cost와 PM downtime도 낮다. 현재 objective는 grade-adjusted output 손실을 직접 비용으로 보지 않으므로, H1/H2의 낮은 effective_output은 TCO를 올리지 않는다.

## H3/H4가 Failure는 낮은데 TCO가 높은 이유

| Regime | Policy | TCO | Failures | PM cost | Downtime cost | PM visits | TCO gap vs H2 | Effective output gain vs H2 |
|---|---|---|---|---|---|---|---|---|
| heterogeneous_condition | H3 | 5,333.9 | 0.0 | 2,069.4 | 3,099.7 | 736.6 | 1,261.9 | 362,425.0 |
| heterogeneous_condition | H4 | 5,504.8 | 0.0 | 2,143.8 | 3,191.4 | 757.9 | 1,432.8 | 425,425.0 |
| high_stress | H3 | 7,467.5 | 0.0 | 2,575.4 | 4,689.8 | 873.0 | 1,366.9 | 363,818.0 |
| high_stress | H4 | 7,694.0 | 0.4 | 2,659.6 | 4,822.1 | 867.5 | 1,593.5 | 426,800.5 |
| high_demand_high_stress | H3 | 8,261.0 | 5.8 | 2,803.1 | 5,166.5 | 852.7 | 993.1 | 266,665.0 |
| high_demand_high_stress | H4 | 8,796.7 | 17.6 | 2,911.6 | 5,462.2 | 787.2 | 1,528.7 | 427,483.0 |

진단: H3/H4는 failure를 잘 억제하지만, H1/H2보다 PM visits가 많고 downtime cost가 크다. 특히 H3/H4의 추가 effective_output은 현재 TCO에서 수익 또는 credit으로 반영되지 않기 때문에, output gain이 있어도 TCO gap을 상쇄하지 못한다.

## H0/H_TIME에서 Failure/CM/Downtime이 TCO를 얼마나 끌어올리는지

| Regime | Policy | TCO | Failures | CM cost | Downtime cost | CM+Downtime | CM+Downtime share | PM+CM+Downtime | Maint/downtime share |
|---|---|---|---|---|---|---|---|---|---|
| heterogeneous_condition | H0 | 9,769.8 | 45.2 | 475.1 | 5,767.1 | 6,242.2 | 63.9% | 9,591.2 | 98.2% |
| heterogeneous_condition | H_TIME | 9,262.9 | 29.8 | 303.5 | 5,484.7 | 5,788.2 | 62.5% | 9,086.2 | 98.1% |
| high_stress | H0 | 11,011.1 | 82.2 | 935.4 | 6,794.6 | 7,729.9 | 70.2% | 10,789.9 | 98.0% |
| high_stress | H_TIME | 10,582.9 | 71.4 | 793.9 | 6,543.7 | 7,337.6 | 69.3% | 10,363.6 | 97.9% |
| high_demand_high_stress | H0 | 11,851.0 | 111.6 | 1,288.4 | 7,261.1 | 8,549.6 | 72.1% | 11,609.6 | 98.0% |
| high_demand_high_stress | H_TIME | 11,499.2 | 105.4 | 1,187.0 | 7,044.8 | 8,231.9 | 71.6% | 11,257.9 | 97.9% |

진단: H0/H_TIME은 CM cost 자체보다 downtime cost가 훨씬 큰 TCO driver다. Blind full-service PM이 PM cost와 downtime을 크게 만들고, 남는 failure/CM이 추가 downtime을 만든다. 따라서 H0/H_TIME의 높은 TCO는 단순 CM 비용보다 PM bay occupation과 downtime 누적의 영향이 더 크다.

## Effective Output이 TCO에 충분히 반영되는지

현재 C5.51 TCO는 다음 항목의 합이다.

```text
total_tco = pm_cost + cm_cost + downtime_cost + degradation_cost + unmet_demand_cost
```

`effective_output`은 별도 KPI로 저장되지만, 위 합계에 포함되지 않는다. 따라서 높은 output은 TCO를 낮추는 credit이 아니고, 낮은 output은 TCO를 높이는 penalty도 아니다.

| Policy | Mean TCO across regimes | Mean effective_output | Avg grade/load |
|---|---|---|---|
| H0 | 10,877.3 | 5,670,009.3 | 0.817 |
| H_TIME | 10,448.3 | 5,669,714.2 | 0.817 |
| H1 | 5,832.1 | 5,086,697.0 | 0.733 |
| H2 | 5,813.5 | 5,088,080.7 | 0.733 |
| H3 | 7,020.8 | 5,419,050.0 | 0.781 |
| H4 | 7,331.8 | 5,514,650.2 | 0.795 |

해석: H1/H2는 가장 낮은 TCO 그룹이지만 effective_output은 낮은 편이다. 반대로 H0/H_TIME은 effective_output이 높지만 TCO도 높다. 이는 effective_output이 현재 objective에 충분히 반영되지 않는다는 강한 증거다. 정확히는 "충분히"가 아니라 "직접 반영되지 않는다"가 현재 코드 기준의 결론이다.

## 종합 결론

C5.51 90-day intermediate run에서 H1/H2가 낮은 TCO를 보이는 주된 이유는 low-risk route 선택으로 failure/CM/downtime을 억제하고 PM 횟수도 상대적으로 낮게 유지하기 때문이다. H3/H4는 failure를 억제하지만 PM과 downtime이 더 크기 때문에 TCO가 높다. H0/H_TIME은 blind PM과 남는 failure가 downtime을 크게 만들면서 TCO가 가장 높다.

다만 H1/H2의 낮은 TCO는 grade-adjusted production 관점의 우월성을 의미하지 않는다. H1/H2는 low-grade C route 비중이 높아 effective_output이 낮고, 현재 TCO에는 이 손실이 직접 들어가지 않는다. 따라서 C5.51 결과를 발표할 때는 TCO ranking과 effective_output ranking을 반드시 함께 제시해야 한다.
