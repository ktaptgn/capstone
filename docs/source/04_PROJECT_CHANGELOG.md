# 04_PROJECT_CHANGELOG.md

## Purpose

This changelog tracks the official direction changes for C5.1.

---

## 2026-05-18 / Week 10 Feedback

- Professor feedback reframed the project as a mine truck transport simulation and PM scheduling problem.
- Priority changed from RL-first to simulation visualization + heuristic baseline.
- RL was moved to a later comparison target.
- Project explanation must use the team's own operational language, not GPT-generated abstraction.

---

## 2026-05-19 / Week 11 Mid-Presentation

- Project direction was positioned as industrial engineering scheduling + preventive maintenance.
- Working simulation, heuristic comparison, and interpretable outputs were confirmed as important.
- The presentation should reveal problem definition and direction, not detailed formulas or code.

---

## 2026-05-25 / Week 12 Meeting

- C5.1 scope fixed as a heuristic comparison foundation.
- H0 baseline and H1-H4 policies will be compared under the same environment.
- Drop Zone is not treated as a heuristic. It is deferred as a separate environment scenario.
- Operator dashboard, PM app, and integration are deferred until separate instruction.
- C5.1 must export logs and KPI summaries for later visualization/dashboard/app use.

## 2026-05-25 / GitHub Commit Preparation

- Initialized the local project for Git tracking on the `main` branch.
- Added repository hygiene files for line-ending normalization and generated-output exclusion.
- Preserved C5.1 output directories with placeholder files while keeping generated logs and summaries out of Git.

## 2026-05-25 / C5.1 Core Foundation Implementation

- Added config loading for the C5.1 main, cost, and maintenance YAML files.
- Implemented the normalized cost model, maintenance action model, log utilities, and simulation runner.
- Added the shared `BasePolicy.decide(state)` interface and executable H0-H4 heuristic policies.
- Added policy sweep and report export scripts that generate policy/seed logs and KPI summaries.
- Added the simulation visualization MVP as a log replay tool only, without dashboard, PM app, integration, RL, or Drop Zone features.
- Added tests for config loading, cost model behavior, policy interface consistency, policy sweep output, and log schema validation.

## 2026-05-25 / Existing UI Draft Import

- Imported the existing operator dashboard and PM worker app drafts into `ui/operator_dashboard` and `ui/pm_worker_app`.
- Added file-based work order export and UI snapshot export scripts.
- Added `public/c5_1` snapshot folders for each UI app, with generated JSON snapshots excluded from Git.
- Updated the imported UI data loading path to prefer official C5.1 snapshots and fall back to existing mock data.
- Kept RL training and Drop Zone implementation out of the official repository.

---

## Current Official Version

| Item | Value |
|---|---|
| Version | C5.1 |
| Main scope | Simulation + heuristic comparison |
| Required policies | H0, H1, H2, H3, H4 |
| Required outputs | logs, KPI summary, visualization MVP |
| Deferred | RL, dashboard, PM app, integration, Drop Zone |
