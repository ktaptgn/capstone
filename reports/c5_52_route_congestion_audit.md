# C5.52 Route / Facility Congestion Audit

## 데이터와 한계

- 입력 summary: `outputs/c5_52/summary/c5_52_policy_comparison.csv`
- 설정 파일: `configs/c5_52.yaml`
- 분석 범위: C5.52 90-day, 10 seeds, 3 regimes, base shortfall sensitivity 기준
- C5.52 summary에는 route/facility load counts, `avg_selected_queue_penalty`, `avg_selected_capacity_score`는 있다.
- 하지만 실제 `queue_hours`, realized waiting time, realized cycle time, shovel/crusher queue length는 로그되지 않는다.
- 따라서 아래의 route utilization은 route capacity 대비 load count 기준이며, shovel/crusher utilization은 derived facility load 대비 facility capacity proxy다. C5.51/52 simulator는 route capacity만 직접 제한하고 shovel/crusher facility capacity를 별도 constraint로 강제하지 않는다.

## 핵심 결론

- H1/H2의 C route 집중은 실제 route capacity 관점에서는 R_C1/R_C2를 거의 포화시키는 강한 route bottleneck 패턴이다.
- 하지만 현재 simulator는 route capacity 소진 시 다른 route로 fallback할 뿐, queue hours나 cycle time 증가를 직접 발생시키지 않는다. 따라서 “실제 queue bottleneck”은 현재 로그만으로 확정할 수 없다.
- H1/H2의 Shovel C derived utilization은 100%를 크게 넘는다. 이는 실제 시설 병목이라기보다, route-level simulator가 shovel capacity를 별도 constraint로 강제하지 않는다는 모델링 한계를 드러낸다.
- H4는 route share를 넓게 분산하여 HHI와 max route share를 낮춘다. 그러나 weighted cycle time proxy는 H1/H2보다 높다. H4의 이득은 현재 로그상 queue/cycle time 이득이라기보다 effective output shortfall 감소와 route/facility 분산에서 나온다.
- C route 집중은 effective output을 낮춘다. H1/H2는 low-risk route 선택으로 reliability cost는 낮추지만, avg grade/load와 effective fulfillment가 낮다.

## Regime: `heterogeneous_condition`

### 1. Policy x Regime Route Share
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

### 2. Shovel Utilization Proxy
| Policy | A share | A util | B share | B util | C share | C util |
|---|---|---|---|---|---|---|
| H0 | 43.9% | 128.0% | 33.7% | 94.4% | 22.4% | 56.0% |
| H_TIME | 43.9% | 128.0% | 33.7% | 94.3% | 22.5% | 56.1% |
| H1_original | 0.1% | 0.3% | 29.4% | 82.4% | 70.5% | 176.2% |
| H1_value_guard | 0.2% | 0.5% | 29.5% | 82.7% | 70.3% | 175.7% |
| H2_original | 0.2% | 0.7% | 29.5% | 82.7% | 70.3% | 175.6% |
| H2_value_guard | 0.3% | 0.9% | 29.5% | 82.7% | 70.2% | 175.4% |
| H3 | 27.6% | 80.6% | 29.5% | 82.7% | 42.9% | 107.1% |
| H4 | 30.0% | 87.5% | 34.3% | 96.0% | 35.7% | 89.3% |

### 3. Crusher Utilization Proxy
| Policy | Crusher1 share | Crusher1 util | Crusher2 share | Crusher2 util |
|---|---|---|---|---|
| H0 | 55.5% | 122.7% | 44.5% | 66.8% |
| H_TIME | 55.6% | 122.9% | 44.4% | 66.6% |
| H1_original | 50.3% | 111.2% | 49.7% | 74.5% |
| H1_value_guard | 61.1% | 135.1% | 38.9% | 58.3% |
| H2_original | 61.2% | 135.2% | 38.8% | 58.2% |
| H2_value_guard | 61.3% | 135.5% | 38.7% | 58.1% |
| H3 | 88.6% | 195.8% | 11.4% | 17.1% |
| H4 | 40.0% | 88.4% | 60.0% | 90.0% |

