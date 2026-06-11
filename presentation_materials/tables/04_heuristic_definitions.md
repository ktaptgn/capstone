# 04 Heuristic Definitions

| Heuristic | Rule Summary | Required Inputs | Expected Behavior | Risk |
| --- | --- | --- | --- | --- |
| H0 Baseline | PM due가 0 이하이면 PM Bay로 보내고, 아니면 기본 crusher dispatch를 수행한다. | pm_due_hours, demand pressure, next_crusher | 비교 기준으로 해석이 단순하다. | 병목, HI risk, queue pressure를 적극적으로 반영하지 못한다. |
| H1 Bottleneck Dispatch | queue/processing 병목이 크면 hold 또는 PM window를 만들고, 아니면 건강한 truck을 dispatch한다. | queue_time, demand pressure, truck/tire risk | 병목 구간에서 불필요한 투입을 줄일 수 있다. | 생산 압력이 높을 때 과도하게 보수적인 결과가 날 수 있다. |
| H2 PM Risk Priority | Truck HI, Tire HI, PM due 기반 risk가 threshold 이상이면 PM을 우선한다. | truck_hi, tire_hi, pm_due_hours, demand pressure | 고위험 설비를 조기에 정비해 상태 저하를 억제한다. | 생산 기회손실과 unmet demand가 커질 수 있다. |
| H3 Cost Unit Value | 운행 가치와 PM 가치를 CU 비용 proxy로 비교해 더 높은 operational value를 선택한다. | demand pressure, truck/tire HI, PM cost, degradation cost | 생산, PM, downtime, degradation을 하나의 비용 언어로 비교한다. | 가중치와 비용 proxy 설정에 민감하다. |
| H4 Flow / Backpressure | downstream pressure와 backpressure를 보고 high-demand release, PM, standby를 선택한다. | demand pressure, queue_time, truck/tire risk | 전체 flow 관점의 병목 완화 설명이 쉽다. | 현재 결과에서는 H1과 같은 성능 패턴을 보인다. |

Source: docs/source/C5_ALGORITHM_EQUATION_IMPLEMENTATION_ADDENDUM.md, docs/c5_1/C5_1_POLICY_SPEC.md, mine_env/policies/*.py
