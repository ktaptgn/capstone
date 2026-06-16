# C5.55 Personal Presentation Summary

## Executive Summary

C5.55 is a personal follow-up benchmark that freezes H5 as the guarded H4 route-allocation improvement from C5.54. In the 90-day benchmark, H5 beats both H4 and the audit-only `BALANCED_RR_H4_PM` comparator in all three regimes under soft TCO v4, with minimum effective fulfillment 0.990. `H5_AGGRESSIVE` is better only under high-demand/high-stress, but its higher fallback dependence makes it an alternative rather than the default.

## C5.4 vs C5.55 Difference

C5.4에서는 reliability-cost 중심 목적함수에서 H1/H2가 우수했습니다. 반면 C5.55는 개인 후속 실험으로 grade-adjusted output과 route/facility congestion을 포함했기 때문에, 생산가치와 병목까지 균형화하는 H5가 우수하게 나타났습니다. 두 결과는 모순이 아니라 objective definition이 달라졌을 때 최적 정책이 달라진다는 후속 검증입니다.

## H5 Policy Definition

H5는 H4의 PM/flow logic을 기반으로 balanced route rotation, shovel/crusher/risk guard, fallback-to-H4 logic을 결합한 guarded route-allocation policy입니다.

## Why H5 Was Selected as Default

- H5 beats H4 in all regimes under soft TCO v4.
- H5 beats the audit-only `BALANCED_RR_H4_PM` comparator in all regimes.
- H5 keeps fallback/load lower than `H5_AGGRESSIVE` while retaining strong TCO performance.
- H5 is easier to explain as a guarded official policy because it uses the C5.54 freeze setting `0.90/base`.

## Why H5_AGGRESSIVE Was Not Selected as Default

`H5_AGGRESSIVE` wins only in `high_demand_high_stress`; in lower-stress regimes it is slightly worse than H5 and roughly doubles fallback/load. It remains useful as a stress-sensitive alternative, but not as the presentation default.

## H4 vs H5 vs H5_AGGRESSIVE Comparison

| regime | policy | soft_tco_v4 | rank | effective_fulfillment_rate | failure_count | cm_count | downtime_hours | hard_congestion_hours | soft_congestion_hours | fallback_per_completed_load | dominant_guard | interpretation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| heterogeneous_condition | H5 | 5454.5 | 1 | 0.990 | 0.000 | 0.000 | 2455.5 | 0.000 | 0.636 | 0.360 | risk | Default official H5; best overall unless aggressive stress setting is isolated. |
| heterogeneous_condition | H5_AGGRESSIVE | 5478.6 | 2 | 0.991 | 0.000 | 0.000 | 2477.4 | 0.000 | 0.449 | 0.730 | risk | Aggressive sensitivity comparator; useful under high-demand stress but higher fallback dependence. |
| heterogeneous_condition | BALANCED_RR_H4_PM | 5570.9 | 3 | 1.000 | 0.000 | 0.000 | 2691.7 | 0.100 | 5.035 | 0.000 | none | Audit-only comparator; not an official policy. |
| heterogeneous_condition | H4 | 5775.0 | 4 | 0.993 | 0.000 | 0.000 | 2659.5 | 0.000 | 0.351 | 0.000 | none | Official H4 baseline; improved by H5 in C5.55. |
| high_stress | H5 | 7616.7 | 1 | 0.991 | 0.000 | 0.000 | 3501.8 | 0.000 | 0.622 | 0.353 | risk | Default official H5; best overall unless aggressive stress setting is isolated. |
| high_stress | H5_AGGRESSIVE | 7623.9 | 2 | 0.991 | 0.000 | 0.000 | 3511.9 | 0.000 | 0.445 | 0.714 | risk | Aggressive sensitivity comparator; useful under high-demand stress but higher fallback dependence. |
| high_stress | BALANCED_RR_H4_PM | 7767.4 | 3 | 1.000 | 0.400 | 0.400 | 3736.7 | 0.106 | 5.085 | 0.000 | none | Audit-only comparator; not an official policy. |
| high_stress | H4 | 7964.3 | 4 | 0.993 | 0.400 | 0.400 | 3709.3 | 0.000 | 0.351 | 0.000 | none | Official H4 baseline; improved by H5 in C5.55. |
| high_demand_high_stress | H5_AGGRESSIVE | 8817.6 | 1 | 0.993 | 14.1 | 14.1 | 4069.3 | 0.069 | 8.327 | 0.843 | shovel | Aggressive sensitivity comparator; useful under high-demand stress but higher fallback dependence. |
| high_demand_high_stress | H5 | 8883.4 | 2 | 0.992 | 15.3 | 15.3 | 4075.3 | 0.122 | 9.171 | 0.566 | shovel | Default official H5; best overall unless aggressive stress setting is isolated. |
| high_demand_high_stress | BALANCED_RR_H4_PM | 8905.0 | 3 | 1.000 | 20.4 | 20.4 | 4242.3 | 1.219 | 24.3 | 0.000 | none | Audit-only comparator; not an official policy. |
| high_demand_high_stress | H4 | 9069.2 | 4 | 0.994 | 17.6 | 17.6 | 4201.7 | 0.023 | 7.346 | 0.000 | none | Official H4 baseline; improved by H5 in C5.55. |

