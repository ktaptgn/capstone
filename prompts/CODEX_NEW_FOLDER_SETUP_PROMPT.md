# Codex Prompt: Create New C5.1 Project Folder and Implement Core Foundation

## Context

We are starting a new clean folder for C5.1.

Use the provided C5.1 source documents as the authoritative context.

C5.1 is not the full final dashboard/app product.  
C5.1 is the core simulation and heuristic comparison foundation.

## Hard Scope

Implement only:

1. C5.1 config loading
2. cost model
3. maintenance action model
4. simulation log schema usage
5. common policy interface
6. H0 baseline
7. H1-H4 heuristic policy skeletons and executable logic
8. policy sweep script
9. KPI summary export
10. simulation visualization MVP that replays logs

Do not implement:

- operator dashboard
- PM Android app
- dashboard-app integration
- PPO/RL training
- Drop Zone environment scenario

## New Folder Structure

Create this structure:

```text
Capstone_C5_1/
├─ README.md
├─ AGENTS.md
├─ CURRENT_TASK.md
├─ docs/
│  ├─ source/
│  └─ c5_1/
├─ configs/
├─ schemas/
├─ mine_env/
│  ├─ __init__.py
│  ├─ costs_c5_1.py
│  ├─ maintenance_c5_1.py
│  ├─ logger_c5_1.py
│  └─ policies/
│     ├─ __init__.py
│     ├─ base_policy.py
│     ├─ h0_baseline.py
│     ├─ h1_bottleneck_dispatch.py
│     ├─ h2_pm_risk_priority.py
│     ├─ h3_cost_unit_value.py
│     └─ h4_flow_backpressure.py
├─ scripts/
│  ├─ run_c5_1_policy_sweep.py
│  └─ export_c5_1_report.py
├─ tests/
│  ├─ test_c5_1_config.py
│  ├─ test_c5_1_cost_model.py
│  ├─ test_c5_1_policy_interface.py
│  ├─ test_c5_1_policy_sweep.py
│  └─ test_c5_1_log_schema.py
├─ ui/
│  └─ simulation_visualization/
│     ├─ index.html
│     └─ app.js
└─ outputs/
   └─ c5_1/
      ├─ logs/
      └─ summary/
```

## Required Implementation Rules

- H0-H4 must share the same `BasePolicy.decide(state)` interface.
- H0-H4 must run under the same config, same seed, same demand scenario, and same KPI set.
- Drop Zone must remain disabled by default.
- All numeric values must come from config when possible.
- Output must include:
  - `outputs/c5_1/summary/policy_comparison.csv`
  - `outputs/c5_1/summary/policy_comparison.json`
  - one log JSON per policy/seed
- Visualization must replay generated logs. It must not become a full dashboard.

## Acceptance Criteria

- `pytest` passes.
- `python scripts/run_c5_1_policy_sweep.py --config configs/c5_1.yaml --policies H0 H1 H2 H3 H4 --seeds 1 2 3` runs.
- Summary CSV/JSON is generated.
- Visualization can load at least one generated log file.
- No dashboard/app/integration/RL/dropzone implementation is added.

## First Step

Before implementing code, scan:

- `AGENTS.md`
- `CURRENT_TASK.md`
- `docs/source/00_CURRENT_PROJECT_DIRECTION.md`
- `docs/c5_1/C5_1_SCOPE.md`
- `docs/c5_1/C5_1_IMPLEMENTATION_PLAN.md`
- `docs/c5_1/C5_1_ACCEPTANCE_CRITERIA.md`

Then implement in small commits.
