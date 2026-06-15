# C5.4 발표용 그래프 사용 가이드

> 모든 그래프는 `scripts/plot_c5_4_results.py`가 분석 산출물에서 렌더 (재시뮬레이션 없음).
> PNG는 슬라이드 삽입용, SVG는 확대/편집용. 파일은 `figures/`에 있다.

## 1. c5_4_tco_boxplots

사용 슬라이드:
- 8장 결과 요약

핵심 메시지:
- H1/H2가 낮은 TCO와 안정적인 분포를 보인다.
- H0/H_TIME은 높은 TCO와 큰 분산을 보인다.

## 2. c5_4_failure_vs_endhi

사용 슬라이드:
- 10장 Blind PM 실패 원인

핵심 메시지:
- Blind PM은 평균 HI가 높아도 failure가 많다.
- State-aware PM은 낮은 HI 근처까지 lean하게 운영해도 failure가 적다.
- 높은 평균 HI가 좋은 정책이라는 뜻은 아니다.

## 3. c5_4_frailty_cv_curve

사용 슬라이드:
- 12장 민감도 분석

핵심 메시지:
- 트럭별 열화 편차가 커질수록 상태 기반 PM의 가치가 커진다.
- 상태 데이터는 fleet이 이질적일수록 더 큰 의사결정 가치를 가진다.
- 수치: state-aware 우위가 CV 0.10에서 +33% → CV 0.80에서 +50%로 단조 증가.

## 4. c5_4_failure_timing

사용 슬라이드:
- 13장 분석 시각화 / 로그 검증
또는 부록

핵심 메시지:
- Blind PM의 failure는 특정 후반부에만 몰리는 문제가 아니다.
- 캠페인 전체에 걸쳐 지속적으로 발생한다.
- 이는 주기 기반 PM 구조의 한계로 해석할 수 있다.
- 수치: blind는 early/mid/late thirds에 고르게 고장 (예: heterogeneous H0 615/664/663), state-aware는 ~0.

## 삽입 우선순위

1순위(반드시): c5_4_tco_boxplots, c5_4_failure_vs_endhi
2순위(권장): c5_4_frailty_cv_curve
3순위(부록 가능): c5_4_failure_timing