### 4. Route Utilization
| Policy | R_A1 util | R_A2 util | R_B1 util | R_B2 util | R_C1 util | R_C2 util |
|---|---|---|---|---|---|---|
| H0 | 79.5% | 67.7% | 74.1% | 33.1% | 37.0% | 27.5% |
| H_TIME | 79.4% | 67.8% | 74.5% | 32.7% | 37.1% | 27.6% |
| H1_original | 0.3% | 0.0% | 63.7% | 29.8% | 100.0% | 100.0% |
| H1_value_guard | 0.7% | 0.0% | 100.0% | 0.0% | 100.0% | 99.5% |
| H2_original | 0.8% | 0.0% | 100.0% | 0.0% | 100.0% | 99.4% |
| H2_value_guard | 1.2% | 0.0% | 100.0% | 0.0% | 100.0% | 99.2% |
| H3 | 100.0% | 0.0% | 100.0% | 0.0% | 100.0% | 29.3% |
| H4 | 46.6% | 52.9% | 43.5% | 60.0% | 45.5% | 54.9% |

### 5-8. Queue/Cycle/Throughput/Concentration Proxies
| Policy | Queue hours | Avg selected queue penalty | Weighted cycle factor | Completed loads/hour | Route HHI | Max route share |
|---|---|---|---|---|---|---|
| H0 | not logged | 0.319 | 1.271 | 8.75 | 0.183 | 22.0% |
| H_TIME | not logged | 0.319 | 1.270 | 8.75 | 0.184 | 22.0% |
| H1_original | not logged | 0.420 | 1.084 | 8.75 | 0.298 | 39.0% |
| H1_value_guard | not logged | 0.506 | 1.068 | 8.75 | 0.337 | 38.9% |
| H2_original | not logged | 0.506 | 1.068 | 8.75 | 0.337 | 38.8% |
| H2_value_guard | not logged | 0.507 | 1.068 | 8.75 | 0.336 | 38.7% |
| H3 | not logged | 0.535 | 1.137 | 8.75 | 0.275 | 31.4% |
| H4 | not logged | 0.244 | 1.237 | 8.75 | 0.175 | 21.4% |

### 9. C Route 집중과 Effective Output 관계
| Policy | R_C1+R_C2 share | Avg grade/load | Effective output | Effective fulfillment | TCO v2 base |
|---|---|---|---|---|---|
| H0 | 22.4% | 0.822 | 5,433,967.0 | 1.027 | 9,769.8 |
| H_TIME | 22.5% | 0.821 | 5,433,662.5 | 1.027 | 9,262.9 |
| H1_original | 70.5% | 0.730 | 4,826,381.0 | 0.912 | 7,412.7 |
| H1_value_guard | 70.3% | 0.730 | 4,828,208.0 | 0.912 | 7,393.8 |
| H2_original | 70.3% | 0.730 | 4,828,775.0 | 0.912 | 7,380.8 |
| H2_value_guard | 70.2% | 0.730 | 4,830,091.0 | 0.913 | 7,368.3 |
| H3 | 42.9% | 0.785 | 5,191,200.0 | 0.981 | 6,053.9 |
| H4 | 35.7% | 0.794 | 5,254,200.0 | 0.993 | 5,774.8 |

## Regime: `high_stress`

### 1. Policy x Regime Route Share
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

### 2. Shovel Utilization Proxy
| Policy | A share | A util | B share | B util | C share | C util |
|---|---|---|---|---|---|---|
| H0 | 43.8% | 127.8% | 33.8% | 94.5% | 22.4% | 56.0% |
| H_TIME | 43.8% | 127.8% | 33.7% | 94.4% | 22.5% | 56.2% |
| H1_original | 0.1% | 0.2% | 29.4% | 82.4% | 70.5% | 176.2% |
| H1_value_guard | 0.1% | 0.3% | 29.5% | 82.7% | 70.4% | 176.0% |
| H2_original | 0.1% | 0.3% | 29.5% | 82.7% | 70.4% | 175.9% |
| H2_value_guard | 0.3% | 0.8% | 29.5% | 82.7% | 70.2% | 175.5% |
| H3 | 27.6% | 80.6% | 29.5% | 82.7% | 42.9% | 107.1% |
| H4 | 30.0% | 87.5% | 34.3% | 96.0% | 35.7% | 89.3% |

