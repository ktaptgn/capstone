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

## 2026-05-25 / Heuristic Comparison Analysis

- Added a C5.1 heuristic analysis script for H0-H4 KPI aggregation, H0 baseline improvement, ranking, stability, and trade-off outputs.
- Added report-ready Markdown documents for heuristic comparison analysis, presentation summary, and dashboard analysis mapping.
- Added tests and a fixture to validate analysis output generation without modifying policy logic.
- Kept this task limited to analysis; no H0-H4 policy logic, dashboard behavior, PM app behavior, RL, or Drop Zone implementation was changed.

## 2026-05-26 / Dashboard Heuristic Analysis Visualization

- Added `dashboard_analysis.json` export from the C5.1 heuristic analysis pipeline for operator dashboard consumption.
- Updated UI snapshot export to copy the dashboard analysis JSON only into the operator dashboard public snapshot directory.
- Added a Korean `휴리스틱 분석` operator dashboard view for recommended policy, KPI winners, H0 improvement, seed stability, trade-off notes, missing KPI warnings, and analysis limitations.
- Added dashboard analysis contract tests and kept generated JSON snapshots, RL/PPO, and Drop Zone work out of the committed source.

## 2026-05-26 / C5.1 Presentation Package

- Added presentation runbook for C5.1 execution and UI demonstration.
- Added screenshot guide for operator dashboard and PM worker app.
- Added final result summary explaining H3 recommendation under current KPI weighting.
- Added slide copy blocks for capstone presentation.
- Clarified that H3 is not a global optimum and RL remains deferred to a separate repository.

## 2026-05-27 / 3D Operation Map MVP

- Added a C5 virtual mine 3D operation map data source for the operator dashboard draft.
- Implemented a React Three Fiber MVP with procedural terrain, cube facilities, hemisphere trucks, route tubes, queue areas, overlays, legend, and camera presets.
- Connected the existing Mine Operation Map card to a 2D/3D toggle while keeping the map as a result visualization layer.
- Kept external GLB models, external GIS/map services, RL, Drop Zone, and production dashboard workflows out of this implementation.

## 2026-05-29 / Dashboard ↔ PM App Real-Time PM Order Sync

- Added a backend-free shared sync bus (`pmSyncBus`) using BroadcastChannel + localStorage so PM work-order request/approve/hold/reject states stay in sync across browser tabs on the same origin.
- Wired the dashboard 긴급 PM 배차 modal to publish real work orders and added a live "실시간 PM 작업 지시" panel where the operator sees and acts on PM-worker decisions in real time.
- Replaced the PM worker app's local mock-order state with the shared bus (seeded once when empty) so worker decisions reflect back to the dashboard instantly.
- Added a zero-dependency `serve_demo.mjs` that serves both single-file builds from one origin (Dashboard `/`, PM app `/pm`), since BroadcastChannel/localStorage sync requires a shared origin.

## 2026-05-29 / All-Truck 2D + 3D HI Views

- Fixed the PM app fleet view so all 25 trucks render both the 2D and 3D HI models on selection (previously only the 3 trucks with explicit component-health data showed tire HI).
- Added `getComponentHealthForTruck` which returns explicit component health when present, otherwise a deterministic per-tire/per-component breakdown derived from the truck's overall healthIndex (stable per truck).
- Wired `FleetScreen` to the new helper so the existing 2D/3D toggle works for every truck.

## 2026-06-04 / Decision Visibility Overhaul (Dashboard + PM App)

Reframed the UI around operational decision-making per professor feedback (what decision / which heuristic / why / how the operator acts).

- **P0 Decision Recommendation panel** (operator dashboard Overview): recommended policy (H0–H4, H3 best), per-truck recommendations with Truck HI / Tire HI / min tire HI / risk score / expected PM duration / recommended action (Inspect·Repair·Replace·Cooldown·Hold) / reason, and Approve PM / Hold / Reject / Send Message actions.
- **P0 H0–H4 explanation table** (analysis page + modal): one-line definition, decision rule, expected benefit, weakness, representative KPI per heuristic.
- **P0 dashboard→PM lifecycle**: extended `pmSyncBus` with HI fields + worker lifecycle (Accept/Start/Complete/Delay/Reject). Operator Approve creates a field work-order card; worker actions reflect back to the dashboard live, real-time.
- **P0 map overlays**: each truck shows ID → destination (Shovel/Crusher/PM Bay/Standby/Cooldown), loaded/empty state (ore block vs default; PM-bound purple), health color + numeric HI, and a direction arrow — in both 2D and 3D.
- **P1 simulation controls**: Reset / Play-Pause / Step / Speed x1·x2·x4 in the header, driving the map animation for presentation recording.
- **P1 PM Decision Gate** on the PM Bay access road (2D + 3D), plus a Route Pressure & Warnings panel (traffic intensity, road wear index, collision/congestion + warning icons).
- **P2 scenario toggle** (Normal / High Demand / Road Risk / PM Bay Bottleneck / Tire Failure Event) updating KPI cards + map warnings, and a Cross-industry Transfer page (helicopter, wind turbine, nuclear, ship/offshore, forestry) framing the system as a proxy DES decision-support model — explicitly not a real Escondida digital twin.

## 2026-06-08 / Capstone Presentation Materials Pack

- Added `presentation_materials/` as a structured presentation production pack, not a PowerPoint deck.
- Copied current C5.1 source documents, configs, official policy summaries, analysis outputs, work-order samples, and replay logs into `presentation_materials/data/raw/`.
- Generated slide outline, speaker notes, source manifest, presentation-ready tables, generated CSV summaries, and chart images for KPI comparison, CU cost breakdown, PM timing, virtual mine flow, system architecture, and heuristic concept mapping.
- Used `outputs/c5_1/summary/policy_comparison.csv` as the official numeric comparison source and documented conflicts with smaller-scale secondary analysis tables.
- Preserved C5.1 framing as a proxy DES with CU-based marginal cost; no RL, Drop Zone, operator dashboard, PM app, or dashboard-app integration work was added.

---

## Current Official Version

| Item | Value |
|---|---|
| Version | C5.1 |
| Main scope | Simulation + heuristic comparison |
| Required policies | H0, H1, H2, H3, H4 |
| Required outputs | logs, KPI summary, visualization MVP |
| Deferred | RL, dashboard, PM app, integration, Drop Zone |
