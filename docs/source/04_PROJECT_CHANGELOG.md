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

## 2026-06-13 / C5.1 Reliability Levers + Cost Transparency (RL Lab port)

- Ported the RL Lab PPO diagnostic levers (C1 free self-healing, C3 health-has-no-consequence) into the C5.1 environment as a config-gated `reliability` section, so the heuristic comparison runs on an honest cost surface. Implemented on the `c5_1-reliability-levers` worktree branch.
- Added cost decomposition to the policy summary: `downtime_cost`, `degradation_cost`, `unmet_demand_cost`, `breakdown_cost`, `failure_count`, `pm_count`, and `total_downtime_hours` are now first-class columns. The previously hidden downtime cost (e.g. H0 ≈ 627 normalized-cu) and the unmet-demand penalty (H1/H4 ≈ 6,644) are now visible instead of being folded silently into `total_cost`.
- Resolved the long-standing `Missing required KPI columns: failure_count` warning: the simulator now emits `failure_count`, so the analyzer reports `none` missing.
- Added a breakdown / HI-consequence model (`mine_env/reliability_c5_1.py`): below the documented operating floor (truck_hi 0.45 / tire_hi 0.40) a RUN attempt can fail, costing a configurable `breakdown_cost_per_event` plus repair downtime, with only a partial health restore (not a free full-health PM). This gives preventive maintenance real protective value and closes the PPO never-PM exploit.
- Disabled free STANDBY self-healing while levers are on, closing the C1 free-PM path.
- Reproducibility: `reliability.enabled: false` reproduces the original C5.1 totals exactly (H0 1858.65, H1 / H4 7062.53, H2 3339.37, H3 1724.75).
- Honest finding (anti-overclaim): the C5.1 heuristics emergently maintain (minimum tire HI ~0.62 over a full year), so they never reach the breakdown floor and `failure_count` stays 0. The breakdown lever is therefore a dormant safeguard for the deferred RL comparison, not a heuristic-ranking changer. The only active lever effect on the heuristics is removing free STANDBY recovery (H3 −2.8%, H1 / H4 +0.6%, H0 unchanged); the H3 recommendation is preserved and reinforced.
- Calibrated `breakdown_cost_per_event` on a principled rule rather than by eye: a reactive repair's direct cost = 3× a planned PM_VEHICLE event (3 × 3.5 = 10.5 = 6.5 breakdown + 4.0 repair downtime), so `breakdown_cost_per_event = 6.5`.
- Added a threshold sensitivity sweep (tire floor 0.40 → 0.75, 3 seeds) documented in `C5_1_RELIABILITY_LEVERS.md`: the lever is dormant for any principled threshold (≤0.65) and only at 0.75 (above the documented floor) does it bite — penalizing under-maintainers H1/H4 (63–67 failures, +7% cost) while H3 stays at 0 failures and the ranking holds. This justifies keeping the floor at 0.40.
- RL/PPO training and Drop Zone remain out of C5.1 scope; only the diagnostic levers and the reporting were ported.

## 2026-06-13 / C5.2 Corrected Heuristic Set + Active Levers

- Imported the corrected heuristic set from `feature/c5_1-dashboard-pm-integration`: H0 is now a genuine **calendar-based periodic PM** (fixed 3-day interval, trucks staggered, always `PM_VEHICLE`), the former state-aware H0 logic moved to a new **H1 (`H1DueHealthPolicy`)**, an operating-hours baseline **`H_TIME`** was added, and the legacy bottleneck-dispatch H1 (which collided bit-for-bit with H4) was retired as `H1_LEGACY_EXCLUDED`.
- Verified **H1 ≠ H4** (1,858.65 vs 7,107.03), closing the previous bit-identical collision that made the "5-policy comparison" effectively a 4-policy one.
- Combined the corrected heuristics with the reliability levers: with health made consequential (C3 fix), the breakdown lever is **no longer dormant**. The two blind-periodic baselines break down — H0 (calendar) 91.7 failures / 595.8 breakdown-cost, H_TIME (operating-hours) 110.3 / 717.2 — while every state-aware policy (H1/H2/H3) stays at 0 failures.
- New cost ranking (3-seed mean, levers on): **H3 1,675.67 < H1 1,858.65 < H_TIME 1,948.67 < H2 3,312.74 < H0 5,748.85 < H4 7,107.03**. H3 still wins, but now on a defended basis: it beats the calendar baseline by avoiding breakdowns rather than by an unexplained margin.
- Honest limitation recorded: H0's failure magnitude is amplified by the modelling choice that calendar PM emits only `PM_VEHICLE` (no scheduled tire service), so tire HI drifts past the floor between slots. The qualitative result (blind periodic < state-aware) is robust; the exact H0 magnitude is a function of that single-action assumption.
- Updated tests: `test_state_aware_heuristics_avoid_breakdowns` (H1/H2/H3 → 0 failures) and `test_blind_periodic_pm_policies_incur_breakdowns` (H0/H_TIME → >0) replace the old dormancy assertion; config enabled list now includes `H_TIME`. Full suite: 28 passed (excl. npm/sweep-dependent UI artifact tests).

## 2026-06-13 / C5.3 — 3-Component Reliability, Dispatch-Only + Rule-Based PM