## H5 Pairwise Improvement

| regime | comparison | tco_margin | effective_fulfillment_diff | failure_diff | cm_diff | downtime_diff | soft_congestion_diff | fallback_diff | interpretation |
|---|---|---|---|---|---|---|---|---|---|
| heterogeneous_condition | H5 vs H4 | 320.5 | -0.003 | 0.000 | 0.000 | -204.0 | 0.286 | 0.360 | H5 is lower TCO than H4; fallback behavior should still be disclosed. |
| heterogeneous_condition | H5 vs BALANCED_RR_H4_PM | 116.4 | -0.010 | 0.000 | 0.000 | -236.2 | -4.399 | 0.360 | H5 converts the audit comparator signal into an official guarded policy. |
| heterogeneous_condition | H5 vs H5_AGGRESSIVE | 24.1 | -0.001 | 0.000 | 0.000 | -21.9 | 0.188 | -0.369 | H5 is lower TCO than the aggressive variant in this regime. |
| high_stress | H5 vs H4 | 347.6 | -0.002 | -0.400 | -0.400 | -207.5 | 0.271 | 0.353 | H5 is lower TCO than H4; fallback behavior should still be disclosed. |
| high_stress | H5 vs BALANCED_RR_H4_PM | 150.6 | -0.009 | -0.400 | -0.400 | -234.9 | -4.463 | 0.353 | H5 converts the audit comparator signal into an official guarded policy. |
| high_stress | H5 vs H5_AGGRESSIVE | 7.150 | -0.000 | 0.000 | 0.000 | -10.1 | 0.177 | -0.361 | H5 is lower TCO than the aggressive variant in this regime. |
| high_demand_high_stress | H5 vs H4 | 185.7 | -0.002 | -2.300 | -2.300 | -126.4 | 1.825 | 0.566 | H5 is lower TCO than H4; fallback behavior should still be disclosed. |
| high_demand_high_stress | H5 vs BALANCED_RR_H4_PM | 21.6 | -0.008 | -5.100 | -5.100 | -167.0 | -15.1 | 0.566 | H5 converts the audit comparator signal into an official guarded policy. |
| high_demand_high_stress | H5 vs H5_AGGRESSIVE | -65.8 | -0.001 | 1.200 | 1.200 | 6.000 | 0.844 | -0.277 | H5_AGGRESSIVE is lower TCO here, but it is not default because fallback dependence is higher. |

## H5 vs BALANCED_RR_H4_PM Comparison

H5 beats the audit-only comparator in all regimes: yes. The key interpretation is that C5.55 converts the synthetic balanced-route signal into an official guarded policy with explicit utilization/risk guards and fallback behavior.

## H5 vs H1/H2 Reliability Caveat

H1/H2 should not be dismissed as failed policies. They can still represent a reliability-focused frontier under a narrower reliability-cost objective. C5.55 changes the objective surface by adding grade-adjusted output and congestion, so the preferred policy changes.

## Guard/Fallback Caveat

H5는 C5.55의 proxy objective에서는 가장 균형적인 정책이지만, 실제 광산 실측 최적 정책을 의미하지는 않습니다. 또한 C5.55는 팀 발표 C5.4를 대체하는 것이 아니라, 개인 발표에서 objective 확장과 정책 개선 과정을 보여주기 위한 follow-up benchmark입니다.

