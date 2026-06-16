# Capstone C5.4

## 가상 광산 신뢰성 시뮬레이션 기반 상태 인지형 PM·배차 정책 비교

2026-1 산업경영공학 캡스톤 디자인 프로젝트입니다.

본 저장소는 노천광산 haul truck 운영을 대상으로, 설비 상태를 고려한 예방정비(PM)와 배차(dispatch) 정책을 비교하는 C5.4 실험 환경을 포함합니다.

핵심 질문은 다음입니다.

```text
어떤 트럭을 어떤 route로 보내고,
어떤 부품을 언제 PM할 것인가?
```

C5.4는 실제 광산을 그대로 복제한 digital twin이 아닙니다. 공개자료와 실험 가정을 바탕으로 만든 **정책 비교용 proxy reliability simulation**입니다.

---

## 1. Project Summary

C5.4는 트럭 본체와 주요 부품의 열화 상태를 반영해 PM scheduling과 route dispatch를 동시에 판단하는 정책 비교 실험입니다.

비교 대상은 크게 두 계열입니다.

```text
State-aware PM/dispatch
vs
Condition-blind time-based PM/dispatch
```

정책만 바꾸고 동일한 환경, 동일한 운영조건, 동일한 seed에서 평가합니다.
평가 지표는 normalized TCO입니다. 낮을수록 좋은 정책입니다.

---

## 2. Problem Definition

시간 기준 PM은 두 가지 문제를 동시에 만듭니다.

| 문제    | 설명                                                       |
| ----- | -------------------------------------------------------- |
| 과잉 정비 | 아직 사용 가능한 부품을 조기 정비해 PM 비용과 PM bay 점유를 증가시킴              |
| 과소 정비 | 빠르게 열화되는 truck/component를 놓쳐 CM, downtime, failure를 증가시킴 |

따라서 본 프로젝트는 단순 주기 정비가 아니라 아래 정보를 함께 보는 정책을 비교합니다.

```text
Truck state
Component Health Index
Route condition
PM bay capacity
Demand pressure
Failure risk
```

---

## 3. C5.4 Environment

| 항목                      | 설정                                |
| ----------------------- | --------------------------------- |
| Simulation type         | Proxy reliability simulation      |
| Fleet                   | 25 trucks                         |
| Minimum operating fleet | 20 trucks                         |
| Buffer / standby        | 5 trucks                          |
| Campaign horizon        | 365 days                          |
| Step                    | 1 hour                            |
| PM bay                  | 2 bays                            |
| Route                   | A / B / C                         |
| Reliability state       | tire / engine / brake HI          |
| Uncertainty             | frailty, sensor noise             |
| Failure path            | Weibull-like hazard, CM, downtime |
| Objective               | normalized TCO                    |

C5.4의 핵심 구조는 다음과 같습니다.

```text
Truck Fleet
→ Dispatch Route A/B/C
→ Production Output
→ PM Bay / CM / Downtime
→ Reliability State Update
→ TCO Evaluation
```

---

## 4. Decision Structure

C5.4에서 정책은 매 시점 다음 두 결정을 수행합니다.

| Decision       | 의미                             |
| -------------- | ------------------------------ |
| PM scheduling  | 어떤 truck/component를 언제 PM할지 결정 |
| Route dispatch | 운행 가능한 truck을 어떤 route로 보낼지 결정 |

입력과 출력은 다음과 같습니다.

```text
INPUT
- Truck state
- Component HI
- Route condition
- PM bay availability
- Demand / stress regime

DECISION
- PM scheduling
- Dispatch routing

OUTPUT
- TCO
- Failure
- Downtime
- Fulfillment
```

---

## 5. Policy Families

C5.4는 H0 계열 기준선과 H1-H4 정책을 비교합니다.

| 그룹              | 정책   | PM 판단             | Dispatch 판단        | 해석                 |
| --------------- | ---- | ----------------- | ------------------ | ------------------ |
| Time-Based PM   | H0-α | calendar          | route-blind        | 고정 주기 기준선          |
| Time-Based PM   | H0-β | operating-hours   | route-blind        | 사용시간 기준선           |
| State-aware PM  | H1   | CBM threshold     | health routing     | 상태 임계값 기반 CBM      |
| State-aware PM  | H2   | risk-priority     | risk-aware routing | 위험도 우선순위 기반        |
| Value / Flow PM | H3   | cost-value        | value routing      | 비용가치 기반 trade-off  |
| Value / Flow PM | H4   | flow-backpressure | capacity routing   | 생산 흐름 우선 trade-off |

