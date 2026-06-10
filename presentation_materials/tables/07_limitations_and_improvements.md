# 07 Limitations and Improvements

## Limitations

| Limitation | Meaning | Presentation Defense |
| --- | --- | --- |
| 실제 광산 digital twin 아님 | Escondida/Atacama 특성을 참조한 proxy DES | 정밀 복제가 아니라 의사결정 프레임워크 |
| 파라미터는 proxy / assumption 포함 | payload, mine scale, HI loss는 단순화 | parameter defense table에 proxy로 분리 |
| 실제 tire sensor / telemetry 없음 | HI는 sensor calibration 값이 아님 | EOH/TKPH/severity 기반 proxy로 설명 |
| CU cost는 실제 회계값 아님 | normalized marginal cost proxy | 정책 비교용 내부 단위 |
| time-risk는 측정 회귀계수 아님 | C5 risk multiplier proxy | 실측값이라고 말하지 않음 |
| seed / scenario / sensitivity 추가 필요 | 현재 multi-seed는 제한적 | robustness 확장 필요 |
| PM crew scheduling은 범위 밖 | PM bay가 통합 정비능력을 대표 | 별도 crew roster 모델은 future work |
| multi-agent RL은 범위 밖 | C5.1은 H0-H4 comparison foundation | RL은 primary target 아님 |

## Future Improvements

| Improvement | Expected Value | Priority |
| --- | --- | --- |
| 실제 telemetry / tire sensor calibration | HI와 RUL proxy 신뢰도 향상 | High |
| multi-seed robustness | 정책 ranking 안정성 확인 | High |
| 30일 / 52주 continuous evaluation | 운영 기간별 PM timing 평가 | Medium |
| PM bay 1 vs 2 sensitivity | 정비 capacity 병목 영향 분리 | High |
| cost weight low/base/high sensitivity | CU weighting 민감도 확인 | High |
| route roughness and demand shock scenario | 실제 운영 충격에 가까운 stress test | Medium |
| RUL proxy refinement | PM 필요도 판단 개선 | High |
| dashboard integration | 운영자 설명과 replay 강화 | Low |
| field app integration | 작업지시 lifecycle 연결 | Low |