- New self-contained `c5_3` module (C5.1/C5.2 code untouched) that transplants the RL-Lab **C6 reliability model** into the **C5 25-truck mine + C6 routes A/B/C**: 3-component HI (tire/engine/brake, truck HI = min), per-truck **frailty** (Gamma wear heterogeneity), **C6 sensor noise** (POMDP), Weibull-like failure hazard, and a PM/CM model — re-implemented in `mine_env/reliability_c5_3.py`, `costs_c5_3.py`, `pm_rule_engine_c5_3.py`, `simulator_c5_3.py`, `config_c5_3.py`, `policies_c5_3/`.
- **Dispatch-only protocol (from C6.1)**: PM is fixed to one shared CBM rule engine (H*=0.21/0.21/0.28, the C6.1 frozen optimum) used byte-identically by every policy, so only dispatch differs. The C5.2 **H0–H4 are recast as route-selection strategies** (H0 route-blind, H1 health, H2 risk-aware, H3 value, H4 capacity); H_TIME is excluded (no dispatch analogue). Objective = TCO (pm+cm+downtime+degradation+unmet).
- **Key design finding**: in the C5.1 env every H0–H4 dispatches identically (round-robin crusher) — they differ only in PM trigger — so delegating PM to a fixed rule would collapse them. Adding the C6 route surface (A/B/C with per-component wear) is what makes the recast non-degenerate.
- **Result (30 seeds × 365 days × 3 regimes)**: condition-aware routing (H1/H2) beats every blind policy (H3/H4/H0) on TCO in all three regimes — heterogeneous_condition −6.4% (22,397 vs 23,933), high_stress −5.1% (32,580 vs 34,315), high_demand_high_stress −1.1% (48,239 vs 48,777); H1/H2 beat the H0 baseline on 24–25/30 seeds in mild and stress regimes (15–16/30 in extreme demand+stress where margins narrow).
- **Honest, regime-dependent mechanism**: in the mild regime failures are near-zero for all policies (the CBM rule prevents them) so the win is fewer PMs; under `high_stress` the failure/CM path activates and condition-aware routing wins by cutting corrective repairs ~6× (≈4 vs ≈26 CM/run). Under extreme demand+stress, grade-chasing (H3) and capacity (H4) fall **below** blind round-robin (H0) — throughput-first dispatch backfires once reliability binds. Under the extreme regime the H1/H2 win margin narrows to −1.1% (15–16/30 seeds), an honest finding preserved in the 30-seed result.
- Robustness regimes (`heterogeneous_condition`, `high_stress`, `high_demand_high_stress`) and all reliability/cost parameters are carried verbatim from the C6 configs (scaled ×2.5 for 10→25 trucks), not tuned. Spec: `06_C5_3_SPECIFICATION.md`; results: `06_C5_3_RESULTS.md`; sweep: `scripts/run_c5_3_dispatch_sweep.py`. Tests: `tests/test_c5_3_*.py` (29 passed).
- Presentation + UI: `scripts/plot_c5_3_results.py` renders the capstone result chart (`outputs/c5_3/analysis/c5_3_results.{png,svg}`); `scripts/build_version_results.py` emits `version_results.json` (C5.3 from the real sweep CSV, C5.2 from the frozen official table, C5.1 from documented totals) into both UIs. The operator dashboard (Header **결과 버전** selector → 정책 비교 page) and the PM worker app (top-bar selector → Today results card) now switch the displayed policy-comparison results between C5.1 / C5.2 / C5.3.

## 2026-06-14 / C5.4 — Joint PM-Scheduling + Dispatch (final-submission module)

