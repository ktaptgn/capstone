# AGENTS.md

## Project

C5.1 capstone implementation for mine truck scheduling simulation and heuristic comparison.

## Current Scope

Implement only:

- C5.1 simulation config
- cost model
- maintenance actions
- common policy interface
- H0 baseline
- H1-H4 heuristic policy modules
- policy sweep
- KPI summary export
- simulation visualization MVP

## Explicitly Out of Scope

Do not implement unless explicitly requested by the user:

- operator dashboard
- PM Android app
- dashboard-app integration
- PPO/RL training
- drop zone environment scenario

## Core Rules

- Keep generated filenames in English.
- Preserve source documents; do not overwrite without a clear changelog entry.
- Add or update `docs/source/04_PROJECT_CHANGELOG.md` for meaningful changes.
- Prefer config-driven values over hardcoded constants.
- H0-H4 must run under the same environment, same seed, same demand scenario, and same KPI set.
- Drop Zone is not a heuristic. Treat it only as a future environment scenario.
- RL is not the primary implementation target for C5.1.
- The simulation visualization MVP should replay policy logs; it should not contain full operator dashboard/app features.