### 3. Crusher Utilization Proxy
| Policy | Crusher1 share | Crusher1 util | Crusher2 share | Crusher2 util |
|---|---|---|---|---|
| H0 | 55.5% | 122.7% | 44.5% | 66.8% |
| H_TIME | 55.6% | 122.8% | 44.4% | 66.6% |
| H1_original | 50.1% | 110.8% | 49.9% | 74.8% |
| H1_value_guard | 61.0% | 134.9% | 39.0% | 58.4% |
| H2_original | 61.1% | 135.0% | 38.9% | 58.4% |
| H2_value_guard | 61.2% | 135.3% | 38.8% | 58.2% |
| H3 | 88.6% | 195.8% | 11.4% | 17.1% |
| H4 | 40.0% | 88.4% | 60.0% | 90.0% |

### 4. Route Utilization
| Policy | R_A1 util | R_A2 util | R_B1 util | R_B2 util | R_C1 util | R_C2 util |
|---|---|---|---|---|---|---|
| H0 | 79.4% | 67.6% | 74.2% | 33.2% | 37.0% | 27.6% |
| H_TIME | 79.3% | 67.7% | 74.4% | 32.8% | 37.2% | 27.6% |
| H1_original | 0.3% | 0.0% | 63.0% | 30.3% | 100.0% | 100.0% |
| H1_value_guard | 0.3% | 0.0% | 100.0% | 0.0% | 100.0% | 99.8% |
| H2_original | 0.4% | 0.0% | 100.0% | 0.0% | 100.0% | 99.7% |
| H2_value_guard | 0.9% | 0.0% | 100.0% | 0.0% | 100.0% | 99.3% |
| H3 | 100.0% | 0.0% | 100.0% | 0.0% | 100.0% | 29.3% |
| H4 | 46.5% | 52.9% | 43.5% | 60.0% | 45.5% | 54.9% |

### 5-8. Queue/Cycle/Throughput/Concentration Proxies
| Policy | Queue hours | Avg selected queue penalty | Weighted cycle factor | Completed loads/hour | Route HHI | Max route share |
|---|---|---|---|---|---|---|
| H0 | not logged | 0.319 | 1.271 | 8.75 | 0.183 | 21.9% |
| H_TIME | not logged | 0.319 | 1.270 | 8.75 | 0.183 | 22.0% |
| H1_original | not logged | 0.419 | 1.084 | 8.75 | 0.298 | 39.0% |
| H1_value_guard | not logged | 0.506 | 1.068 | 8.75 | 0.338 | 39.0% |
| H2_original | not logged | 0.506 | 1.068 | 8.75 | 0.337 | 38.9% |
| H2_value_guard | not logged | 0.506 | 1.068 | 8.75 | 0.336 | 38.8% |
| H3 | not logged | 0.535 | 1.137 | 8.75 | 0.275 | 31.4% |
| H4 | not logged | 0.244 | 1.237 | 8.75 | 0.175 | 21.4% |

### 9. C Route 집중과 Effective Output 관계
| Policy | R_C1+R_C2 share | Avg grade/load | Effective output | Effective fulfillment | TCO v2 base |
|---|---|---|---|---|---|
| H0 | 22.4% | 0.821 | 5,433,218.0 | 1.027 | 11,011.1 |
| H_TIME | 22.5% | 0.821 | 5,433,001.0 | 1.027 | 10,582.9 |
| H1_original | 70.5% | 0.730 | 4,826,314.5 | 0.912 | 9,441.8 |
| H1_value_guard | 70.4% | 0.730 | 4,827,060.0 | 0.912 | 9,452.9 |
| H2_original | 70.4% | 0.730 | 4,827,382.0 | 0.912 | 9,419.3 |
| H2_value_guard | 70.2% | 0.730 | 4,829,251.0 | 0.913 | 9,411.8 |
| H3 | 42.9% | 0.785 | 5,191,200.0 | 0.981 | 8,187.5 |
| H4 | 35.7% | 0.794 | 5,254,182.5 | 0.993 | 7,964.2 |

