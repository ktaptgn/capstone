# C5.1 Screenshot Guide

## Screenshot 1. Operator Dashboard - Overview

### Purpose
Shows the control-tower view for demand, fleet status, PM bay state, and recommended actions.

### Slide Use
System Overview

### Presenter Message
"대시보드는 시뮬레이션 결과를 운영자가 읽을 수 있는 형태로 보여줍니다. 이 화면은 현재 수요, 트럭 상태, PM 대기 상황을 한 번에 확인하는 관제 화면입니다."

### Do Not Say
"현장 시스템과 동일하게 동작합니다."

## Screenshot 2. Operator Dashboard - Policy Comparison

### Purpose
Shows H0-H4 KPI comparison using generated C5.1 policy summary data.

### Slide Use
H0-H4 Policy Comparison

### Presenter Message
"H0는 baseline이고 H1-H4는 같은 환경과 seed 조건에서 비교한 휴리스틱 정책입니다. 비용, 수요 충족률, PM 비용, 대기시간을 함께 봅니다."

### Do Not Say
"한 KPI만으로 정책 우열이 완전히 결정됩니다."

## Screenshot 3. Operator Dashboard - Heuristic Analysis

### Purpose
Shows that H0-H4 comparison is not just a raw table. The dashboard interprets policy ranking, H0 improvement, seed stability, trade-offs, and missing KPI.

### Slide Use
Heuristic Comparison Result

### Presenter Message
"현재 KPI 가중 기준에서는 H3가 추천 정책으로 표시됩니다. 단, 이는 현재 C5.1 가정과 3개 seed 기준의 1차 비교 결과입니다."

### Do Not Say
"H3가 모든 상황에서 항상 최고입니다."

## Screenshot 4. Operator Dashboard - PM Planning / Work Orders

### Purpose
Shows that the selected policy result can be converted into PM work orders.

### Slide Use
PM Scheduling Output

### Presenter Message
"H3 결과에서 생성한 Work Order가 PM 작업 목록으로 이어집니다. 이 단계는 분석 결과를 정비 실행 데이터로 연결하는 부분입니다."

### Do Not Say
"생성된 Work Order가 실제 현장 시스템에 자동 반영됩니다."

## Screenshot 5. Operator Dashboard - Scenario Replay

### Purpose
Shows replay-style visualization of policy logs if the screen is stable during demo.

### Slide Use
Simulation Replay

### Presenter Message
"시나리오 재생은 정책 로그를 다시 보여주는 MVP입니다. 운영자 dashboard 전체 기능이나 실시간 관제 시스템은 아닙니다."

### Do Not Say
"실시간 운영 시스템입니다."

## Screenshot 6. PM Worker App - Today PM List

### Purpose
Shows the mobile worker-facing PM target list and priority order.

### Slide Use
PM Worker Execution

### Presenter Message
"PM worker app은 오늘 작업할 PM 대상과 우선순위를 보여줍니다. 현장 작업자는 예상 소요시간과 PM 사유를 확인할 수 있습니다."

### Do Not Say
"native Android 앱으로 배포 완료했습니다."

## Screenshot 7. PM Worker App - Truck Detail

### Purpose
Shows truck detail, Tire HI, component state, and expected PM.

### Slide Use
Maintenance Detail

### Presenter Message
"Truck 상세 화면은 작업자가 특정 장비의 Health Index와 예상 PM 시점을 확인하는 화면입니다."

### Do Not Say
"센서 데이터와 직접 실시간 연동되어 있습니다."

## Screenshot 8. PM Worker App - PM Checklist

### Purpose
Shows practical PM execution language such as Work Order, PM 대상, 예상 소요시간, and 작업 완료.

### Slide Use
Work Order Execution

### Presenter Message
"이 화면은 분석 결과를 작업자가 수행 가능한 PM 작업 단위로 바꾸는 역할을 합니다."

### Do Not Say
"체크리스트가 실제 정비 표준 절차를 모두 대체합니다."

## Screenshot 9. PM Worker App - Limited Chatbot Mock

### Purpose
Shows fixed PM help responses for expected PM time, duration, and policy reason.

### Slide Use
Worker Assistance Mock

### Presenter Message
"PM 도움말은 자유 대화형 AI가 아니라 제한된 도움말 mock입니다. PM 시점, 예상 소요시간, 선정 이유만 안내합니다."

### Do Not Say
"실제 LLM 챗봇이 운영 판단을 대신합니다."
