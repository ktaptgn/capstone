# Source Manifest

이 압축파일(`c5_4_claude_design_pack.zip`)에 포함된 모든 파일 목록이다.

## 발표 입력 문서 (이 팩에서 새로 작성)

| 분류 | 파일 | 역할 |
|---|---|---|
| guide | 00_README_FOR_CLAUDE_DESIGN.md | Claude Design 작업 지침 + 원칙 |
| guide | 01_SLIDE_STRUCTURE_C5_4.md | 15장 슬라이드 구성안 |
| guide | 02_C5_4_KEY_MESSAGE.md | 핵심 메시지 + 금지 표현 |
| guide | 03_C5_4_POLICY_TABLE.md | 정책 6종 설계 표 |
| guide | 04_C5_4_RESULT_TABLES.md | regime별 순위 + 실제 TCO 수치 |
| guide | 05_C5_4_GRAPH_USAGE_GUIDE.md | 그래프 4종 사용 가이드 |
| guide | 06_C5_4_SCRIPT_NOTES.md | 슬라이드별 발표 대본 초안 |
| guide | 07_LIMITATIONS_AND_DEFENSE.md | 한계 + 방어 문장 |
| guide | 08_SOURCE_MANIFEST.md | 본 파일 |

## 근거 자료 (저장소에서 복사)

| 분류 | 파일 | 역할 | PPT 사용 위치 |
|---|---|---|---|
| config | configs/c5_4.yaml | C5.4 실험 설정 | 4~7장 |
| report | reports/07_C5_4_RESULTS.md | 메인 결과 보고서 (자동 생성 표) | 8~11장 |
| report | reports/07_C5_4_INTERPRETATION.md | 결과 해설·메커니즘 서술 (수기, sweep 재실행 시 보존) | 8~11장 |
| report | reports/08_C5_4_SENSITIVITY.md | 민감도 분석 (자동 생성 표) | 12장 |
| report | reports/08_C5_4_SENSITIVITY_FINDINGS.md | 민감도 핵심 발견 (수기) | 12장 |
| report | reports/09_C5_4_MECHANISM.md | 실패 메커니즘 분석 (자동 생성 표) | 9~11장 |
| report | reports/09_C5_4_MECHANISM_FINDINGS.md | 메커니즘 핵심 발견 (수기) | 9~11장 |
| figure | figures/c5_4_tco_boxplots.png/.svg | TCO 결과 그래프 | 8장 |
| figure | figures/c5_4_failure_vs_endhi.png/.svg | 실패 원인 그래프 | 10장 |
| figure | figures/c5_4_frailty_cv_curve.png/.svg | 민감도 그래프 | 12장 |
| figure | figures/c5_4_failure_timing.png/.svg | 실패 시점 그래프 | 13장 |
| result | results/c5_4_policy_comparison.csv | 정책별 raw result (long) | 8장, 부록 |
| result | results/c5_4_policy_comparison.json | 정책별 집계 result | 8장, 부록 |
| result | results/sensitivity/c5_4_sensitivity_frailty_cv.json | frailty CV sweep | 12장 |
| result | results/sensitivity/c5_4_sensitivity_cbm_threshold.json | CBM threshold robustness | 12장 |
| result | results/sensitivity/c5_4_sensitivity_pm_bay.json | PM bay 수 민감도 | 12장 |
| result | results/sensitivity/c5_4_sensitivity_blind_cadence.json | blind 주기 robustness | 12장 |
| result | results/mechanism/c5_4_mechanism.json | 실패 메커니즘 raw | 9~11장 |
| script | source_scripts/run_c5_4_sweep.py | 메인 sweep 실행 | (근거) |
| script | source_scripts/run_c5_4_sensitivity.py | 민감도 실행 | (근거) |
| script | source_scripts/analyze_c5_4_mechanism.py | 메커니즘 분석 | (근거) |
| script | source_scripts/plot_c5_4_results.py | 그래프 렌더 | (근거) |
| code | source_scripts/mine_env/config_c5_4.py | 설정 로더 | (근거) |
| code | source_scripts/mine_env/reliability_c5_4.py | 신뢰성 모델 | (근거) |
| code | source_scripts/mine_env/costs_c5_4.py | 비용 모델 | (근거) |
| code | source_scripts/mine_env/pm_scheduler_c5_4.py | PM 스케줄링 family | (근거) |
| code | source_scripts/mine_env/simulator_c5_4.py | joint 시뮬레이터 | (근거) |
| code | source_scripts/mine_env/rl_interface_c5_4.py | PPO 인터페이스 stub | (근거) |

## 비고

- `evidence/` 폴더는 비어 있다. 지시문이 요구한 per-policy×seed(seed 101) 샘플 로그 형식은
  저장소에 존재하지 않으며(로그는 base_sweep / sensitivity / mechanism 단위의 집계 프로세스 로그뿐),
  지시문상 로그 부재 시 생략이 허용된다. 정량 근거는 results/의 summary·sensitivity·mechanism JSON으로 갈음한다.
- 그래프는 PNG(슬라이드 삽입)와 SVG(확대/편집) 모두 포함했다.