핵심 비교는 다음입니다.

```text
H1 / H2
vs
H0-α / H0-β
```

---

## 6. Experiment Design

C5.4는 세 가지 운영조건에서 정책을 평가합니다.

| Regime                  | 의미                     |
| ----------------------- | ---------------------- |
| heterogeneous_condition | 트럭별 열화 편차가 큰 조건        |
| high_stress             | 가혹한 운영 stress 조건       |
| high_demand_high_stress | 수요 압박과 stress가 함께 큰 조건 |

평가 조건은 다음과 같습니다.

```text
30 held-out seeds
3 regimes
365 days
Lower normalized TCO = better
```

정책 간 비교에서는 reliability surface, seed, 운영조건을 동일하게 유지합니다.
즉, 환경빨로 이기는 구조가 아니라 같은 조건에서 정책만 바꿔 비교합니다.

---

## 7. Main Finding

C5.4의 핵심 결과는 다음입니다.

```text
H1 ≈ H2 < H3 ≈ H4 < H0-α ≈ H0-β
```

해석은 다음과 같습니다.

| 결과        | 의미                                                    |
| --------- | ----------------------------------------------------- |
| H1/H2 최상위 | 상태 기반 PM과 위험도 기반 routing이 failure와 downtime을 안정적으로 줄임 |
| H3/H4 중간  | 비용가치 또는 생산흐름을 우선하지만 PM timing이 늦어질 수 있음               |
| H0 계열 최하위 | 평균 기준 정비로는 fast-frailty truck/component를 놓침           |

중요한 결론은 다음입니다.

```text
많이 정비하는 것보다,
위험한 부품을 제때 잡는 것이 더 중요하다.
```

---

## 8. Why State-Aware Policies Win

Time-based PM은 평균적인 일정이나 사용시간을 기준으로 움직입니다.
이 방식은 fleet 내부의 열화 편차를 제대로 반영하지 못합니다.

특히 fast-frailty truck은 평균 truck보다 빠르게 열화됩니다.
고정 주기 PM은 이런 truck을 놓칠 수 있습니다.

반대로 H1/H2는 다음 정보를 사용합니다.

```text
- Component HI
- Failure risk
- PM bay availability
- Route stress
- Truck-level frailty
```

이 때문에 H1/H2는 평균 HI가 아니라 실제 위험도를 기준으로 PM 대상을 선택합니다.

---

## 9. Failure Mechanism

Time-based PM이 실패하는 구조는 단순합니다.

```text
Over-service
→ 아직 멀쩡한 truck/component를 정비함
→ PM bay와 비용을 소모함

Under-protection
→ 빠르게 닳는 truck/component를 놓침
→ CM과 downtime이 발생함

Failure leakage
→ 특정 시점이 아니라 early/mid/late 전 구간에서 failure가 반복됨
```

따라서 평균 HI가 높다고 좋은 정책은 아닙니다.
정책의 품질은 failure-prone tail을 얼마나 잘 잡는지로 봐야 합니다.

---

## 10. Sensitivity Result

Frailty CV가 커질수록 state-aware policy의 이점이 증가했습니다.

```text
Frailty CV ↑
→ truck별 열화 편차 ↑
→ 상태 정보의 가치 ↑
→ H1/H2 우위 증가
```

해석은 명확합니다.

```text
fleet이 균질하면 시간 기준 PM도 어느 정도 버틸 수 있다.
하지만 fleet이 이질적일수록 상태 기반 PM의 가치가 커진다.
```

---

## 11. Repository Structure

```text
configs/
  c5_1.yaml
  c5_3.yaml
  c5_4.yaml

mine_env/
  C5.1~C5.4 simulation environment
  reliability state
  policy interface
  simulator logic

scripts/
  run_c5_4_sweep.py
  run_c5_4_sensitivity.py
  analyze_c5_4_mechanism.py
  plot_c5_4_results.py

tests/
  test_c5_4_config.py
  test_c5_4_pm_scheduler.py
  test_c5_4_policies.py
  test_c5_4_reliability.py
  test_c5_4_rl_interface.py
  test_c5_4_simulator.py

outputs/
  experiment outputs
  result tables
  figures
  logs

presentation_pack_c5_4/
  final presentation assets
```

---

## 12. How to Run

Install dependencies.

```bash
python -m pip install -r requirements.txt
```

Run C5.4 policy sweep.

```bash
python scripts/run_c5_4_sweep.py --config configs/c5_4.yaml
```

Run C5.4 sensitivity analysis.

```bash
python scripts/run_c5_4_sensitivity.py --config configs/c5_4.yaml
```

