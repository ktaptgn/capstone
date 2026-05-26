# C5.1 Presentation Runbook

## Purpose

This runbook prepares the current C5.1 simulation, heuristic analysis, operator dashboard, and PM worker app for capstone presentation. It does not add algorithms, RL training, Drop Zone, native Android build, or production backend behavior.

## 1. Generate Policy Comparison Outputs

```powershell
cd C:\working\Capstone

python scripts/run_c5_1_policy_sweep.py --config configs/c5_1.yaml --policies H0 H1 H2 H3 H4 --seeds 1 2 3
```

Outputs:

- `outputs/c5_1/logs/*.json`
- `outputs/c5_1/summary/policy_comparison.csv`
- `outputs/c5_1/summary/policy_comparison.json`

Use this to explain that H0-H4 run under the same C5.1 environment, seed set, demand scenario, and KPI definitions.

## 2. Generate Heuristic Analysis

```powershell
python scripts/analyze_c5_1_heuristics.py --summary outputs/c5_1/summary/policy_comparison.csv
```

Outputs:

- `outputs/c5_1/analysis/dashboard_analysis.json`
- `outputs/c5_1/analysis/policy_kpi_summary.csv`
- `outputs/c5_1/analysis/h0_improvement_table.csv`
- `outputs/c5_1/analysis/policy_ranking_table.csv`
- `outputs/c5_1/analysis/policy_stability_table.csv`
- `docs/c5_1/C5_1_HEURISTIC_COMPARISON_ANALYSIS.md`

Presenter note: say "H3 is recommended under the current C5.1 KPI weighting. It is not a mathematical global optimum."

## 3. Generate Work Orders

```powershell
python scripts/export_work_orders.py --policy H3 --seed 1
```

Outputs:

- `outputs/c5_1/work_orders/work_orders_H3_seed1.json`
- `outputs/c5_1/work_orders/pm_feedback_log.json`

Use this to connect the dashboard result to PM worker execution screens.

## 4. Export UI Snapshots

```powershell
python scripts/export_ui_snapshots.py
```

Outputs:

- `ui/operator_dashboard/public/c5_1/policy_comparison.json`
- `ui/operator_dashboard/public/c5_1/dashboard_analysis.json`
- `ui/operator_dashboard/public/c5_1/sample_log.json`
- `ui/operator_dashboard/public/c5_1/work_orders.json`
- `ui/pm_worker_app/public/c5_1/work_orders.json`
- `ui/pm_worker_app/public/c5_1/pm_feedback_log.json`

Generated JSON files under `outputs/` and `ui/**/public/c5_1/` are local generated artifacts. Do not commit them unless repository policy explicitly changes.

## 5. Run Operator Dashboard

```powershell
cd C:\working\Capstone\ui\operator_dashboard
npm run dev
```

Open the local URL printed by Vite. Show:

- 전체 현황
- 정책 비교
- 휴리스틱 분석
- 시나리오 재생 if stable

## 6. Run PM Worker App

```powershell
cd C:\working\Capstone\ui\pm_worker_app
npm run dev
```

Open the local URL printed by Vite. Show:

- 오늘 PM
- Truck 상세
- 작업 기록
- PM 도움말

## 7. One-command Asset Preparation

```powershell
cd C:\working\Capstone
python scripts/prepare_c5_1_presentation_assets.py
```

This runs the policy sweep, heuristic analysis, H3 work order export, and UI snapshot export.

## 8. Screenshots to Capture

- Operator Dashboard - Overview
- Operator Dashboard - Policy Comparison
- Operator Dashboard - Heuristic Analysis
- Operator Dashboard - PM Planning / Work Orders
- Operator Dashboard - Scenario Replay, if stable
- PM Worker App - Today PM List
- PM Worker App - Truck Detail
- PM Worker App - PM Checklist
- PM Worker App - Limited Chatbot Mock

## 9. What to Say

- C5.1 compares dispatch and PM scheduling policies in a mine truck simulation.
- H0 is the baseline, and H1-H4 are heuristic policies.
- H3 is recommended under the current KPI weighting because it leads total operating cost, demand fulfillment, and unmet demand in this run.
- H1 and H4 are strong on queue time, PM cost, and total downtime.
- H2 is most stable by total cost standard deviation.
- The dashboard reads generated analysis JSON; it does not recompute the full analysis in React.
- PM worker app receives generated Work Order data and presents execution-focused PM tasks.

## 10. What Not to Claim

- Do not say H3 is the optimal policy.
- Do not say the result is a mathematical global optimum.
- Do not say the simulation fully reproduces a real mine.
- Do not say RL is already implemented or necessarily better.
- Do not include Drop Zone in the H0-H4 comparison.

## Required Command Block

```powershell
cd C:\working\Capstone

python scripts/run_c5_1_policy_sweep.py --config configs/c5_1.yaml --policies H0 H1 H2 H3 H4 --seeds 1 2 3

python scripts/analyze_c5_1_heuristics.py --summary outputs/c5_1/summary/policy_comparison.csv

python scripts/export_work_orders.py --policy H3 --seed 1

python scripts/export_ui_snapshots.py

cd ui/operator_dashboard
npm run dev

cd ../pm_worker_app
npm run dev
```
