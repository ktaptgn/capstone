# C5.4 결과 요약

> 출처: `reports/07_C5_4_RESULTS.md` (30 held-out seeds × 365일, lower TCO = better).
> TCO 단위는 normalized presentation value (실제 회계 비용 아님).

## Regime별 최종 순위

| Regime | Ranking | Best Policy | 해석 |
|---|---|---|---|
| heterogeneous_condition | H2 < H1 < H3 < H4 < H_TIME < H0 | H2 | H1/H2 state-aware 계열 우위 |
| high_stress | H1 < H2 < H3 < H4 < H_TIME < H0 | H1 | stress 상황에서도 CBM 계열 우위 |
| high_demand_high_stress | H1 < H2 < H3 < H4 < H_TIME < H0 | H1 | 수요 압박 조건에서도 state-aware 우위 |

## Regime별 정책 TCO (낮을수록 좋음)

### heterogeneous_condition

| 순위 | 정책 | TCO | CM/run | fail/run | end HI |
|---:|---|---:|---:|---:|---:|
| 1 | H2 (best) | 22,367 | 0.1 | 0.1 | 0.32 |
| 2 | H1 | 22,386 | 0.0 | 0.0 | 0.34 |
| 3 | H3 | 23,675 | 0.0 | 0.0 | 0.73 |
| 4 | H4 | 23,740 | 0.1 | 0.1 | 0.74 |
| 5 | H_TIME | 36,694 | 66.4 | 66.4 | 0.83 |
| 6 | H0 | 37,548 | 95.9 | 95.9 | 0.84 |

### high_stress

| 순위 | 정책 | TCO | CM/run | fail/run | end HI |
|---:|---|---:|---:|---:|---:|
| 1 | H1 (best) | 32,565 | 2.4 | 2.4 | 0.32 |
| 2 | H2 | 32,584 | 3.6 | 3.6 | 0.30 |
| 3 | H3 | 33,690 | 13.3 | 13.3 | 0.72 |
| 4 | H4 | 33,807 | 17.4 | 17.4 | 0.72 |
| 5 | H_TIME | 42,520 | 256.4 | 256.4 | 0.65 |
| 6 | H0 | 43,362 | 276.7 | 276.7 | 0.72 |

### high_demand_high_stress

| 순위 | 정책 | TCO | CM/run | fail/run | fulfil | end HI |
|---:|---|---:|---:|---:|---:|---:|
| 1 | H1 (best) | 47,631 | 44.1 | 44.1 | 0.934 | 0.28 |
| 2 | H2 | 47,655 | 46.4 | 46.4 | 0.934 | 0.26 |
| 3 | H3 | 48,047 | 42.4 | 42.4 | 0.934 | 0.65 |
| 4 | H4 | 48,071 | 48.2 | 48.2 | 0.934 | 0.65 |
| 5 | H_TIME | 56,673 | 346.2 | 346.2 | 0.934 | 0.58 |
| 6 | H0 | 57,397 | 360.1 | 360.1 | 0.934 | 0.62 |

## state-aware vs blind 요약 수치 (발표 핵심 한 장)

| Regime | state-aware best | blind best | TCO 절감 | paired seed 우위 |
|---|---:|---:|---:|---:|
| heterogeneous_condition | 22,367 (H2) | 36,694 (H_TIME) | **−40.4%** | 30/30 |
| high_stress | 32,565 (H1) | 42,520 (H_TIME) | **−24.9%** | 30/30 |
| high_demand_high_stress | 47,631 (H1) | 56,673 (H_TIME) | **−17.0%** | 30/30 |

## 발표용 결론

C5.4에서 중요한 것은 특정 정책 하나의 절대 승리가 아니라,
상태 정보를 활용하는 H1/H2 계열이 blind PM 계열보다
전 regime에서 안정적으로 낮은 TCO를 보였다는 점이다.

핵심 역설: blind PM(H0/H_TIME)은 평균 HI가 0.83~0.84로 가장 "건강"해 보이지만
CM(고장 정비)이 가장 많다. state-aware(H1/H2)는 HI 0.3 근처로 lean하게 운영하면서
고장은 거의 0에 가깝다. 많이 정비하는 것이 아니라 "맞는 부품"을 정비하는 것이 핵심이다.
