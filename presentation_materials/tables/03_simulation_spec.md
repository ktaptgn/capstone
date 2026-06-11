# 03 Simulation Spec

| Spec | Value | Classification | Source File | Presentation Caution |
| --- | --- | --- | --- | --- |
| simulation_method | C5.1 DES | Fixed | configs/c5_1.yaml | event-based virtual mine simulation |
| fleet size | 8 | Config | configs/c5_1.yaml | 실제 광산 설비 수가 아닌 C5.1 proxy fleet |
| minimum operating trucks | N/A | Not explicit | N/A | 현재 config에 별도 literal field 없음 |
| truck model proxy | large haul truck proxy | Presentation label | docs/source/03_EVIDENCE_AND_SOURCE_REGISTER.md | 특정 실제 모델 재현으로 말하지 않음 |
| payload | 350 | Proxy | configs/c5_1.yaml | simplified average payload |
| shovel count | 3 presentation flow nodes | Presentation label | slide request | 현재 config에는 shovel_count literal field 없음 |
| crusher count | 2 | Fixed | configs/c5_1.yaml | current C5 environment |
| PM bay capacity | 2 | Proxy | configs/maintenance_c5_1.yaml | 통합 정비능력 |
| tire count per truck | N/A | Not explicit | N/A | 현재 simulation state는 aggregate tire_hi를 사용 |
| initial Truck HI | 0.92 | Config | configs/c5_1.yaml | state proxy |
| initial Tire HI | 0.88 | Config | configs/c5_1.yaml | state proxy |
| time slot factor | C5 risk multiplier proxy | Proxy concept | docs/source/C5_PM_BAY_AND_TIME_RISK_DEFENSE.md | 실측값으로 말하지 않음 |
| demand scenarios | daily_loads=18, variation=3 | Config | configs/c5_1.yaml | same seed/scenario comparison |
| cost unit | normalized_cu | Fixed | configs/cost_model_c5_1.yaml | CU 기반 비교 |
