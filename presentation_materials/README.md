# Presentation Materials Pack

This folder contains presentation-ready source copies, generated tables, chart images, slide outline, and speaker notes for:

가상 광산 시뮬레이션을 통한 마일리지 적용 설비 PM 분석 및 최소 비용 지출 정책 도출

## Use For PPT Production
- `slide_outline.md`
- `slide_script_notes.md`
- `tables/*.md`
- `figures/*.png`

## Raw Copied Evidence
Raw copied files are under `data/raw/`. They preserve source documents, configs, result summaries, analysis files, and replay logs without modification.

## Generated Files
- `data/generated/policy_result_summary.csv`
- `data/generated/cost_breakdown_by_policy.csv`
- `data/generated/pm_timing_counts.csv`
- `data/generated/missing_requested_sources.csv`
- `tables/*.md`
- `figures/*.png`

## Chart Placeholders
No chart placeholder was needed. PM timing data was available from replay logs.

## Regenerate Figures and Tables
Run from repository root:

```powershell
python scripts/build_presentation_assets.py
```

## Allowed Claims
- Escondida/Atacama 특성을 참조한 proxy DES 가상광산이다.
- time-risk factor는 C5 risk multiplier proxy다.
- cost는 CU 기반 marginal cost proxy다.
- PM bay capacity는 bay, crew, tool, tire handler를 포함한 통합 정비능력이다.
- 정책 비교는 reward가 아니라 KPI, cost, robustness 기준으로 해석한다.

## Do Not Claim
- 실제 광산을 정밀 재현했다.
- time-risk를 현장 측정 회귀계수로 제시한다.
- CU cost matrix를 실제 광산 회계 장부값으로 제시한다.
- PM bay 2개가 실제 광산 설비 수다.
- PPO/RL이 모든 baseline보다 우수하다.

## Missing Requested Source Names
See `data/generated/missing_requested_sources.csv`.
Missing exact names: final_comparison_summary_table.csv, final_comparison_summary_table.md, c5_final_metrics_table.csv, c5_policy_comparison.csv, c5_scenario_robustness.csv, c5_cost_breakdown.csv, c5_action_distribution_by_time.csv, c5_health_summary.csv, c5_final_report.json, baseline_vs_ppo_summary.json, RESULTS_ALL.csv, REPORT_DATA.md, PROJECT_SPEC.md.

## Generated Figures
- presentation_materials/figures/system_architecture.png
- presentation_materials/figures/virtual_mine_flow.png
- presentation_materials/figures/policy_kpi_comparison.png
- presentation_materials/figures/cost_breakdown.png
- presentation_materials/figures/heuristic_concept_map.png
- presentation_materials/figures/pm_timing_tradeoff.png
