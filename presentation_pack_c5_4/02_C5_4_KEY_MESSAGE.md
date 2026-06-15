# C5.4 Key Message

## 한 줄 요약

C5.4는 광산 트럭 fleet에서 PM scheduling과 dispatch를 동시에 결정하는 신뢰성 기반 운영정책 비교 실험이다.

## 발표 핵심

- H0/H_TIME은 blind periodic PM 계열이다.
- H1/H2는 상태 인지형 PM 계열이다.
- H3/H4는 cost-value / flow-backpressure 계열의 2군 정책이다.
- 핵심 결과는 H1/H2가 H0/H_TIME보다 모든 regime에서 안정적으로 낮은 TCO를 보였다는 점이다.
- H1/H2의 차이는 regime에 따라 바뀌지만, 실질적으로는 state-aware Tier 1으로 묶어 설명하는 것이 안전하다.
- H4는 실패 정책이 아니라 blind PM보다 낫지만 H1/H2보다 늦게 정비해 failure tail이 생기는 2군 정책이다.

## 수치로 본 핵심 (방어용 근거)

- state-aware(H1/H2)가 blind(H0/H_TIME) 대비 TCO를 40.4% / 24.9% / 17.0% 낮춤
  (heterogeneous / high_stress / high_demand_high_stress 순).
- 모든 regime에서 30/30 paired seed가 H0 대비 더 저렴 (H_TIME은 28~30/30).
- 순위 H1≈H2 < H3≈H4 < H_TIME < H0 가 3개 regime에서 동일 — pair 내 순서만 noise로 바뀜.
- blind는 정비를 적게 해서가 아니라, full-vehicle service를 반복하며 빠른-마모 트럭/타이어를 놓쳐 실패.

## 발표에서 절대 피할 표현

- H3가 최종 추천 정책이다.
- 실제 Escondida 광산을 재현했다.
- 실제 현장 비용을 그대로 계산했다.
- 대시보드와 PM 앱이 완성 구현되었다.
- C5.4 결과가 수학적 전역 최적해다.