## Regime: `high_demand_high_stress`

### 1. Policy x Regime Route Share
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

### 2. Shovel Utilization Proxy
| Policy | A share | A util | B share | B util | C share | C util |
|---|---|---|---|---|---|---|
| H0 | 36.7% | 122.7% | 35.9% | 115.2% | 27.5% | 78.8% |
| H_TIME | 36.7% | 122.7% | 35.8% | 115.1% | 27.5% | 79.0% |
| H1_original | 0.1% | 0.2% | 38.5% | 123.8% | 61.4% | 176.2% |
| H1_value_guard | 0.1% | 0.4% | 38.5% | 123.6% | 61.4% | 176.2% |
| H2_original | 0.1% | 0.5% | 38.4% | 123.5% | 61.4% | 176.2% |
| H2_value_guard | 0.3% | 1.0% | 38.4% | 123.3% | 61.3% | 176.0% |
| H3 | 24.1% | 80.6% | 25.7% | 82.7% | 50.2% | 144.0% |
| H4 | 31.6% | 105.6% | 31.9% | 102.6% | 36.5% | 104.8% |

### 3. Crusher Utilization Proxy
| Policy | Crusher1 share | Crusher1 util | Crusher2 share | Crusher2 util |
|---|---|---|---|---|
| H0 | 54.5% | 138.2% | 45.5% | 78.4% |
| H_TIME | 54.5% | 138.3% | 45.5% | 78.3% |
| H1_original | 50.0% | 126.7% | 50.0% | 86.2% |
| H1_value_guard | 53.2% | 135.1% | 46.8% | 80.5% |
| H2_original | 53.3% | 135.1% | 46.7% | 80.5% |
| H2_value_guard | 53.4% | 135.5% | 46.6% | 80.2% |
| H3 | 77.2% | 195.8% | 22.8% | 39.3% |
| H4 | 41.1% | 104.2% | 58.9% | 101.4% |

### 4. Route Utilization
| Policy | R_A1 util | R_A2 util | R_B1 util | R_B2 util | R_C1 util | R_C2 util |
|---|---|---|---|---|---|---|
| H0 | 77.9% | 63.4% | 69.6% | 57.7% | 65.1% | 28.4% |
| H_TIME | 77.9% | 63.5% | 69.7% | 57.5% | 65.2% | 28.5% |
| H1_original | 0.2% | 0.0% | 87.5% | 51.5% | 100.0% | 100.0% |
| H1_value_guard | 0.6% | 0.0% | 100.0% | 40.9% | 100.0% | 100.0% |
| H2_original | 0.6% | 0.0% | 100.0% | 40.9% | 100.0% | 100.0% |
| H2_value_guard | 1.2% | 0.0% | 100.0% | 40.7% | 100.0% | 99.8% |
| H3 | 100.0% | 0.0% | 100.0% | 0.0% | 100.0% | 67.1% |
| H4 | 56.8% | 63.4% | 53.2% | 58.6% | 50.1% | 67.0% |

### 5-8. Queue/Cycle/Throughput/Concentration Proxies
| Policy | Queue hours | Avg selected queue penalty | Weighted cycle factor | Completed loads/hour | Route HHI | Max route share |
|---|---|---|---|---|---|---|
| H0 | not logged | 0.331 | 1.246 | 10.04 | 0.173 | 18.8% |
| H_TIME | not logged | 0.331 | 1.245 | 10.04 | 0.173 | 18.7% |
| H1_original | not logged | 0.444 | 1.102 | 10.04 | 0.267 | 34.0% |
| H1_value_guard | not logged | 0.463 | 1.098 | 10.04 | 0.273 | 34.0% |
| H2_original | not logged | 0.463 | 1.098 | 10.04 | 0.273 | 34.0% |
| H2_value_guard | not logged | 0.464 | 1.098 | 10.04 | 0.272 | 33.9% |
| H3 | not logged | 0.515 | 1.132 | 10.04 | 0.251 | 27.4% |
| H4 | not logged | 0.282 | 1.237 | 10.04 | 0.173 | 22.8% |

