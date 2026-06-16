# RSW C5.4 Mini-Test Sanity Improvement Report

## 1. Purpose

These additional runs are sanity checks, not real factory validation. The original 30-day base result is preserved.

## 2. Why additional sanity runs were needed

- Demand stress was added because the original base demand had too much slack.
- The 90-day run was added because the original failure path was sparse.

## 3. Base 30-day result recap

| regime | policy | TCO mean | failure mean | fulfillment mean |
|---|---|---:|---:|---:|
| heterogeneous_condition | H3 | 77.943 | 0.000 | 1.000 |
| high_demand_high_stress | H4 | 126.178 | 0.000 | 1.000 |
| high_stress | H3 | 112.002 | 0.000 | 1.000 |

## 4. Demand pressure stress result

- H3 had the lowest stress TCO (2293.83 synthetic CU).
- Mean unmet demand appeared only for H_TIME; most policies still retained enough production slack for fulfillment = 1.000.
- H4 did not win the stress run; results are retained without post-hoc tuning.

## 5. 90-day horizon sanity result

| regime | policy | TCO mean | CM mean | failure mean |
|---|---|---:|---:|---:|
| heterogeneous_condition | H4 | 448.745 | 0.000 | 0.000 |
| high_demand_high_stress | H4 | 734.391 | 0.000 | 0.000 |
| high_stress | H3 | 611.485 | 0.000 | 0.000 |

- Failure/CM mean totals increased from 1.2 at 30 days to 2.8 at 90 days.
- Observed 90-day failure/CM events remained concentrated in H_TIME.
- Lowest-TCO policies by regime were heterogeneous_condition: H4, high_demand_high_stress: H4, high_stress: H3.
- H1-H4 retained component-targeted PM; no policy ranking was forced.

## 6. What changed from the original mini-test

- Optional higher-demand and longer-horizon execution contracts were added.
- Separate outputs expose a limited unmet-demand path and a somewhat richer failure/CM path.

## 7. What did not change

- The original 30-day base result and its output files remain unchanged.
- The common environment, policies, seeds, KPI definitions, and synthetic scope remain unchanged.
- Results are reported as-is and not tuned to reproduce the C5.4 mining ranking.

## 8. Remaining limitations

- These are synthetic transfer checks with no real factory calibration or validation.
- Stress produced mean unmet demand only for H_TIME; demand slack remained for most policies.
- Even at 90 days, failures remained sparse and concentrated in H_TIME.

## 9. Final presentation recommendation

Present the runs as supporting sanity checks for PM-production and horizon behavior, not as proof of manufacturing performance.

한국어 발표 요약: RSW mini-test의 추가 sanity run은 기존 결과를 대체하기 위한 것이 아니라, 기존 mini-test의 약점이었던 낮은 demand pressure와 짧은 horizon을 점검하기 위한 보조 검증이다. Demand stress에서는 PM과 생산 사이의 trade-off가 더 강하게 나타나는지 확인하고, 90-day run에서는 failure/CM path가 더 드러나는지 확인한다. 이 결과 역시 실제 공장 검증이 아니라 synthetic transfer test다.
