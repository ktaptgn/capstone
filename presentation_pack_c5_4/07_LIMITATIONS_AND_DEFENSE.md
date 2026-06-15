# C5.4 한계 및 방어 문장

## 한계

- C5.4는 실제 광산 digital twin이 아니다.
- 공개 자료와 산업공학적 가정에 기반한 in-lab benchmark다.
- 비용은 실제 회계 비용이 아니라 normalized TCO다.
- route, wear, frailty, cost parameter는 실험 목적의 proxy 값이다.
- PPO/RL은 본 발표의 정량 결과로 주장하지 않는다.
- dashboard/PM app은 완성 시연물이 아니라 후속 UI 설계 방향이다.

## 방어 문장

본 프로젝트의 목적은 실제 광산을 완전히 재현하는 것이 아니라,
열화 설비 fleet에서 상태 기반 PM이 주기 기반 PM보다 어떤 조건에서 유리한지
시뮬레이션으로 비교하는 것입니다.

C5.4는 실제 비용 예측 모델이 아니라,
정책 간 상대 성능을 비교하기 위한 normalized TCO 기반 실험입니다.

H1/H2가 좋은 결과를 보인 이유는 threshold를 임의로 맞췄기 때문이 아니라,
트럭별·부품별 열화 차이를 상태 정보로 반영했기 때문입니다.

## 예상 질문 대비 (anti-overclaim 근거)

Q. blind PM의 주기를 일부러 나쁘게 잡은 것 아닌가?
A. 아닙니다. blind 주기는 fast-frailty-tail에 맞춘 가장 타이트한(유리한) 값입니다.
   주기를 3→8일로 sweep해도 blind는 전 구간에서 state-aware보다 비쌌습니다 (cadence-robust).

Q. CBM threshold를 결과에 맞춰 튜닝한 것 아닌가?
A. 아닙니다. C6.1 grid-search 동결값을 그대로 썼고, ±20% 흔들어도 H1 TCO 변화는 0.5% 미만입니다.

Q. state-aware의 end HI 0.3은 트럭이 너무 망가진 것 아닌가?
A. 아닙니다. PM 임계값 근처에서 lean하게 운영한 의도된 결과이며, 고장은 거의 0입니다.
   end HI는 캠페인 종료 시점 스냅샷일 뿐이고, timing/causal 분석과 함께 읽어야 합니다.

Q. state-aware가 단지 수요를 못 채운 것 아닌가?
A. 비-극단 regime에서는 모든 정책의 fulfilment가 1.000입니다.
   즉 TCO 격차는 생산 손실이 아니라 순수한 정비 효율 차이입니다.