### 9. C Route 집중과 Effective Output 관계
| Policy | R_C1+R_C2 share | Avg grade/load | Effective output | Effective fulfillment | TCO v2 base |
|---|---|---|---|---|---|
| H0 | 27.5% | 0.809 | 6,142,843.0 | 1.011 | 11,851.0 |
| H_TIME | 27.5% | 0.809 | 6,142,479.0 | 1.011 | 11,499.2 |
| H1_original | 61.4% | 0.739 | 5,607,395.5 | 0.923 | 10,621.3 |
| H1_value_guard | 61.4% | 0.739 | 5,608,008.0 | 0.923 | 10,598.2 |
| H2_original | 61.4% | 0.739 | 5,608,085.0 | 0.923 | 10,590.2 |
| H2_value_guard | 61.3% | 0.739 | 5,609,807.0 | 0.924 | 10,587.2 |
| H3 | 50.2% | 0.774 | 5,874,750.0 | 0.967 | 9,678.5 |
| H4 | 36.5% | 0.795 | 6,035,568.0 | 0.994 | 9,065.5 |

## H1/H2 C Route Concentration Bottleneck Check

| Regime | Policy | C route share | R_C1 util | R_C2 util | Shovel C util proxy | HHI | Max route share | Queue penalty proxy | Cycle proxy | Eff fulfill |
|---|---|---|---|---|---|---|---|---|---|---|
| heterogeneous_condition | H1_original | 70.5% | 100.0% | 100.0% | 176.2% | 0.298 | 39.0% | 0.420 | 1.084 | 0.912 |
| heterogeneous_condition | H1_value_guard | 70.3% | 100.0% | 99.5% | 175.7% | 0.337 | 38.9% | 0.506 | 1.068 | 0.912 |
| heterogeneous_condition | H2_original | 70.3% | 100.0% | 99.4% | 175.6% | 0.337 | 38.8% | 0.506 | 1.068 | 0.912 |
| heterogeneous_condition | H2_value_guard | 70.2% | 100.0% | 99.2% | 175.4% | 0.336 | 38.7% | 0.507 | 1.068 | 0.913 |
| high_stress | H1_original | 70.5% | 100.0% | 100.0% | 176.2% | 0.298 | 39.0% | 0.419 | 1.084 | 0.912 |
| high_stress | H1_value_guard | 70.4% | 100.0% | 99.8% | 176.0% | 0.338 | 39.0% | 0.506 | 1.068 | 0.912 |
| high_stress | H2_original | 70.4% | 100.0% | 99.7% | 175.9% | 0.337 | 38.9% | 0.506 | 1.068 | 0.912 |
| high_stress | H2_value_guard | 70.2% | 100.0% | 99.3% | 175.5% | 0.336 | 38.8% | 0.506 | 1.068 | 0.913 |
| high_demand_high_stress | H1_original | 61.4% | 100.0% | 100.0% | 176.2% | 0.267 | 34.0% | 0.444 | 1.102 | 0.923 |
| high_demand_high_stress | H1_value_guard | 61.4% | 100.0% | 100.0% | 176.2% | 0.273 | 34.0% | 0.463 | 1.098 | 0.923 |
| high_demand_high_stress | H2_original | 61.4% | 100.0% | 100.0% | 176.2% | 0.273 | 34.0% | 0.463 | 1.098 | 0.923 |
| high_demand_high_stress | H2_value_guard | 61.3% | 100.0% | 99.8% | 176.0% | 0.272 | 33.9% | 0.464 | 1.098 | 0.924 |

판정: H1/H2는 route capacity 기준으로 R_C1/R_C2를 거의 포화시키는 패턴을 보인다. 그러나 이 포화가 실제 queue hours로 이어졌는지는 현재 summary/log로는 검증할 수 없다. simulator가 route capacity를 일일 cap으로 제한하고 fallback을 수행하지만, waiting queue나 cycle time delay를 상태로 누적하지 않기 때문이다.

## H4 Route Diversification Check