## Caveat / Defense Table

| issue | risk_if_overclaimed | safe_interpretation | presentation_sentence |
|---|---|---|---|
| C5.55 does not replace team C5.4. | Audience may think the team result changed retroactively. | C5.55 is a personal follow-up benchmark with an expanded objective. | C5.55는 C5.4를 대체하지 않고, 목적함수 확장 시 정책 순위가 어떻게 달라지는지 보여주는 후속 실험입니다. |
| C5.55 uses proxy cycle-time and soft congestion model. | Could be mistaken for site-calibrated mine optimization. | The model is useful for structured comparison, not real dispatch calibration. | cycle time과 congestion은 proxy model이므로 실제 광산 실측 최적 정책이라고 주장하지 않습니다. |
| H5_AGGRESSIVE wins in high_demand_high_stress. | Could make the default H5 selection look inconsistent. | It is a stress-sensitive alternative with higher fallback dependence. | 고수요 고스트레스에서는 aggressive variant가 더 낮은 TCO를 보였지만 fallback 의존도가 높아 default로 두지 않았습니다. |
| H1/H2 can still be reliability-focused frontier. | Could imply H1/H2 are simply bad policies. | They remain reliability-oriented policies under a narrower objective. | H1/H2는 reliability-cost 관점에서는 여전히 의미 있는 frontier이며, C5.55는 production-congestion objective를 추가한 비교입니다. |
| H5 includes fallback-to-H4 behavior and guard logic. | Could hide that H5 partly depends on H4 fallback. | Fallback is an explicit safety mechanism and must be disclosed. | H5는 balanced rotation만 쓰는 정책이 아니라 guard 위반 시 H4 score로 fallback하는 guarded policy입니다. |
| Route guard is currently non-binding. | Could overstate the role of route-capacity guard. | Most decisions are driven by shovel, crusher, risk guards and fallback. | 현재 regime에서는 route guard violation이 0이라, 실제로는 shovel/risk/crusher guard가 의사결정을 주도했습니다. |

## Recommended Slide Structure

1. Slide A — Why C5.4 and C5.55 differ
2. Slide B — From H4 to H5: route allocation improvement
3. Slide C — H5 benchmark result table
4. Slide D — Guard/fallback caveat and limitations
5. Slide E — Portfolio meaning: objective-sensitive operations optimization

## Presentation-Ready Korean Explanation Paragraphs

첫째, C5.4와 C5.55의 결과 차이는 정책 성능이 갑자기 뒤집힌 것이 아니라 목적함수 정의가 달라졌기 때문에 발생한 결과입니다. C5.4는 reliability-cost 관점에서 H1/H2의 장점을 보여주었고, C5.55는 grade-adjusted output과 congestion까지 포함했을 때 H5가 더 균형적인 선택이 될 수 있음을 보여줍니다.

둘째, H5는 H4를 버린 새로운 정책이 아니라 H4의 flow/backpressure PM logic 위에 route allocation guard를 얹은 정책입니다. balanced route rotation으로 route 집중을 낮추고, shovel/crusher/risk guard로 병목과 위험을 제어하며, 모든 guard가 막힐 때는 H4 scoring으로 fallback합니다.

셋째, H5_AGGRESSIVE는 high-demand/high-stress 조건에서 가장 낮은 TCO를 보였지만 fallback 의존도가 높기 때문에 default로 선택하지 않았습니다. 발표에서는 H5를 기본 정책으로, H5_AGGRESSIVE를 stress-sensitive alternative로 설명하는 것이 가장 방어 가능한 해석입니다.

## Q&A Defense Bullets

- H5 beats H4 across all regimes: yes.
- H5 beats the audit comparator across all regimes: yes.
- H5_AGGRESSIVE beats H5 only in: high_demand_high_stress.
- C5.55 does not replace C5.4; it demonstrates objective-sensitive optimization.
- The model is proxy-based and should not be presented as site-calibrated dispatch optimization.
- Fallback-to-H4 is a designed safety mechanism and should be disclosed.
- Route guard is non-binding in current regimes; shovel/risk/crusher guards explain most guard behavior.