- New self-contained `c5_4` module that widens the decision target from C5.3's dispatch-only to the **joint (PM scheduling + dispatch)** problem on the **same** C5.3/C6 reliability+cost surface. C5.3 had frozen PM to one shared CBM rule, so PM could never be *wrong*; C5.4 makes PM scheduling a **policy decision**, jointly with route choice.
- **Verbatim reuse (anti-overclaim).** `reliability_c5_4.py` / `costs_c5_4.py` are thin subclasses of the C5.3 models and `config_c5_4.py` reuses the C5.3 loader — a test (`test_reliability_cost_routes_are_verbatim_from_c5_3`) asserts the reliability/cost/routes/regimes/rule_based_pm subtrees are byte-identical to `c5_3.yaml`, so any C5.4 vs C5.3 difference is attributable to the decision change alone, never a quietly altered parameter.
- **Heuristics recast as PM-family × dispatch-family pairs.** Six selectable PM-scheduling families (`pm_scheduler_c5_4.py`: calendar / operating-hours / condition-CBM / risk-priority / cost-value / flow-backpressure) are each paired with the matching **C5.3 dispatch policy reused verbatim**: H0 calendar+route-blind, **H_TIME** operating-hours+route-blind (restored — it has a real PM analogue again once PM is a decision, unlike C5.3 where it was dropped), H1 CBM+health, H2 risk+risk-aware, H3 cost-value+value, H4 flow+capacity.
- **Realistic per-truck bay model (a refinement over C5.3).** A PM referral is now one *shop visit*: a truck occupies one bay and several components are serviced together (cost = Σ component PM costs, downtime = Σ durations). Blind baselines do a *full* vehicle service on a clock; state-aware rules service only the flagged components — sharpening the C5.2 "over-service the vehicle axis, under-protect the worn axis" contrast on the 3-component surface.
- **Defects repaired / carried forward.** Free self-heal (C1) and health-has-no-consequence (C3) stay closed via the inherited C5.3 surface; the production-reward/STANDBY idle-exploit stays closed via the TCO-only objective; making PM a decision does **not** reopen an exploit (PM cost + bay downtime price over-maintenance, CM prices under-maintenance — a genuine two-sided tradeoff). C5.3's frozen-PM limitation is lifted, and the long-standing **RL disconnect** is addressed by a documented joint-decision **interface** both heuristics and PPO target.
- **PPO integration = interface stub (no env in-repo; training stays in the RL Lab).** `rl_interface_c5_4.py` ships the `JointPolicy` protocol, the exact observation vector (`encode_observation`) and per-truck discrete action set (`decode_action`, `MultiDiscrete([6]*trucks)`), and an `AgentJointPolicy` adapter; `run_policy_simulation(..., policy=...)` accepts any `JointPolicy`, so a trained agent runs through the identical loop as the heuristics on the same seeds/regimes. Reward contract = −ΔTCO per step.
- **Submission-prep (Tier 1–3) executed.** `tests/test_c5_4_*.py` (**45 passed**, incl. sensor-noise/hazard/frailty boundary tests). Tier-1 logging added to `simulator_c5_4.py`: per-component PM **and** CM counts (`pm_*`/`cm_tire/engine/brake`), per-seed frailty (`avg_/max_frailty`), and an optional `failure_log`.
- **Headline result (`07_C5_4_RESULTS.md`, 30 seeds × 365 days × 3 regimes).** Ranking is identical in all regimes: **H1≈H2 < H3≈H4 < H_TIME < H0**. Joint state-aware PM+dispatch (H1 CBM+health, H2 risk) beats blind periodic PM (H0 calendar, H_TIME hours) by **40.4 % / 24.9 % / 17.0 %** TCO (heterogeneous / high_stress / high_demand) on **30/30 paired seeds** in every regime. H1/H2 are statistically ~tied (order flips within seed noise, as in C5.3); H3/H4 (cost-value/flow PM) are a clear second tier.
- **Mechanism (`09_C5_4_MECHANISM.md`).** Blind loses on two axes at once: it *over-services* (full-vehicle visits, end HI ~0.84) yet *under-protects the tail* (full-vehicle PM saturates the 2 bays at ~1,460–1,594 visits/yr, so fast-frailty trucks fail — CM 66→360/run as stress rises, ~66 % of it tire). State-aware does ~2× **more** but short, tire-targeted visits that fit the bays, runs lean (end HI ~0.32) and reaches ~0 failures. Per-seed failure count correlates **0.91** with a seed's worst frailty draw for blind policies (structural, not noise) — and that link **collapses** for condition-based H1 (it adapts).
- **Robustness (`08_C5_4_SENSITIVITY.md`).** Frailty-CV sweep: the state-aware advantage grows monotonically with heterogeneity (**+33 % at cv 0.10 → +50 % at cv 0.80**) and never disappears. CBM-threshold: TCO flat within ~0.5 % across ±20 % of the frozen 0.21/0.21/0.28 (a flat basin, not a knife-edge). Plus PM-bay-count and a blind-cadence robustness probe.
- **Anti-overclaim catch (logged).** The first config sized the blind cadence to the *average* truck (calendar interval 8 / hours due 72), making H0 fail ~586/run in the mild regime — a strawman. A diagnostic found the real mechanism (full-vehicle PM saturates the 2 bays regardless of interval); the cadence was **steelmanned** to the fast-frailty-tail / tightest-feasible value (interval 3 / due 30 — blind's best shot), and a cadence sweep confirms blind ≫ state-aware across interval 3→8, so the result is cadence-robust, not engineered. Spec: `07_C5_4_SPECIFICATION.md` §5.
- **Tier-4 presentation visuals.** `scripts/plot_c5_4_results.py` renders four figures (PNG+SVG) to `outputs/c5_4/analysis/` from the analysis artifacts: TCO box plots by regime, failures-vs-end-HI scatter (CBM-threshold validity), the frailty-CV advantage curve (+33 %→+50 %), and the failure-timing histogram.
- **UI wiring.** `scripts/build_version_results.py` now emits a **C5.4** block (read live from `outputs/c5_4/summary`, heterogeneous regime, mean/seed) and makes C5.4 the default version; the operator dashboard + PM-worker app pick it up generically via the shared `version_results.json` (no component changes). Deferred: PPO *training* (RL Lab).

---

## Current Official Version

| Item | Value |
|---|---|
| Version | C5.4 |
| Main scope | Joint (PM scheduling + dispatch) on the C5.3/C6 3-component reliability surface in the 25-truck mine; H0–H4 + H_TIME recast as PM-family × dispatch-family pairs |
| Required policies | H0 (calendar+blind), H_TIME (hours+blind), H1 (CBM+health), H2 (risk+risk-aware), H3 (cost-value+value), H4 (flow+capacity) |
| Required outputs | per-regime KPI tables (incl. PM visits/components), cost decomposition, paired-seed robustness across 3 regimes; documented PPO interface contract |
| Core findings | Joint state-aware PM+dispatch (H1/H2) beats blind periodic PM (H0/H_TIME) by 17–40 % TCO on 28–30/30 seeds in all 3 regimes; mechanism = blind over-services yet under-protects the bay-saturated tail (CM ~66 % tire); advantage grows with frailty CV (+33 %→+50 %); CBM threshold robust (±20 % → <0.5 % TCO) |
| Deferred | Tier-4 presentation plots; UI `version_results.json` C5.4 wiring; PPO *training* (RL Lab); Drop Zone |

(C5.3 remains the prior run-complete version: condition-aware routing > condition-blind on TCO in all 3 regimes, dispatch-only under fixed rule-based PM. C5.2: state-aware PM beats blind periodic PM, H3 recommended.)

## 2026-06-15 / RSW C5.4 Level 2 Synthetic Transfer Mini-Test

- Added the self-contained `transfer_tests/rsw_c5_4_level2` synthetic manufacturing transfer
  mini-test. The mining C5.4 experiment remains the main project; the RSW work is explicitly not a
  real factory validation or calibrated automotive-factory model.
- Reconstructed the C5.4 joint PM-scheduling + dispatch structure for 10 RSW welding guns with
  electrode-tip, cooling, and actuator/clamp HI; Gamma frailty; noisy observed HI; partial PM/CM
  restoration; synthetic defect/failure risk; three job families; and limited maintenance slots.
- Implemented the common `JointPolicy` contract and H0/H_TIME/H1/H2/H3/H4 as joint PM and
  production-assignment policies. Blind policies perform full gun service; H1-H4 can perform
  targeted component PM. No PPO/RL training, operator dashboard, PM app, or Drop Zone scenario was
  added.
- Executed the reduced default comparison at **10 seeds x 30 days x 3 regimes x 6 policies** under
  identical seeds, demand, environment, cost model, and KPI definitions. Generated policy summary,
  event log, failure log, mechanism, sensitivity, Excel, Markdown, and PNG artifacts.
- Honest result: the mini-test does not reproduce the mining C5.4 H1/H2-best ordering. H3 is
  lowest-TCO under heterogeneous condition and high stress; H4 is lowest under high demand + high
  stress. H0 is consistently worst because frequent full-service PM dominates cost and downtime.
- Sensitivity findings: the best policy changes with frailty CV; H1 CBM threshold perturbations
  produce modest TCO changes; additional maintenance slots do not change the ranking and increase
  blind full-service activity. Failures are sparse and occur only for H_TIME in the base sweep,
  mostly in the final campaign third.
- Added focused RSW regression tests covering six-policy execution, reproducibility, PM-slot
  capacity, TCO decomposition, blind full-service accounting, targeted PM, and required KPI
  summary fields.
- Added explicit runtime dependencies for NumPy, pandas, Matplotlib, and openpyxl, which are used by
  the RSW simulator and deliverable-generation scripts.

## 2026-06-15 / RSW Mini-Test Sanity Improvement Pack

- Preserved the original 30-day, 10-seed base outputs and added config-defined, separately stored
  optional sanity scenarios: a 30-day demand pressure stress run and a 90-day horizon run.
- Added `--demand-stress` and `--horizon-sanity-90` CLI modes. Sanity modes use fixed scenario
  contracts for policies, seeds, regimes, horizon, demand, and output paths so they cannot silently
  overwrite or inherit base outputs.
- Demand stress actual result: H3 had the lowest TCO; H_TIME alone produced mean unmet demand
  (`1.5` welds/run, fulfillment `0.999971`). Most policies still achieved fulfillment `1.000`, so
  the higher-demand run exposed only a limited PM-production trade-off.
- 90-day actual result: failure/CM mean totals increased from `1.2` in the base summary to `2.8`
  and remained concentrated in H_TIME. H4 was lowest-TCO under heterogeneous condition and high
  demand + high stress; H3 was lowest under high stress. H1-H4 retained component-targeted PM.
- Added `rsw_sanity_outputs.py`, scenario-specific Markdown reports and plots, and the integrated
  `rsw_c5_4_sanity_improvement_report.md`. Reports explicitly preserve the synthetic transfer-test,
  not-real-factory-validation, and no-post-hoc-tuning limitations.
- Added regression coverage for scenario contracts, CLI modes, base-output preservation, required
  sanity KPI columns, report disclaimers, and generated plots.

## 2026-06-15 / KAMP Welding Dataset Partial Defect-Risk Recheck

- Added a separate `kamp_validation` workflow for auditing the provided KAMP welding dataset and
  partially rechecking only the RSW mini-test's synthetic defect-risk proxy.
- Audited `Welding Data Set_01.xlsx`: 11,939 per-weld process rows, 23 result rows, and 10 data
  dictionary rows. The result sheet contains daily/defect-type aggregate counts, not reliable
  per-weld labels; per-weld supervised defect prediction was therefore explicitly excluded.
- Generated a daily quality summary for 9 raw-data dates. Eight dates have matched defect counts;
  the unmatched raw date was left unlabeled rather than assumed to have zero defects.
- The matched-day weighted defect rate is `0.00378972` (39 defects / 10,291 welds). The
  suggested-only calibration retains the existing `p_max=0.06`, center HI, and slope because the
  aggregate proxy does not justify a stronger defect hazard.
- Executed a separate 30-day x 10-seed x 3-regime KAMP-calibrated defect-hazard recheck. Because
  the recommended hazard equals the existing hazard, policy rankings, TCO, and defect results are
  unchanged from base. This is reported as evidence that ranking is dominated by the synthetic
  PM/downtime structure, not as a failure or as real factory validation.
- Added explicit limitations and tests confirming that KAMP data does not validate PM scheduling,
  tip dressing timing, maintenance slots, downtime, or electrode wear/HI.

## 2026-06-16 / C5.5 Facility-Destination Experimental Module

- Added C5.5 as an experimental module that inherits the C5.4 reliability, cost, frailty,
  sensor-noise, PM-scheduling, policy roster, regimes, seeds, and normalized-CU objective while
  replacing Route A/B/C dispatch with C5.1-style facility destination decisions.
- Added `configs/c5_5.yaml`, `mine_env/simulator_c5_5.py`, `mine_env/config_c5_5.py`, and
  `mine_env/policies_c5_5/` with H0, H_TIME, H1, H2, H3, and H4 adapted to shovel/crusher
  destination ranking.
- Modeled the required C5.5 layout: 25 trucks, 20 operating trucks, 5 standby/reserve trucks,
  Shovel A/B/C, Crusher 1/2, and one PM bay facility with two simultaneous service slots.
- Added `scripts/run_c5_5_sweep.py` and `scripts/analyze_c5_5_results.py`, plus C5.5 output
  folders under `outputs/c5_5/`.
- Added focused C5.5 tests for config loading, facility layout, state-valid destination decisions,
  PM service capacity, policy smoke execution, and TCO decomposition. C5.4 focused regression tests
  still pass.
- Ran a first C5.5 smoke experiment at heterogeneous_condition, seeds 101-103, 30 days, all six
  policies. H3 was lowest mean TCO in the smoke run; H1/H2 avoided failures but were too
  production-conservative, causing high unmet-demand cost. This result is documented as
  experimental and not tuned away.
- Added `reports/c5_5_facility_destination_test.md` with inheritance notes, C5.1/C5.4/C5.5
  comparison, facility layout, policy adaptation table, smoke result, limitations, and recommendation
  to keep C5.5 experimental until the full comparison is run.

## 2026-06-16 / C5.51 Facility-Route Ablation Module

- Added C5.51 as a separate experimental module that inherits the C5.5 facility layout but restores
  C5.4-style route ranking. C5.4 and C5.5 files and outputs were not overwritten.
- Added `configs/c5_51.yaml`, `mine_env/config_c5_51.py`, `mine_env/simulator_c5_51.py`, and
  `mine_env/policies_c5_51/`.
- Defined six facility-compatible routes as Shovel x Crusher pairs: R_A1, R_A2, R_B1, R_B2, R_C1,
  and R_C2. Route attributes include shovel/crusher mapping, grade, hardness, cycle factor,
  capacity, component wear multipliers, and queue sensitivity.
- Added route-level H0, H_TIME, H1, H2, H3, and H4 policies. Policies return ranked route lists,
  not direct facility actions.
- Added `scripts/run_c5_51_sweep.py`, `scripts/analyze_c5_51_results.py`, output folders under
  `outputs/c5_51/`, and focused C5.51 regression tests.
- Ran the comparable C5.51 smoke experiment at heterogeneous_condition, seeds 101-103, 30 days, all
  six policies. H2 and H1 ranked best by mean TCO, both with fulfillment 1.000 and zero failures.
- Compared against the C5.5 smoke: H1 fulfillment improved from 0.585 to 1.000, and H2 fulfillment
  improved from 0.418 to 1.000. This supports the ablation hypothesis that direct facility
  destination actions contributed to C5.5 H1/H2 under-dispatch in smoke testing.
- Added `reports/c5_51_facility_route_test.md` with C5.4/C5.5/C5.51 comparison, route definitions,
  smoke ranking, C5.5 comparison, limitations, and recommendation to keep C5.51 experimental until
  the full comparison is run.

## 2026-06-16 / C5.52 Grade-Aware Objective Experiment

- Added C5.52 as a separate experimental module that inherits the C5.51 facility and route layout
  while adding grade-adjusted production KPIs and a grade-aware TCO variant. C5.4, C5.5, and C5.51
  code paths were not modified.
- Added `configs/c5_52.yaml`, `mine_env/config_c5_52.py`, `mine_env/simulator_c5_52.py`,
  `mine_env/policies_c5_52/`, `scripts/run_c5_52_sweep.py`, and C5.52 output folders.
- Preserved load-based fulfillment and added `target_effective_output`,
  `effective_fulfillment_rate`, `avg_grade_per_load`, `total_tco_v1`, `total_tco_v2`, and
  `effective_output_shortfall_cost`.
- Added low/base/high shortfall-cost sensitivity. The base rate is derived from the existing unmet
  load penalty divided by a balanced-grade load (`2.0 / (350 x 0.80)`).
- Added H1/H2 original aliases and H1/H2 value-guard variants without overwriting existing H1/H2
  route policies.
- Ran the requested 90-day x 10-seed x 3-regime C5.52 experiment across low/base/high shortfall
  sensitivities and 10 policies, producing `outputs/c5_52/summary/c5_52_policy_comparison.csv`.
- Result: H1/H2 remain strongest under legacy TCO v1, but under base/high grade-aware TCO v2 the
  ranking shifts toward H4/H3 because H1/H2's low-grade route concentration creates effective-output
  shortfall cost.
- Added `reports/c5_52_grade_aware_objective_test.md` with fulfillment definitions, route shares,
  avg grade/load, effective output, v1/v2 ranking comparisons, sensitivity results, and the
  conclusion that reliability-cost optimum and production-value-aware optimum differ.

## 2026-06-16 / C5.52 Pareto Tradeoff Analysis and C5.53 Plan

- Added `reports/c5_52_pareto_tradeoff_analysis.md` to interpret C5.52 as a multi-objective
  reliability-cost versus grade-adjusted production-value trade-off.
- Exported Pareto plotting tables:
  `outputs/c5_52/analysis/c5_52_pareto_points.csv` and
  `outputs/c5_52/analysis/c5_52_policy_tradeoff_summary.csv`.
- Added formal Pareto flags for `v1_output` and `v2_failure_output`, plus route/facility share and
  ranking fields for downstream plotting or dashboard use.
- Added `reports/c5_53_value_risk_weight_sweep_plan.md` as a design-only DOE proposal for the next
  value-risk weight sweep. No C5.53 implementation or H5 policy was added.

## 2026-06-16 / C5.52 Route and Facility Congestion Audit

- Added `reports/c5_52_route_congestion_audit.md` to assess whether C5.52 route concentration,
  especially H1/H2 concentration on low-risk C routes, implies route/facility bottlenecks.
- Used existing C5.52 summary outputs only; no C5.4, C5.5, C5.51, or C5.52 simulator logic was
  modified.
- Finding: H1/H2 saturate R_C1/R_C2 route capacity and show high derived Shovel C utilization, but
  current logs do not include realized queue hours or cycle time, so actual queue/cycle bottlenecks
  cannot be confirmed without additional C5.53 logging.
- Finding: H4 clearly lowers route concentration and improves effective fulfillment, but current
  logs are insufficient to claim realized queue-hour or cycle-time savings.

## 2026-06-16 / C5.53 Congestion-Aware Bottleneck Experiment

- Added C5.53 as a separate congestion-aware experiment module without modifying C5.4, C5.5,
  C5.51, or C5.52 simulator logic.
- Added `configs/c5_53.yaml`, `mine_env/config_c5_53.py`, `mine_env/simulator_c5_53.py`, and
  `mine_env/policies_c5_53/` to inherit the C5.52 route/facility/grade-aware structure while
  adding deterministic route, shovel, and crusher congestion delay.
- Added dispatch-event and daily-summary instrumentation for preferred route, assigned route,
  fallback reason, route/facility utilization, queue delays, realized cycle time, route HHI, max
  route share, congestion cost, and `total_tco_v3`.
- Added `scripts/run_c5_53_sweep.py`, `scripts/analyze_c5_53_results.py`, C5.53 tests, and
  `reports/c5_53_congestion_bottleneck_test.md`.
- Ran the requested smoke test and the 90-day x 10-seed x 3-regime base congestion experiment
  (`alpha=1.0`, `beta=2.0`). Summary output is in
  `outputs/c5_53/summary/c5_53_policy_comparison.csv`, daily congestion logs are in
  `outputs/c5_53/logs/c5_53_daily_summary.csv`, and a smoke dispatch-event log remains in
  `outputs/c5_53/logs/c5_53_dispatch_events.csv`.
- Finding: under the base congestion setting, H1/H2 family policies retain reliability-cost
  characteristics but are heavily penalized by C-route concentration in `total_tco_v3`, while H4
  keeps lower route concentration and near-zero congestion delay across regimes.

## 2026-06-16 / C5.53 Literature-Informed Proxy Cycle-Time Calibration

- Added C5.53-only literature-informed proxy values for ultra-class truck motion, route distance,
  route speed factors, shovel loading time, and crusher service time in `configs/c5_53.yaml`.
- Updated `mine_env/simulator_c5_53.py` so realized cycle time uses route-specific proxy
  `base_cycle_time_min` plus route, shovel, and crusher queue delays instead of the earlier
  abstract one-hour base cycle multiplier.
- Added route cycle-time table export at
  `outputs/c5_53/analysis/c5_53_route_cycle_time_table.csv`.
- Updated `reports/c5_53_congestion_bottleneck_test.md` with a literature-informed proxy
  calibration section and clarified that the values are not actual Escondida measurements.
- Extended C5.53 tests to validate proxy config loading, cycle-time ordering, Crusher 2 service
  versus distance behavior, and use of proxy base cycle time in realized dispatch events.
- Re-ran the requested 30-day smoke test only after proxy calibration. H4 remained best under
  `total_tco_v3` for the heterogeneous-condition smoke run.

## 2026-06-16 / C5.53 H4 Zero-Congestion Audit

- Added `reports/c5_53_h4_zero_congestion_audit.md` to diagnose why H4 shows zero or near-zero
  congestion under the C5.53 base run.
- Audited existing 90-day C5.53 summary and daily logs without modifying C5.4, C5.5, C5.51,
  C5.52, or C5.53 simulator logic.
- Finding: H4 uses the same congestion calculation path as H1/H2/H3; no H4-specific bypass or
  logging omission was found.
- Finding: exact zero congestion in heterogeneous and high-stress regimes is caused by the current
  hard threshold (`utilization > 1.0`) and H4 preferred-attempt utilization staying at or below
  capacity. The high-demand/high-stress regime is near-zero but nonzero in the current audited
  output.
- Proposed a soft-threshold congestion design starting around utilization 0.85 as a future
  experiment, while preserving the current hard-threshold metric for comparability.

## 2026-06-16 / C5.53 Soft-Threshold Congestion Variant Analysis

- Added C5.53 soft-threshold congestion metrics while preserving existing hard-threshold
  `total_tco_v3` semantics.
- Added `soft_congestion` parameters to `configs/c5_53.yaml`, including `soft_start: 0.85`,
  low/base/high `alpha_soft`, `beta_soft`, hard-threshold parameters, and soft congestion cost.
- Added `congestion_delay_hours_hard`, `congestion_cost_hard`, `total_tco_v3_hard`,
  `congestion_delay_hours_soft`, `congestion_cost_soft`, and
  `total_tco_v4_soft_congestion` summary fields in `mine_env/simulator_c5_53.py`.
- Added `BALANCED_RR_H4_PM` as an audit-only synthetic comparator in `mine_env/policies_c5_53/`;
  it uses the H4 PM family with round-robin route ranking and is not an official policy.
- Added `scripts/analyze_c5_53_soft_threshold.py`, producing
  `outputs/c5_53/analysis/c5_53_soft_threshold_policy_comparison.csv`,
  `outputs/c5_53/analysis/c5_53_soft_threshold_tradeoff_summary.csv`, and
  `reports/c5_53_soft_threshold_congestion_analysis.md`.
- Ran the required 90-day x 10-seed x 3-regime experiment across official C5.53 policies plus
  `BALANCED_RR_H4_PM` with no full event log.
- Finding: H4 remains the best official H0-H4 policy under soft TCO v4 in all regimes, but
  `BALANCED_RR_H4_PM` beats H4 in all regimes, suggesting route allocation improvement potential
  for a future C5.54 design rather than immediate H5 creation.

## 2026-06-16 / C5.54 H4 Route Allocation Design Proposal

- Added `reports/c5_54_h4_route_allocation_design.md` as a design-only proposal for official
  C5.54 route allocation variants.
- Preserved C5.4, C5.5, C5.51, C5.52, and C5.53 logic; no C5.54 simulator or H5 implementation
  was created.
- Proposed three candidate variants: `H4_BALANCED_CAPACITY`,
  `H4_EFFECTIVE_FULFILLMENT_GUARD`, and `H4_BALANCED_RR_GUARD`.
- Recommended `H4_BALANCED_RR_GUARD` as the first implementation target because it is the closest
  guarded official translation of the audit-only `BALANCED_RR_H4_PM` comparator.
- Defined staged DOE execution: 30-day smoke, 90-day base across three regimes, then
  soft-threshold sensitivity for surviving candidates.

## 2026-06-16 / C5.54 Stage 1 H4 Balanced RR Guard Implementation

- Added C5.54 as a separate experimental module without modifying C5.4, C5.5, C5.51, C5.52, or
  C5.53 logic.
- Added `configs/c5_54.yaml`, `mine_env/config_c5_54.py`, `mine_env/simulator_c5_54.py`, and
  `mine_env/policies_c5_54/`.
- Implemented the first official C5.54 candidate, `H4_BALANCED_RR_GUARD`, using H4's
  flow-backpressure PM family plus balanced route order `R_A1, R_B1, R_C1, R_A2, R_B2, R_C2`,
  route/facility utilization guards, risk guard, and fallback to H4 route score.
- Preserved C5.53 hard and soft TCO semantics: `total_tco_v3_hard` remains the hard-threshold
  result and `total_tco_v4_soft_congestion` remains the soft-threshold result.
- Added guard/fallback summary metrics: `guard_skip_count`, `fallback_to_h4_count`,
  `route_guard_violation_count`, `shovel_guard_violation_count`,
  `crusher_guard_violation_count`, and `risk_guard_violation_count`.
- Added `scripts/run_c5_54_sweep.py`, `scripts/analyze_c5_54_results.py`, C5.54 tests, and
  `reports/c5_54_route_allocation_experiment.md`.
- Ran the requested Stage 1 smoke test: 30 days x seeds 101-103 x heterogeneous condition for
  `H4`, `BALANCED_RR_H4_PM`, and `H4_BALANCED_RR_GUARD`.
- Finding: `H4_BALANCED_RR_GUARD` beat both H4 and the audit comparator under soft TCO in the
  Stage 1 smoke run without hard-threshold congestion spikes or failure/CM increases. Stage 2
  90-day evaluation is justified, but guard skip and fallback counts should be monitored.

## 2026-06-16 / Operator 3D Map Facility OBJ Replacement

- Replaced the dashboard 3D map shovel, crusher, and PM Bay placeholder cube bodies with OBJ
  models named `shovel.obj`, `crusher.obj`, and `pm_bay.obj`.
- Kept facility colors driven by the existing dashboard status/risk color functions so replacement
  models retain the same color semantics as the previous facility bodies.
- Removed the `concentrator` facility, crusher-to-concentrator routes, and `concentrator_sink`
  asset entry from the 3D map dataset.
- Anchored shovel facility models to the shared terrain elevation sampler and lowered their model
  base slightly so the replacement OBJ appears attached to the terrain surface.

## 2026-06-16 / C5.54 Stage 2 90-Day Robustness Run

- Ran the requested C5.54 Stage 2 experiment: 90 days x 10 seeds x 3 regimes for `H4`,
  `BALANCED_RR_H4_PM`, and `H4_BALANCED_RR_GUARD`.
- Updated `outputs/c5_54/summary/c5_54_policy_comparison.csv`,
  `outputs/c5_54/logs/c5_54_daily_summary.csv`,
  `outputs/c5_54/analysis/c5_54_stage2_policy_summary.csv`,
  `outputs/c5_54/analysis/c5_54_stage2_guard_behavior_summary.csv`, and
  `reports/c5_54_route_allocation_experiment.md`.
- Finding: `H4_BALANCED_RR_GUARD` ranked first under soft TCO v4 in all three tested regimes,
  beating both official H4 and the audit-only `BALANCED_RR_H4_PM` comparator.
- Finding: effective fulfillment stayed near or above 0.99, hard congestion spikes were avoided,
  and failure/CM counts did not increase versus H4.
- Finding: guard activity is high but interpretable; risk and shovel guards dominate while route
  guard violations remain zero in this Stage 2 run.
- H5 was not created or named; threshold and risk-guard sensitivity validation remains the next
  required step before promoting any C5.54 candidate.

## 2026-06-16 / C5.54 Guard Threshold and Risk Sensitivity

- Added C5.54-only guard sensitivity controls for `H4_BALANCED_RR_GUARD`: risk levels
  `relaxed`, `base`, and `strict` mapped to H4 baseline risk percentiles `0.95`, `0.90`, and
  `0.75`.
- Added `scripts/run_c5_54_guard_sensitivity.py` to run isolated S1/S2 sensitivity experiments
  under `outputs/c5_54/sensitivity/` without overwriting Stage 2 base outputs.
- Ran S1 smoke: 30 days x seeds 101-103 x heterogeneous condition across all 9
  threshold/risk combinations.
- Ran S2 full sensitivity for four representative settings:
  `0.90/base`, `0.85/relaxed`, `0.85/strict`, and `0.85/base` across 90 days x 10 seeds x
  three regimes.
- Wrote `outputs/c5_54/analysis/c5_54_guard_sensitivity_summary.csv`,
  `outputs/c5_54/analysis/c5_54_guard_sensitivity_guard_behavior.csv`, and
  `reports/c5_54_guard_sensitivity_analysis.md`.
- Finding: `0.90/base` remains a conservative robust setting that beats H4 and the audit
  comparator in all S2 regimes with lower fallback dependence than `0.85/strict`.
- Finding: `0.85/strict` has the best S2 soft TCO among tested settings and beats both
  comparators in all regimes, but fallback dependence is materially higher and requires review.
- H5 was not created or named; sensitivity evidence is supportive but final confirmation should
  compare `0.85/strict` against `0.90/base`.

## 2026-06-16 / C5.54 H5 Candidate Freeze Decision

- Added `scripts/analyze_c5_54_h5_freeze_decision.py` to generate the final freeze decision
  from existing C5.54 sensitivity outputs without rerunning the full sweep.
- Wrote `outputs/c5_54/analysis/c5_54_h5_candidate_freeze_table.csv` and
  `reports/c5_54_h5_candidate_freeze_decision.md`.
- Compared the two remaining candidate settings: `0.90/base` and `0.85/strict`.
- Finding: `0.85/strict` has lower soft TCO in `high_demand_high_stress`, but is not lower TCO
  in the two lower-stress regimes and materially increases fallback dependence.
- Decision: recommend `H4_BALANCED_RR_GUARD` with `soft_utilization_threshold = 0.90` and
  `risk_guard_level = base` as the default H5 candidate setting.
- Keep `0.85/strict` as an aggressive sensitivity variant; H5 implementation was not created.

## 2026-06-16 / C5.55 Official H5 Benchmark

- Added C5.55 as a separate official H5 benchmark module without modifying C5.4, C5.5, C5.51,
  C5.52, C5.53, or C5.54.
- Added `configs/c5_55.yaml`, `mine_env/config_c5_55.py`, `mine_env/simulator_c5_55.py`,
  `mine_env/policies_c5_55/`, `scripts/run_c5_55_sweep.py`, and
  `scripts/analyze_c5_55_results.py`.
- Defined official `H5` as the C5.54 guarded H4 route-allocation policy frozen at
  `soft_utilization_threshold = 0.90` and `risk_guard_level = base`.
- Defined `H5_AGGRESSIVE` as a sensitivity comparator frozen at `0.85/strict`; it is not the
  default official policy.
- Ran the requested 90-day x 10-seed x 3-regime benchmark across `H0`, `H_TIME`, `H1`, `H2`,
  `H3`, `H4`, `H5`, `BALANCED_RR_H4_PM`, and `H5_AGGRESSIVE` with event logs disabled.
- Wrote `outputs/c5_55/summary/c5_55_policy_comparison.csv`,
  `outputs/c5_55/logs/c5_55_daily_summary.csv`,
  `outputs/c5_55/analysis/c5_55_policy_tradeoff_summary.csv`,
  `outputs/c5_55/analysis/c5_55_guard_behavior_summary.csv`, and
  `reports/c5_55_h5_policy_benchmark.md`.
- Finding: official H5 beats H4 and the audit-only `BALANCED_RR_H4_PM` comparator in all three
  regimes under soft TCO v4.
- Finding: `H5_AGGRESSIVE` beats H5 only in `high_demand_high_stress`, so it remains a
  stress-sensitive alternative rather than the default.
- Finding: H5 is robust enough for personal presentation as a follow-up benchmark, while C5.55
  does not replace the team C5.4 result.

## 2026-06-16 / C5.55 Personal Presentation Summary Package

- Added `scripts/analyze_c5_55_presentation_summary.py` to create presentation-focused summary
  tables from existing C5.55 benchmark outputs without rerunning experiments.
- Wrote `reports/c5_55_personal_presentation_summary.md`.
- Wrote `outputs/c5_55/analysis/c5_55_presentation_ranking_table.csv`,
  `outputs/c5_55/analysis/c5_55_h4_h5_h5aggressive_comparison.csv`, and
  `outputs/c5_55/analysis/c5_55_presentation_caveat_table.csv`.
- Summarized H5 as the default official presentation policy, `H5_AGGRESSIVE` as a
  stress-sensitive alternative, and `BALANCED_RR_H4_PM` as audit-only.
- Added presentation caveats that C5.55 is a personal follow-up benchmark, does not replace C5.4,
  uses proxy cycle-time/congestion assumptions, and must disclose H5 guard/fallback behavior.
