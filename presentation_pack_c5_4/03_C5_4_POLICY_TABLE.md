# C5.4 정책 설계 표

| 그룹 | 정책 | PM 판단 | Dispatch 판단 | 발표 해석 |
|---|---|---|---|---|
| Blind PM | H0 | calendar | route-blind | 고정 주기 PM 기준선 |
| Blind PM | H_TIME | operating-hours | route-blind | 사용시간 기반 blind PM |
| State-aware Tier 1 | H1 | CBM threshold | health routing | 상태 기반 최상위 정책 |
| State-aware Tier 1 | H2 | risk-priority | risk-aware routing | 위험도 기반 최상위 정책 |
| Value/Flow Tier 2 | H3 | cost-value | value routing | CM 비용을 더 늦게 반영하는 정책 |
| Value/Flow Tier 2 | H4 | flow/backpressure | capacity routing | 수요 압박과 흐름을 우선하는 정책 |

## 정책 해석

H1/H2는 상태 기반 PM의 대표 정책이다.
H0/H_TIME은 상태를 보지 않는 blind PM이다.
C5.4의 핵심 비교는 H1/H2 vs H0/H_TIME이다.

## 트리거 한 줄 정리 (config 근거: configs/c5_4.yaml)

- H0 calendar: 3일마다 full-vehicle service (fast-frailty-tail에 맞춘 가장 타이트한 주기).
- H_TIME operating-hours: 가동시간 30h마다 full-vehicle service.
- H1 condition(CBM): 관측 HI가 임계값(tire/engine 0.21, brake 0.28) 아래로 내려간 부품만 PM.
- H2 risk-priority: 부품 위험도(risk) ≥ 0.80인 부품만 PM.
- H3 cost-value: 예상 CM 비용이 PM을 정당화할 때(24-haul lookahead) PM — CBM보다 늦게.
- H4 flow/backpressure: HI<0.30 부품만, 수요 압박 시 PM을 미룸 — 가장 늦게.

핵심: blind(H0/H_TIME)는 부품을 안 보고 차량 전체를 통째로 반복 정비.
state-aware(H1/H2)는 실제 위험 부품(주로 tire)만 골라 짧게 자주 정비.
