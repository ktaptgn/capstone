# Slide Outline

## Slide 1. Title
Title: 가상 광산 시뮬레이션을 통한 마일리지 적용 설비 PM 분석 및 최소 비용 지출 정책 도출

Subtitle: 등가 마일리지·Health Index·PM timing을 고려한 가상광산 DES 기반 정책 비교

## Slide 2. 프로젝트 개요
- 문제 배경: 열화가 누적되는 haul truck과 tire를 계속 운행할지 PM으로 뺄지 결정해야 한다.
- 핵심 질문: 같은 환경에서 어떤 정책이 CU 기반 비용과 생산 KPI를 더 잘 균형화하는가.
- 산업공학적 의사결정 구조: resource allocation, queue, PM timing, cost trade-off.
- 왜 광산 트럭인가: 설비 열화, 대기, 생산 목표, 정비 capacity가 동시에 충돌한다.
- 표현: Escondida/Atacama 특성을 참조한 proxy DES 가상광산이다.

## Slide 3. 프로젝트 요소 설명
Truck, Tire HI, Truck HI, Shovel, Crusher 1 / Crusher 2, PM Bay, Plant Feed Manager, Time-risk / seasonal risk, Cost Unit을 한 장에 정리한다.

## Slide 4. 시뮬레이션 환경 구조
DES engine, dispatch-PM decision, queue, loading / hauling / dumping / PM / cooldown / standby, event scheduler 흐름을 설명한다.

## Slide 5. 시뮬레이션 세부 스펙
`tables/03_simulation_spec.md`의 Category / Value / Type / Defense 구조를 사용한다.

## Slide 6. 마일리지 / HI / PM 판단 구조
운행 누적 → EOH / TKPH / severity 증가 → Tire HI, Truck HI 감소 → RUL proxy, PM due score 증가 → PM / 계속 운행 / cooldown / standby 판단.

마일리지 용어 매핑:

| 발표 용어 | 구현상 의미 |
| --- | --- |
| 마일리지 | EOH, TKPH, route severity 기반 누적 사용량 proxy |
| 설비 상태 | Truck HI + Tire HI |
| PM 필요도 | RUL proxy, PM due score, HI threshold |
| 최소 비용 정책 | CU 기반 총비용, downtime, queue, failure, PM cost 최소화 정책 |

## Slide 7. 휴리스틱 비교 구조
구현 이름을 사용한다: H0 Baseline, H1 Bottleneck Dispatch, H2 PM Risk Priority, H3 Cost Unit Value, H4 Flow / Backpressure.

## Slide 8. 각 휴리스틱 설명
`tables/04_heuristic_definitions.md`의 policy decision table을 사용한다.

## Slide 9. 결과 비교 — KPI
Official source: `outputs/c5_1/summary/policy_comparison.csv`.
현재 365-day sweep 기준 lowest total cost는 H3 (1724.749 CU), highest fulfillment도 H3 (0.971)이다.

## Slide 10. 결과 비교 — 비용 분해
`tables/06_cost_breakdown.md`와 `figures/cost_breakdown.png`를 사용한다. CU cost가 정책 비교 기준이다.

## Slide 11. 정책 해석
- 가장 낮은 비용: H3
- 생산량 유지: H3
- PM을 많이 쓰는 정책은 cost와 downtime을 같이 봐야 한다.
- failure field는 현재 official output에 별도 존재하지 않는다.
- PM bay / queue / time-risk는 ranking을 해석하는 proxy factor이며 통계적 유의성으로 과장하지 않는다.

## Slide 12. 프로젝트 한계점
`tables/07_limitations_and_improvements.md`의 limitations table을 사용한다.

## Slide 13. 개선점
telemetry calibration, multi-seed robustness, PM bay sensitivity, cost sensitivity, route roughness/demand shock, RUL proxy refinement를 제안한다.

## Slide 14. 타 분야 응용
스마트팩토리 AGV, 반도체 후공정 설비, 저항점용접 RSW electrode tip, 데이터센터 냉각/서버 설비, 발전소/풍력 설비, 군용 차량/항공 정비로 전이 가능성을 설명한다. 이미 검증한 실험으로 말하지 않는다.

## Slide 15. Final Message
본 프로젝트의 핵심은 광산 자체를 정밀 복제하는 것이 아니라,
열화가 누적되는 설비를 언제 계속 운행하고 언제 PM으로 빼야 하는지
정량 KPI와 비용 proxy로 비교하는 의사결정 프레임워크를 만든 것이다.
