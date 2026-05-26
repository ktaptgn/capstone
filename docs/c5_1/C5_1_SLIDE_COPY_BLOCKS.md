# C5.1 Slide Copy Blocks

## 1. Problem Definition

C5.1은 광산 트럭 운송 시뮬레이션에서 주어진 수요를 만족하면서 PM 비용과 운영 손실을 줄이기 위한 운행 스케줄 정책을 비교한다.

트럭은 운반 작업과 PM 작업 사이에서 선택된다. 정책의 목표는 단순히 PM을 줄이는 것이 아니라 수요 미충족, 대기시간, 다운타임, PM 비용을 함께 줄이는 것이다.

## 2. Simulation Structure

동일한 C5.1 환경에서 H0-H4 정책을 실행한다.

비교 조건은 동일하다.

- 같은 demand scenario
- 같은 seed set
- 같은 cost model
- 같은 maintenance action model
- 같은 KPI set

생성 결과는 policy log, KPI summary, dashboard analysis JSON으로 저장된다.

## 3. H0-H4 Heuristic Comparison

H0는 baseline이다.

H1-H4는 dispatch와 PM 판단 기준이 다른 휴리스틱 정책이다.

현재 3개 seed 기준의 1차 비교에서는 H3가 총 운영비용, 수요 충족률, 미충족 수요에서 가장 좋은 결과를 보였다.

H1과 H4는 대기시간, PM 비용, 총 다운타임에서 강점이 있다.

H2는 총 운영비용 표준편차 기준으로 가장 안정적이다.

## 4. Dashboard Result Interpretation

대시보드는 React 안에서 전체 분석을 다시 계산하지 않는다.

Python 분석 스크립트가 `dashboard_analysis.json`을 생성하고, dashboard는 이 파일을 읽어 결과를 표시한다.

추천 정책은 `H3`이다.

표현은 항상 "현재 KPI 기준 추천 정책"으로 제한한다.

"항상 최고인 정책"이라고 말하지 않는다.

## 5. PM Worker App Role

PM worker app은 Work Order를 작업자가 읽을 수 있는 형태로 보여준다.

주요 정보는 PM 대상, 우선순위, 예상 소요시간, PM 선정 이유, 작업 기록이다.

PM 도움말은 제한된 mock이다. 자유 대화형 AI가 아니라 PM 시점, 예상 소요시간, PM 선정 이유만 안내한다.

## 6. RL Future Work

RL은 C5.1의 현재 구현 대상이 아니다.

RL 비교는 별도 RL Lab 또는 별도 repository에서 후속 진행한다.

현재 발표에서는 heuristic baseline과 simulation visualization을 중심으로 설명한다.

## 7. Limitations

현재 결과는 3개 seed 기준의 1차 비교다.

비용 값은 정규화 비용이다.

결과는 현재 C5.1 가정과 설정에 의존한다.

`failure_count`는 현재 생성 데이터에 포함되지 않아 순위 계산에서 제외했다.

Drop Zone은 H0-H4 비교에 포함되지 않는다.