| Regime | H4 max share | H4 HHI | H4 cycle proxy | H4 queue proxy | H4 eff fulfill | H2_vg max share | H2_vg HHI | H2_vg cycle proxy | H2_vg queue proxy | H2_vg eff fulfill |
|---|---|---|---|---|---|---|---|---|---|---|
| heterogeneous_condition | 21.4% | 0.175 | 1.237 | 0.244 | 0.993 | 38.7% | 0.336 | 1.068 | 0.507 | 0.913 |
| high_stress | 21.4% | 0.175 | 1.237 | 0.244 | 0.993 | 38.8% | 0.336 | 1.068 | 0.506 | 0.913 |
| high_demand_high_stress | 22.8% | 0.173 | 1.237 | 0.282 | 0.994 | 33.9% | 0.272 | 1.098 | 0.464 | 0.924 |

해석: H4는 route HHI와 max route share를 낮춰 route 분산은 명확히 달성한다. 다만 weighted cycle factor는 H1/H2보다 낮지 않다. 현재 데이터만으로 H4가 실제 queue hours 또는 realized cycle time을 줄였다고 말할 수는 없다. H4의 확인 가능한 장점은 route/facility 분산과 높은 effective fulfillment다.

## 현재 로그로 부족한 필드

현재 C5.52 summary만으로 부족한 필드는 다음과 같다.

| Needed field | 이유 | 권장 grain |
|---|---|---|
| `route_queue_hours` | route capacity 포화가 실제 대기시간으로 이어졌는지 확인 | route x day 또는 route x step |
| `shovel_queue_hours` | derived shovel over-utilization이 실제 shovel 병목인지 확인 | shovel x day/step |
| `crusher_queue_hours` | Crusher 1/2 병목과 stop-go risk 검증 | crusher x day/step |
| `realized_cycle_time_hours` | route cycle factor가 실제 cycle time으로 반영되는지 확인 | completed haul event |
| `waiting_truck_count_by_facility` | queue length와 congestion severity 측정 | facility x step |
| `capacity_blocked_dispatch_count` | capacity 때문에 preferred route를 못 쓴 횟수 측정 | policy x route x day |
| `fallback_route_selected` | route ranking 1순위가 막혀 대체 route로 간 경우 확인 | dispatch event |
| `route_service_capacity_remaining_end_of_day` | route cap 소진/잔여 분포 확인 | route x day |

## C5.53 설계 제안: Congestion-Aware Logging

C5.53을 구현한다면 simulator objective를 바로 바꾸기보다, 먼저 congestion logging을 추가하는 것이 좋다. 추천 설계는 다음과 같다.

1. Dispatch event log에 `preferred_route`, `assigned_route`, `fallback_reason`, `route_capacity_remaining_before`, `route_capacity_remaining_after`를 기록한다.
2. Route/facility daily summary에 route/shovel/crusher별 demand, assigned loads, rejected/fallback loads, capacity utilization, estimated queue hours를 기록한다.
3. `realized_cycle_time_hours = base_cycle_hours * route.cycle_time_factor + queue_delay_hours` 형태의 명시적 proxy를 도입하되, 기존 C5.52와 별도 모듈로 둔다.
4. Queue delay는 먼저 deterministic proxy로 시작한다: utilization이 1.0을 넘는 facility/route에 대해 excess load를 capacity로 나눈 시간을 누적한다.
5. C5.53 DOE에서는 value-risk weight sweep과 congestion metrics를 함께 보고, H4의 분산이 실제 queue/cycle 이득으로 이어지는지 검증한다.

## 최종 결론

C5.52 summary 기준으로 H1/H2의 C route 집중은 route-level capacity bottleneck 패턴을 만든다. 특히 R_C1/R_C2는 거의 포화되고, derived Shovel C utilization은 100%를 넘는다. 하지만 현재 simulator는 shovel/crusher queue와 realized cycle time을 직접 모델링/로그하지 않으므로, 실제 queue hours나 cycle time 병목을 확정할 수 없다.

H4는 route 분산을 명확히 달성하며 effective fulfillment도 높다. 그러나 현재 로그만으로는 H4가 queue/cycle time 이득을 얻었다고 단정할 수 없고, 그 이득을 검증하려면 C5.53에서 congestion-aware logging이 필요하다.
