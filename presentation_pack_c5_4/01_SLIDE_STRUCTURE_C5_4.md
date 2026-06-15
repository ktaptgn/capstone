# C5.4 최종 발표 PPT 구조

| 장 | 제목 | 핵심 내용 | 권장 자료 |
|---:|---|---|---|
| 1 | 표지 | C5.4 Reliability Series 명시 | 제목 텍스트 |
| 2 | 문제 정의 | 시간 기준 PM의 과잉 정비와 고장 누락 문제 | 간단한 2분할 다이어그램 |
| 3 | C5.4 의사결정 문제 | PM scheduling + dispatch joint decision | decision flow |
| 4 | 시뮬레이션 핵심 구조 | 25 trucks, 3 routes, PM bay, 365 days | 구조도 |
| 5 | 신뢰성 모델 | tire / engine / brake, frailty, sensor noise | 모델 카드 |
| 6 | 정책 설계 | H0/H_TIME vs H1/H2 vs H3/H4 | 정책 그룹 표 |
| 7 | 실험 설계 | 3 regimes × 30 held-out seeds | 실험 매트릭스 |
| 8 | 결과 요약 | H1/H2가 1위권 | regime별 순위표 |
| 9 | H1/H2가 이긴 이유 | state-aware targeted PM | state-aware vs blind 비교표 |
| 10 | Blind PM 실패 원인 | over-service + under-protection | failure_vs_endhi 그래프 |
| 11 | H3/H4 해석 | 2군 정책, 늦은 PM trade-off | 결과 요약 표 |
| 12 | 민감도 분석 | frailty CV 증가 시 상태 기반 가치 증가 | frailty_cv_curve |
| 13 | 분석 시각화 / 로그 검증 | 결과표와 그래프 기반 evidence | 4개 그래프 thumbnail |
| 14 | 한계 | in-lab benchmark, 실제 광산 아님 | limitations 카드 |
| 15 | 타분야 확장성 | 발전소, 데이터센터, fleet | 적용 분야 표 |

## 장별 핵심 수치 메모 (슬라이드 디자인 참고용)

- 2장: blind PM은 평균 HI 0.83~0.84로 "건강"해 보이지만 고장이 가장 많다 (역설).
- 3장: 결정 = (어느 트럭/부품을 PM bay로 보낼지) + (각 트럭을 A/B/C 중 어느 route로 보낼지).
- 4장: 25 trucks, 3 routes(A/B/C), PM bay 2개, 365일 campaign.
- 5장: 3-component HI, Gamma frailty(트럭별 마모율 편차), sensor noise 0.03.
- 7장: regime 3종 × held-out seed 30개(101~130). lower TCO = better.
- 8장: 모든 regime에서 순위 H1≈H2 < H3≈H4 < H_TIME < H0 (동일).
- 12장: state-aware 우위가 frailty CV 0.10에서 +33% → 0.80에서 +50%로 증가.
