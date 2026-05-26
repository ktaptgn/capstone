# C5.1 Dashboard Analysis Mapping

## Overview Cards

- `total_cost` -> Total Cost / 총 운영비용
- `demand_fulfillment_rate` -> Demand Fulfillment / 수요 충족률
- `average_available_trucks` -> Available Trucks / 가용 트럭
- `pm_cost` -> PM Cost / PM 비용
- `unmet_demand` -> Unmet Demand / 미충족 수요
- `queue_time` -> Queue Time / 대기시간

## Policy Comparison Page

- Source snapshot: `ui/operator_dashboard/public/c5_1/policy_comparison.json`
- Analysis source: `outputs/c5_1/analysis/policy_kpi_summary.csv`
- Purpose: show H0-H4 KPI table and policy-level comparison.
- Presentation interpretation: use this page to show that policies are compared under the same C5.1 environment and KPI definitions.

## Heuristic Analysis Page

- Source snapshot: `ui/operator_dashboard/public/c5_1/dashboard_analysis.json`
- `recommended_policy` -> 추천 정책 card
- `best_by_kpi` -> KPI별 우수 정책 cards
- `h0_improvement` -> H0 대비 개선율 table
- `stability` -> Seed 안정성 table
- `tradeoff_notes_ko` -> Trade-off 해석 panel
- `missing_kpis` -> 누락 KPI warning
- `limitations_ko` -> 분석 한계 section

## PM Worker App Link

- Source snapshot: `ui/pm_worker_app/public/c5_1/work_orders.json`
- Purpose: show that selected policy results can be converted into PM Work Order data.
- Presentation interpretation: this is an execution mock, not a native Android production build.

## Warning

Composite score is a presentation helper. Do not label it as a mathematical optimum.
