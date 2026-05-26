# C5.1 Presentation Asset Index

| Artifact | Source Command | Purpose | Commit Status | Slide Use |
|---|---|---|---|---|
| `outputs/c5_1/summary/policy_comparison.csv` | `python scripts/run_c5_1_policy_sweep.py --config configs/c5_1.yaml --policies H0 H1 H2 H3 H4 --seeds 1 2 3` | Policy/seed KPI table | Generated local artifact | H0-H4 comparison |
| `outputs/c5_1/summary/policy_comparison.json` | Same policy sweep command | Dashboard snapshot source | Generated local artifact | Dashboard data flow |
| `outputs/c5_1/analysis/dashboard_analysis.json` | `python scripts/analyze_c5_1_heuristics.py --summary outputs/c5_1/summary/policy_comparison.csv` | Recommended policy, KPI winners, improvement, stability, warnings | Generated local artifact | Heuristic result |
| `ui/operator_dashboard/public/c5_1/dashboard_analysis.json` | `python scripts/export_ui_snapshots.py` | Operator dashboard analysis input | Generated local artifact | Dashboard demo |
| `outputs/c5_1/work_orders/work_orders_H3_seed1.json` | `python scripts/export_work_orders.py --policy H3 --seed 1` | PM Work Order data | Generated local artifact | PM worker app |
| Operator dashboard screenshot | Manual capture after `npm run dev` | UI proof for overview, policy comparison, heuristic analysis | Not committed unless separately requested | Dashboard result slides |
| PM worker app screenshot | Manual capture after `npm run dev` | UI proof for PM target list, truck detail, checklist, limited help mock | Not committed unless separately requested | PM execution slides |
| `docs/c5_1/C5_1_FINAL_RESULT_SUMMARY.md` | Manual doc from generated `dashboard_analysis.json` | Final result summary | Committed | Result explanation |
| `docs/c5_1/C5_1_SLIDE_COPY_BLOCKS.md` | Manual presentation copy | Korean slide text blocks | Committed | Slide drafting |
| `docs/c5_1/C5_1_SCREENSHOT_GUIDE.md` | Manual screenshot checklist | Capture guide and presenter notes | Committed | Demo preparation |
| `docs/c5_1/C5_1_PRESENTATION_RUNBOOK.md` | Manual runbook | Reproducible presentation setup | Committed | Presenter preparation |

## Notes

- Generated JSON files under `outputs/` and `ui/**/public/c5_1/` are not committed under the current repository policy.
- Screenshots are not committed unless explicitly requested.
- RL model files, Drop Zone data, and production backend artifacts are not part of the C5.1 presentation package.
