# Slide Script Notes

## Slide 1. Title

### 핵심 메시지
프로젝트 제목과 범위를 먼저 고정한다.

### 발표자가 말할 내용
등가 마일리지와 HI 기반 PM timing 비교라고 소개한다.

### 주의할 표현
실제 광산을 복제했다고 말하지 않는다.

### 예상 질문 대응
마일리지는 실제 odometer가 아니라 equivalent operating mileage proxy라고 답한다.


## Slide 2. 프로젝트 개요

### 핵심 메시지
이 프로젝트는 정비 타이밍을 비용과 KPI로 비교하는 의사결정 프레임워크다.

### 발표자가 말할 내용
광산 트럭은 생산 목표, queue, 정비 capacity, 설비 열화가 동시에 충돌하는 사례라 설명한다.

### 주의할 표현
디지털 트윈, 실측 회계값이라는 표현을 피한다.

### 예상 질문 대응
왜 광산인가라는 질문에는 IE scheduling/maintenance trade-off가 선명한 사례라고 답한다.


## Slide 3. 프로젝트 요소 설명

### 핵심 메시지
각 object가 simulation에서 어떤 역할을 하는지 연결한다.

### 발표자가 말할 내용
Truck과 Tire HI는 상태, PM Bay는 제한자, Plant Feed Manager는 수요 목표라고 말한다.

### 주의할 표현
PM bay 2개를 실제 설비 수로 말하지 않는다.

### 예상 질문 대응
PM bay는 bay, crew, tool, tire handler를 묶은 통합 capacity라고 답한다.


## Slide 4. 시뮬레이션 환경 구조

### 핵심 메시지
DES 흐름을 event와 state update 중심으로 설명한다.

### 발표자가 말할 내용
dispatch/PM policy가 action을 내고, DES가 truck state와 KPI를 업데이트한다고 말한다.

### 주의할 표현
operator dashboard 기능 설명으로 확장하지 않는다.

### 예상 질문 대응
시각화 MVP는 policy log replay라고 답한다.


## Slide 5. 시뮬레이션 세부 스펙

### 핵심 메시지
config-driven 값을 보여주고 proxy/assumption을 구분한다.

### 발표자가 말할 내용
fleet 8, payload 350, crusher 2, PM bay 2, 365 days 등 config 값을 짚는다.

### 주의할 표현
shovel count처럼 config에 없는 값은 presentation flow label로만 말한다.

### 예상 질문 대응
실제 값이냐는 질문에는 parameter defense table의 proxy 분류를 근거로 답한다.


## Slide 6. 마일리지 / HI / PM 판단 구조

### 핵심 메시지
마일리지를 구현상 equivalent usage proxy로 정리한다.

### 발표자가 말할 내용
EOH/TKPH/severity가 누적되면 HI가 내려가고 PM 필요도가 오른다는 흐름으로 말한다.

### 주의할 표현
실제 odometer field가 있다고 말하지 않는다.

### 예상 질문 대응
마일리지 표현은 발표 제목과 구현 사이를 연결하는 용어라고 답한다.


## Slide 7. 휴리스틱 비교 구조

### 핵심 메시지
정책만 바꾸고 환경은 같게 유지한 comparison이라고 설명한다.

### 발표자가 말할 내용
H0-H4 이름과 역할을 짧게 소개한다.

### 주의할 표현
Drop Zone을 H4로 말하지 않는다.

### 예상 질문 대응
Drop Zone은 future environment scenario라 답한다.


## Slide 8. 각 휴리스틱 설명

### 핵심 메시지
각 정책의 입력 정보와 약점을 함께 말한다.

### 발표자가 말할 내용
H0 baseline, H1 queue/bottleneck, H2 HI risk, H3 CU value, H4 backpressure로 구분한다.

### 주의할 표현
어느 하나를 무조건 최적이라고 말하지 않는다.

### 예상 질문 대응
H3는 현재 cost weighting과 sweep에서 좋은 정책이라고 답한다.


## Slide 9. 결과 비교 — KPI

### 핵심 메시지
공식 365-day result를 사용해 정책 ranking을 말한다.

### 발표자가 말할 내용
total cost, completed loads, unmet demand, fulfillment를 같이 본다.

### 주의할 표현
analysis 폴더의 작은 scale table과 혼용하지 않는다.

### 예상 질문 대응
충돌 값이 있으면 official summary를 우선했다고 답한다.


## Slide 10. 결과 비교 — 비용 분해

### 핵심 메시지
CU 비용 분해로 어떤 비용이 ranking을 만드는지 설명한다.

### 발표자가 말할 내용
PM direct, downtime, degradation, target shortfall을 분리해 말한다.

### 주의할 표현
queue/failure cost가 별도 field인 것처럼 만들지 않는다.

### 예상 질문 대응
N/A는 missing field를 숨기지 않은 표시라고 답한다.


## Slide 11. 정책 해석

### 핵심 메시지
정책 선택은 reward가 아니라 KPI, cost, robustness 기준이다.

### 발표자가 말할 내용
현재 sweep에서는 H3가 cost와 fulfillment에서 가장 강하다고 말하되 과장하지 않는다.

### 주의할 표현
통계적 유의성을 주장하지 않는다.

### 예상 질문 대응
multi-seed가 제한적이라 sensitivity가 필요하다고 답한다.


## Slide 12. 프로젝트 한계점

### 핵심 메시지
한계는 방어 포인트로 제시한다.

### 발표자가 말할 내용
proxy DES, no telemetry, CU cost, time-risk proxy, limited robustness를 정리한다.

### 주의할 표현
약점 숨기기처럼 말하지 않는다.

### 예상 질문 대응
범위를 명확히 잘라서 구현 신뢰도를 높였다고 답한다.


## Slide 13. 개선점

### 핵심 메시지
다음 단계는 데이터 calibration과 sensitivity다.

### 발표자가 말할 내용
telemetry, PM bay sensitivity, cost weight sensitivity, RUL refinement를 우선순위로 제안한다.

### 주의할 표현
지금 구현된 것처럼 말하지 않는다.

### 예상 질문 대응
개선안은 validation roadmap이라고 답한다.


## Slide 14. 타 분야 응용

### 핵심 메시지
열화 설비 PM timing 문제로 일반화한다.

### 발표자가 말할 내용
AGV, 반도체 후공정, RSW tip, 데이터센터, 발전/풍력, 군용 정비를 연결한다.

### 주의할 표현
이미 실험 완료한 적용 사례로 말하지 않는다.

### 예상 질문 대응
공통 구조는 degradation proxy + maintenance action + objective라고 답한다.


## Slide 15. Final Message

### 핵심 메시지
핵심 메시지를 한 문장으로 닫는다.

### 발표자가 말할 내용
정밀 복제가 아니라 PM 의사결정 프레임워크라는 점을 강조한다.

### 주의할 표현
성과를 실제 광산 성능으로 과장하지 않는다.

### 예상 질문 대응
가치가 어디 있냐는 질문에는 비교 가능한 정책 평가 구조라고 답한다.
