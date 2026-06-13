# CURRENT_TASK.md

## Current Task

Implement C5.1 core simulation and heuristic comparison foundation.

## C5.1 One-Line Definition

C5.1 compares H0 baseline and H1-H4 heuristic policies under the same virtual mine simulation environment, then exports logs and KPI summaries for visualization.

## In Scope

- C5.1 docs/config/schema
- cost model
- maintenance model
- common policy interface
- H0 baseline
- H1-H4 heuristic policy modules
- policy sweep script
- KPI summary export
- simulation visualization MVP

## Out of Scope

- operator dashboard implementation
- PM Android app implementation
- dashboard-app integration
- PPO/RL training
- drop zone scenario implementation

## Acceptance Criteria

- H0-H4 run under the same config, same seed, and same demand scenario.
- `policy_comparison.csv` and `policy_comparison.json` are generated.
- `total_cost`, `pm_cost`, `unmet_demand`, and `demand_fulfillment_rate` are calculated.
- Drop Zone is disabled by default.
- No operator dashboard, PM app, or dashboard-app integration code is added.
- Simulation visualization MVP can replay generated logs.