Analyze failure mechanism.

```bash
python scripts/analyze_c5_4_mechanism.py --config configs/c5_4.yaml
```

Plot C5.4 results.

```bash
python scripts/plot_c5_4_results.py
```

Run tests.

```bash
pytest
```

---

## 13. Evaluation Metrics

C5.4는 단일 reward score만 보지 않습니다.
정책 해석을 위해 다음 KPI를 함께 봅니다.

| KPI                | 의미                                                     |
| ------------------ | ------------------------------------------------------ |
| normalized TCO     | PM, CM, downtime, degradation, unmet demand를 합친 총비용 지표 |
| PM count           | 예방정비 횟수                                                |
| CM count           | 비계획 고장정비 횟수                                            |
| downtime           | 정비·고장으로 인한 운행 손실                                       |
| failure count      | failure 발생 수                                           |
| fulfillment        | 생산 목표 충족도                                              |
| degradation cost   | 부품/트럭 상태 소모 비용                                         |
| fleet availability | 최소 운행대수 유지 여부                                          |

---

## 14. Cost Model

C5.4의 비용은 실제 회계 비용이 아닙니다.

학습과 평가는 normalized Cost Unit(CU)을 사용합니다.

```text
1 CU = 정상 조건에서 트럭 1대가 1시간 생산적으로 운행했을 때의 기준 가치
```

포함되는 비용 항목은 다음과 같습니다.

```text
- PM direct cost
- PM downtime opportunity cost
- CM / failure cost
- off-site repair cost
- degradation cost
- queue cost
- unmet-demand cost
- fleet availability penalty
```

USD 금액은 실제 Escondida 회계값으로 주장하지 않습니다.
필요한 경우 보고서 해석용 proxy range로만 사용합니다.

---

## 15. Scope Limitations

본 프로젝트의 한계는 다음과 같습니다.

| 한계                            | 설명                                                                  |
| ----------------------------- | ------------------------------------------------------------------- |
| Proxy simulation              | 실제 광산 digital twin이 아님                                              |
| Normalized TCO                | 실제 회계 비용이 아니라 정책 비교용 비용 지표                                          |
| Parameter assumption          | 공개자료와 실험 가정을 결합한 환경                                                 |
| Synthetic reliability surface | 실제 센서 로그 기반 보정은 아님                                                  |
| RL status                     | C5.4의 본체는 heuristic policy comparison이며, PPO는 후속 확장 또는 interface 대상 |

안전한 표현은 다음입니다.

```text
C5.4는 실제 광산 운영을 복제한 시스템이 아니라,
열화 설비의 PM timing과 dispatch policy를 비교하기 위한 proxy reliability benchmark다.
```

---

## 16. Transfer Potential

C5.4의 분석 대상은 광산 그 자체가 아니라 다음 구조입니다.

```text
열화 설비
+ 운영 투입 결정
+ 정비 timing
+ 생산/가용률/비용 trade-off
```

따라서 같은 의사결정 구조는 다음 분야로 확장할 수 있습니다.

| Domain      | Transfer Target | Decision                |
| ----------- | --------------- | ----------------------- |
| 발전소         | 터빈, 펌프, 밸브      | 계속 운전, 출력 조정, 점검, 계획정비  |
| 데이터센터       | 서버, 냉각설비        | 부하 이전, 냉각장치 점검, 장애 예방   |
| 산업·군용 fleet | 차량, 엔진, 제동계     | 임무 투입, 정비 우선순위, 예비대 운용  |
| 제조공정        | RSW 전극, 공정 설비   | defect-risk 기반 점검·정비 판단 |

이 전이는 실제 현장 적용을 의미하지 않습니다.
C5.4에서 검증한 것은 “상태 정보가 PM·운영 의사결정에 들어갈 때 정책 비교가 가능하다”는 구조입니다.

---

## 17. Team

2026-1 Capstone Design
3조

| 이름  | 학번       |
| --- | -------- |
| 권영택 | 20201040 |
| 권민재 | 20231040 |
| 김수현 | 20200647 |
| 이정우 | 20211086 |

---

## 18. Status

| Version | Status                                                 |
| ------- | ------------------------------------------------------ |
| C5.1    | 초기 core simulation / heuristic foundation              |
| C5.3    | reliability surface and dispatch foundation            |
| C5.4    | final joint PM scheduling + dispatch policy comparison |

현재 README는 C5.4 기준 설명을 우선합니다.
C5.1, C5.3 관련 파일은 개발 이력과 하위 실험 근거로 보관합니다.
