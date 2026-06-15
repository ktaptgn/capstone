# C5.4 Claude Design Presentation Pack

이 압축파일은 캡스톤 최종 발표 PPT 제작을 위한 C5.4 입력 자료다.

## 발표 주제

가상 광산 신뢰성 시뮬레이션 기반 상태 인지형 PM·배차 정책 비교

## 핵심 메시지

C5.4는 C5.1의 단순 PM 정책 비교를 확장하여,
25대 트럭의 tire / engine / brake 상태와 route 선택을 함께 고려한
PM scheduling + dispatch joint decision 실험이다.

30개 held-out seed와 3개 operating regime에서
H1/H2 상태 인지형 정책이 H0/H_TIME blind periodic PM보다
안정적으로 낮은 TCO를 보였다.

## Claude Design 작업 원칙

- 긴 표를 그대로 넣지 말 것.
- 시뮬레이션 세부 스펙은 최소화할 것.
- 결과는 H1/H2 state-aware 정책의 우위 중심으로 설명할 것.
- 기존 C5.1의 "H3 최종 추천" 결과와 섞지 말 것.
- C5.4는 in-lab benchmark이며 실제 광산 digital twin이라고 주장하지 말 것.
- 대시보드/PM 앱 완성 시연처럼 표현하지 말 것.
- 분석 시각화와 로그 기반 검증이라고 표현할 것.

## 필수 삽입 그래프

1. c5_4_tco_boxplots
2. c5_4_failure_vs_endhi
3. c5_4_frailty_cv_curve
4. c5_4_failure_timing

## 이 팩의 구조

```
00_README_FOR_CLAUDE_DESIGN.md   이 문서
01_SLIDE_STRUCTURE_C5_4.md       15장 슬라이드 구성안
02_C5_4_KEY_MESSAGE.md           한 줄 요약 + 금지 표현
03_C5_4_POLICY_TABLE.md          정책 6종 설계 표
04_C5_4_RESULT_TABLES.md         regime별 순위 + 실제 TCO 수치
05_C5_4_GRAPH_USAGE_GUIDE.md     그래프 4종 사용 가이드
06_C5_4_SCRIPT_NOTES.md          슬라이드별 발표 대본 초안
07_LIMITATIONS_AND_DEFENSE.md    한계 + 방어 문장
08_SOURCE_MANIFEST.md            포함 파일 목록

configs/        C5.4 실험 설정 (c5_4.yaml)
reports/        결과/민감도/메커니즘 보고서 (원문)
results/        정책 비교 CSV/JSON + sensitivity/mechanism JSON
figures/        발표용 그래프 PNG/SVG 4종
source_scripts/ 근거 확인용 실험 코드 (직접 설명 불요)
evidence/       (per-policy×seed 샘플 로그 — 해당 형식 미생성, 비어 있음)
```

## 한 문장 요약 (발표 표지/도입용)

> 시간 기준으로 차량 전체를 반복 정비하는 blind PM은 평균 건강도는 높게 유지하지만,
> 빨리 닳는 트럭과 부품을 놓쳐 고장을 낸다. C5.4는 상태(HI/risk)를 보고
> 위험 부품만 골라 정비하는 state-aware PM이 모든 운영 조건에서 더 낮은 총비용(TCO)을 낸다는 것을
> 30 seed × 3 regime 시뮬레이션으로 보인다.
