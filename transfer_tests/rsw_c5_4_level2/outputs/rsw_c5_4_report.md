# RSW C5.4 Level 2 Mini Transfer Simulation Report

This RSW simulation is a synthetic Level 2 transfer mini-test. It is not a real factory validation. Its purpose is to reconstruct the C5.4 joint PM scheduling + dispatch structure in a manufacturing RSW setting.

RSW 미니 시뮬레이션은 본 프로젝트의 메인 실험이 아니라 제조업 전이 가능성을 보여주는 보조 실험이다. C5.4의 truck/component/route/PM bay 구조를 RSW의 welding gun/component/job family/maintenance slot 구조로 재구성했다. 실제 현장 적용을 위해서는 용접 로그, 전극 dressing 이력, 품질 검사 데이터로 파라미터 보정이 필요하다.

## 1. Purpose

Demonstrate that the C5.4 joint PM scheduling and dispatch decision structure can be reconstructed as a reduced synthetic RSW mini-test.

## 2. Why this is a transfer mini-test, not the main project

The main project remains the mining C5.4 experiment. RSW parameters use synthetic CU and are not calibrated to a factory, vehicle program, or real maintenance standard.

## 3. C5.4-to-RSW mapping

| C5.4 mining | RSW mini transfer |
|---|---|
| Truck | Welding gun/cell |
| Tire / engine / brake HI | Tip / cooling / actuator HI |
| Route A/B/C | Job family A/B/C |
| PM bay | Maintenance/dressing slot |
| Dispatch | Production assignment |
| TCO | PM + CM + downtime + degradation + unmet + defect |

## 4. Simulation environment

- 10 guns, 2 maintenance slots, 30 days, 24 hourly steps/day, 10 seeds.
- Daily demand: 210 welds split equally across job families A/B/C.
- Regimes: heterogeneous condition, high stress, high demand + high stress.

## 5. Reliability surface

Each gun has tip, cooling, and actuator HI; gun HI is the component minimum. Gamma frailty, noisy observed HI, partial PM/CM restoration, defect events, and threshold-power failure hazard are enabled.

## 6. Joint PM scheduling + production assignment

Each policy returns PM referrals and ranked job families in one hourly decision. PM referrals are constrained by free gun-level maintenance slots.

## 7. Policy definitions: H0-H4 + H_TIME

- H0: calendar full service + blind round-robin.
- H_TIME: operating-hours full service + blind round-robin.
- H1: condition CBM + health routing.
- H2: risk-priority PM + risk-aware routing.
- H3: cost-value PM + value/risk routing.
- H4: flow-backpressure PM + capacity routing.

## 8. Regime results

Lower TCO is better. Actual results are retained even when they differ from the expected C5.4 mining ranking.

| regime | rank | policy | TCO | PM visits | CM | failure | defect | fulfillment |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| heterogeneous_condition | 1 | H3 **(best)** | 77.94 | 6.2 | 0.00 | 0.00 | 4.10 | 1.000 |
| heterogeneous_condition | 2 | H1 | 80.90 | 3.7 | 0.00 | 0.00 | 6.10 | 1.000 |
| heterogeneous_condition | 3 | H4 | 82.44 | 6.8 | 0.00 | 0.00 | 4.30 | 1.000 |
| heterogeneous_condition | 4 | H2 | 83.18 | 4.0 | 0.00 | 0.00 | 6.20 | 1.000 |
| heterogeneous_condition | 5 | H_TIME | 365.16 | 18.0 | 0.20 | 0.20 | 1.20 | 1.000 |
| heterogeneous_condition | 6 | H0 | 1914.44 | 100.0 | 0.00 | 0.00 | 0.10 | 1.000 |
| high_demand_high_stress | 1 | H4 **(best)** | 126.18 | 13.9 | 0.00 | 0.00 | 4.10 | 1.000 |
| high_demand_high_stress | 2 | H3 | 132.63 | 14.7 | 0.00 | 0.00 | 4.40 | 1.000 |
| high_demand_high_stress | 3 | H1 | 137.62 | 10.1 | 0.00 | 0.00 | 8.00 | 1.000 |
| high_demand_high_stress | 4 | H2 | 144.89 | 10.0 | 0.00 | 0.00 | 9.10 | 1.000 |
| high_demand_high_stress | 5 | H_TIME | 451.21 | 21.4 | 0.60 | 0.60 | 2.20 | 1.000 |
| high_demand_high_stress | 6 | H0 | 1920.06 | 100.0 | 0.00 | 0.00 | 0.00 | 1.000 |
| high_stress | 1 | H3 **(best)** | 112.00 | 11.6 | 0.00 | 0.00 | 4.30 | 1.000 |
| high_stress | 2 | H4 | 112.32 | 11.3 | 0.00 | 0.00 | 4.50 | 1.000 |
| high_stress | 3 | H2 | 115.73 | 7.7 | 0.00 | 0.00 | 7.30 | 1.000 |
| high_stress | 4 | H1 | 121.18 | 7.7 | 0.00 | 0.00 | 8.00 | 1.000 |
| high_stress | 5 | H_TIME | 394.93 | 17.9 | 0.40 | 0.40 | 4.10 | 1.000 |
| high_stress | 6 | H0 | 1918.53 | 100.0 | 0.00 | 0.00 | 0.10 | 1.000 |

## 9. Sensitivity results

- Frailty-CV sweep: the lowest-TCO policy changes across H1, H4, H3, and H1.
- Best state-aware H1/H2 remains roughly 77-80% cheaper than best blind H0/H_TIME.
- H1 CBM threshold perturbation changes TCO modestly, but the best scale differs by regime.
- Extra maintenance slots do not change ranking; they increase blind full-service activity.

## 10. Mechanism analysis

- H_TIME generated 12 failures; 10 occurred in the late campaign third.
- H0 performs 100 full-service visits/run and has the highest TCO despite near-zero failures.
- H1-H4 concentrate PM on the electrode tip, while blind policies split PM equally.
- Job-family completion shares are equal because demand is explicitly split A/B/C.

## 11. Key findings

- H3 is best under heterogeneous condition and high stress.
- H4 is best under high demand + high stress.
- Blind periodic PM is substantially more expensive, primarily from full-service PM and downtime.
- The mini-test does not reproduce the C5.4 mining H1/H2-best ranking; this difference is an honest result.

## 12. Limitations

- Synthetic parameters and synthetic CU; no factory calibration.
- Reduced 30-day, 10-seed horizon.
- Equal job-family demand forces equal completed route shares, limiting dispatch-mix interpretation.
- Failures are sparse, so frailty/failure correlation is undefined for most policies.
- No PPO/RL training and no operator dashboard.

## 13. Final presentation usage

Use this mini-test as supporting evidence that the joint decision architecture transfers to manufacturing. Do not present it as proof of real-factory performance.
