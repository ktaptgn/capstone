# C5_1_IMPLEMENTATION_PLAN.md

## Development Sequence

```text
0. Create C5.1 branch/folder
1. Add configs
2. Add cost model
3. Add maintenance model
4. Add log schema
5. Add policy interface
6. Add H0 baseline
7. Add H1-H4 heuristics
8. Add policy sweep script
9. Add KPI summary export
10. Add simulation visualization MVP
11. Add tests
```

---

## Phase 1: Configs

Create:

```text
configs/c5_1.yaml
configs/cost_model_c5_1.yaml
configs/maintenance_c5_1.yaml
```

---

## Phase 2: Core Modules

Create:

```text
mine_env/costs_c5_1.py
mine_env/maintenance_c5_1.py
mine_env/logger_c5_1.py
```

---

## Phase 3: Policies

Create:

```text
mine_env/policies/base_policy.py
mine_env/policies/h0_baseline.py
mine_env/policies/h1_bottleneck_dispatch.py
mine_env/policies/h2_pm_risk_priority.py
mine_env/policies/h3_cost_unit_value.py
mine_env/policies/h4_flow_backpressure.py
```

---

## Phase 4: Sweep and Reports

Create:

```text
scripts/run_c5_1_policy_sweep.py
scripts/export_c5_1_report.py
```

Expected outputs:

```text
outputs/c5_1/logs/
outputs/c5_1/summary/policy_comparison.csv
outputs/c5_1/summary/policy_comparison.json
outputs/c5_1/summary/c5_1_policy_report.md
```

---

## Phase 5: Visualization MVP

Create:

```text
ui/simulation_visualization/index.html
ui/simulation_visualization/app.js
```

The visualization should replay logs only.  
Do not implement operator dashboard or PM app here.
