# 02 Project Elements

| Element | Role | Main Variables | Presentation Meaning |
| --- | --- | --- | --- |
| Truck | 광석 운반 설비 | truck_id, truck_hi, state, location | PM 또는 운행 의사결정 대상 |
| Tire HI | 타이어 열화 상태 | tire_hi, min threshold | 등가 마일리지 proxy가 누적되며 감소하는 상태값 |
| Truck HI | 차량 본체 상태 | truck_hi, pm_due_hours | 고장위험과 PM 필요도를 표현하는 proxy |
| Shovel | 상차 지점 | Shovel A/B/C presentation label | 운반 flow 시작점 |
| Crusher 1 / Crusher 2 | 하역/처리 지점 | crusher_count=2 | downstream capacity와 queue가 생기는 지점 |
| PM Bay | 통합 정비능력 | pm_bay_capacity | bay, crew, tool, tire handler를 묶은 capacity proxy |
| Plant Feed Manager | 수요/목표 관리 | daily_loads, variation | concentrator feed target을 맞추는 상위 요구 |
| Time-risk / seasonal risk | 상황별 위험 multiplier proxy | time-risk factor | 측정 회귀계수가 아니라 C5 risk multiplier proxy |
| Cost Unit | 정책 비교 단위 | normalized_cu | 실제 회계값이 아닌 marginal cost proxy |
