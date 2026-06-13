# Capstone C5.1

## Purpose

This repository contains the C5.1 core simulation and heuristic comparison foundation for the mine truck scheduling capstone.

C5.1 is not a full dashboard/app implementation phase.  
C5.1 is the core simulation and heuristic comparison foundation.

## C5.1 Definition

C5.1 is the version that compares H0 baseline and H1-H4 heuristic policies under the same mine simulation environment, same demand scenario, and same seed control.

The output of C5.1 must be standardized logs, KPI summaries, and a simulation visualization MVP.

## Current In Scope

- C5.1 config loading
- normalized cost model
- maintenance action model
- simulation log schema usage
- common `BasePolicy.decide(state)` interface
- H0 baseline and H1-H4 heuristic policies
- policy sweep script
- KPI summary CSV/JSON export
- simulation visualization MVP that replays generated logs

## Deferred Until Separate Instruction

- Operator dashboard implementation
- PM Android app implementation
- Dashboard-app integration
- PPO/RL training
- Drop Zone scenario implementation

## Run

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the required C5.1 policy sweep:

```powershell
python scripts/run_c5_1_policy_sweep.py --config configs/c5_1.yaml --policies H0 H1 H2 H3 H4 --seeds 1 2 3
```

Export the markdown report:

```powershell
python scripts/export_c5_1_report.py --config configs/c5_1.yaml
```

Run tests:

```powershell
pytest
```

Open `ui/simulation_visualization/index.html` in a browser and load one generated log JSON from `outputs/c5_1/logs/` to replay the simulation.

Generated logs and summaries are intentionally ignored by Git except for placeholder files that preserve the output directory structure.
