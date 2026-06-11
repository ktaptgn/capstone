# Validation Report

## Checks
- Deprecated USD constants are not used in generated presentation text.
- No claim says the model is a real mine digital twin.
- No claim says time-risk factors are measured values.
- No fake numeric result values are introduced; numeric KPI values come from official CSV/logs/config.
- Result tables cite source file paths.
- 마일리지는 EOH / equivalent mileage proxy로 설명된다.
- Heuristic names use implemented C5.1 names.
- CU-based cost is used for policy comparison.
- Missing data is reported in `data/generated/missing_requested_sources.csv`.

## Missing / Placeholder
- Missing exact requested source names: final_comparison_summary_table.csv, final_comparison_summary_table.md, c5_final_metrics_table.csv, c5_policy_comparison.csv, c5_scenario_robustness.csv, c5_cost_breakdown.csv, c5_action_distribution_by_time.csv, c5_health_summary.csv, c5_final_report.json, baseline_vs_ppo_summary.json, RESULTS_ALL.csv, REPORT_DATA.md, PROJECT_SPEC.md
- Figure placeholders: None

## Warnings
- outputs/c5_1/analysis/policy_kpi_summary.csv conflicts with the official 365-day summary scale; official summary values were used.
- Queue cost and failure cost are not separate official cost fields; they are marked N/A.
- No literal mileage/odometer field was found; mileage is explained as EOH / equivalent mileage proxy.

## Created Figure Files
- presentation_materials/figures/system_architecture.png
- presentation_materials/figures/virtual_mine_flow.png
- presentation_materials/figures/policy_kpi_comparison.png
- presentation_materials/figures/cost_breakdown.png
- presentation_materials/figures/heuristic_concept_map.png
- presentation_materials/figures/pm_timing_tradeoff.png

## Copied Source Count
46
