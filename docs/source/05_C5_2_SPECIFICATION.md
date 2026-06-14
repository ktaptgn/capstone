# C5.2 Official Specification

## Version and Date
- **Version**: C5.2
- **Effective Date**: 2026-06-13
- **Status**: Official (Frozen for Capstone Submission)
- **Supersedes**: the interim C5.2 draft that ran on the legacy heuristic set (H1≡H4 collision, H0 as a state-aware baseline). This version runs on the **corrected heuristic set** imported from `feature/c5_1-dashboard-pm-integration`.

---

## 1. Purpose

C5.2 is the official capstone specification combining two corrections:

1. **Corrected heuristic set** — H0 is now a genuine **calendar-based periodic PM** baseline, the legacy bottleneck-dispatch H1 (which collided bit-for-bit with H4) is retired, and a new state-aware H1 plus an operating-hours baseline `H_TIME` make every policy genuinely distinct.
2. **Reliability levers (PPO defect port)** — the C1 (free self-heal) and C3 (health-has-no-consequence) defects found in the RL Lab PPO runs are closed, so health now has a cost consequence.

The combination produces the headline C5.2 result: **with health made consequential, blind periodic PM (calendar / operating-hours) is measurably penalised by breakdowns, while state-aware PM (HI/risk/cost driven) is rewarded.**

---

## 2. Heuristic Set (corrected)

| ID | Class | PM trigger | Distinct? |
|----|-------|-----------|-----------|
| **H0** | `H0BaselinePolicy` | **Calendar**: fixed `periodic_pm_interval_days = 3`, trucks staggered, always `PM_VEHICLE`. Ignores per-truck HI. | ✅ |
| **H_TIME** | `HTimeDuePmPolicy` | **Operating hours**: PM when `pm_due_hours ≤ 12`. Usage-based, ignores HI directly. | ✅ |
| **H1** | `H1DueHealthPolicy` | **Due + health**: PM when `pm_due ≤ 12` **or** `truck_hi ≤ 0.45` **or** `tire_hi ≤ 0.40` (the former H0 logic). | ✅ |
| **H2** | `H2PmRiskPriorityPolicy` | **Risk priority**: PM the highest-risk truck above a risk threshold. | ✅ |
| **H3** | `H3CostUnitValuePolicy` | **Cost unit value**: PM vs run by expected operational value. | ✅ |
| **H4** | `H4FlowBackpressurePolicy` | **Flow / backpressure**: dispatch by system flow pressure. | ✅ |

Retired: `LegacyBottleneckDispatchPolicy` (`policy_id = H1_LEGACY_EXCLUDED`) — kept on disk for traceability, **not registered**. It is the policy that previously collided with H4.

The three PM-trigger families (calendar / operating-hours / state-aware) are the comparison's backbone: they let the report show *why* a PM strategy wins or loses, not just *that* it does.

---

## 3. Core Requirements

### 3.1 Reliability Levers — Complete + Active
**Status**: ✅ Delivered
- Config-gated breakdown model; `reliability.enabled: false` reproduces the legacy-heuristic totals exactly.
- Below the operating floor (truck_hi 0.45 / tire_hi 0.40) a RUN can fail: lost haul (unmet) + `breakdown_cost_per_event = 6.5` + 8h repair downtime + partial restore (0.70, not a free full PM).
- Free STANDBY self-heal disabled while levers on (C1 path closed).
- **Now active** (unlike the legacy-heuristic C5.2): the calendar (H0) and operating-hours (H_TIME) baselines reach the floor and break down; state-aware policies do not.

### 3.2 Cost Decomposition & Transparency
**Status**: ✅ Delivered
- `pm_cost`, `downtime_cost`, `degradation_cost`, `unmet_demand_cost`, `breakdown_cost` decomposed; sum equals `total_cost` (test invariant).
- KPI columns `failure_count`, `pm_count`, `total_downtime_hours` first-class.

### 3.3 H3 Recommendation Reproducibility & Validation
**Status**: ✅ Delivered
- H3 is the lowest-cost policy across 3 seeds: **H3 < H1 < H_TIME < H2 < H0 < H4**.
- H3 now wins **with a defended mechanism**: it beats the calendar baseline (H0) by avoiding 92 breakdowns, and beats the operating-hours baseline (H_TIME) on cost despite H_TIME's higher throughput.

### 3.4 Heuristic Policy Fairness & Comparability
**Status**: ✅ Delivered
- All six policies share environment, demand, seeds, cost model, and breakdown model.
- H1 ≠ H4 is now verified (1,858.65 vs 7,107.03), closing the previous bit-identical collision.

---

## 4. C5.2 KPI Table (365 days × 3 seeds, levers ON)

### 4.1 Headline KPIs

| Policy (PM family) | total_cost ↓ | fulfill % | unmet | completed | **failures** | avail % |
|---|---:|---:|---:|---:|---:|---:|
| **H3** (cost-value) 🏆 | **1,675.67** | 97.6 | 160 | 6,431 | **0** | 92.0 |
| **H1** (due+health) | 1,858.65 | 94.7 | 348 | 6,243 | **0** | 82.1 |
| **H_TIME** (operating-hours) | 1,948.67 | 98.5 | 101 | 6,490 | 110.3 | 88.4 |
| **H2** (risk priority) | 3,312.74 | 81.7 | 1,206 | 5,385 | **0** | 88.9 |
| **H0** (calendar) | 5,748.85 | 83.2 | 1,108 | 5,483 | 91.7 | 60.7 |
| **H4** (flow/backpressure) | 7,107.03 | 49.8 | 3,306 | 3,285 | **0** | 96.2 |

### 4.2 Cost Decomposition

| Policy | pm | downtime | degrad | unmet | **breakdown** | failures | pm_count |
|---|---:|---:|---:|---:|---:|---:|---:|
| H3 | 613.3 | 724.3 | 18.0 | 320.0 | **0.0** | 0 | 502 |
| H1 | 520.8 | 625.0 | 17.5 | 695.3 | **0.0** | 0 | 417 |
| H_TIME | 244.0 | 766.7 | 18.2 | 202.7 | **717.2** | 110.3 | 163 |
| H2 | 402.7 | 483.0 | 15.1 | 2,412.0 | **0.0** | 0 | 322 |
| H0 | 1,095.0 | 1,826.7 | 15.4 | 2,216.0 | **595.8** | 91.7 | 730 |
| H4 | 220.8 | 265.0 | 9.2 | 6,612.0 | **0.0** | 0 | 177 |

---

## 5. Headline Findings (anti-overclaim)

1. **Health now has a consequence (C3 fix is real).** Only the two blind-periodic baselines break down: H0 (calendar, 91.7 failures) and H_TIME (operating-hours, 110.3). Every state-aware policy (H1/H2/H3) stays at 0 failures. The lever discriminates exactly on the axis it was built to test.

2. **Calendar PM (H0) is the worst non-degenerate policy.** It PMs the most (730 events, pm_cost 1,095) yet still fails 91.7 times and only fulfils 83.2% of demand. Reason: H0 fires `PM_VEHICLE` on a fixed 3-day clock and **never restores tires**, so tire HI drifts below the 0.40 floor between slots → breakdowns. Calendar PM over-services on the vehicle axis and under-services on the tire axis simultaneously — the textbook weakness of state-blind scheduling.

3. **Operating-hours PM (H_TIME) is cheap and high-throughput but fragile.** Highest fulfilment (98.5%), fewest PMs (163), but 110 breakdowns because `pm_due_hours` tracks usage, not component HI. It lands 3rd on cost — breakdowns eat its throughput advantage.

4. **State-aware PM wins on a defended basis.** H3 (cost-value) is 1st; the former-H0 due+health policy (now H1) is 2nd. Both read per-truck HI and never reach the floor. **The C5.2 message is no longer "the lever is dormant" — it is "the lever proves state-aware PM beats blind periodic PM."**

5. **H4 remains a throughput failure, not a maintenance one.** Its 7,107 cost is 6,612 unmet-demand penalty (49.8% fulfilment); 0 failures because it barely runs equipment hard enough to degrade it.

6. **Honest limitation.** H0's breakdown count is inflated by the modelling choice that calendar PM emits only `PM_VEHICLE` (no scheduled tire service). A real calendar program that also rotates tires would fail less. The qualitative result (blind periodic < state-aware) is robust; the exact H0 failure magnitude is a function of this single-action assumption and should be presented as such.

---

## 6. Reproducibility & Deferred

- `reliability.enabled: false` reproduces the legacy totals to the decimal; the decomposition columns only split `total_cost`, never change it.
- Deferred (not C5.2): RL/PPO training, Drop Zone scenario, dashboard optimisation integration, PM-app production deployment.

---

## 7. Conformance Checklist

| Requirement | Evidence | Status |
|---|---|---|
| Corrected heuristics (H0 calendar, H1≠H4) | `POLICY_REGISTRY`, KPI table §4 | ✅ |
| H1 ≠ H4 | 1,858.65 vs 7,107.03 | ✅ |
| Reliability levers active | H0/H_TIME failures > 0, H1/H2/H3 = 0 | ✅ |
| Cost decomposition sums to total | `test_breakdown_plumbing_flows_into_costs_and_summary` | ✅ |
| State-aware avoids breakdowns | `test_state_aware_heuristics_avoid_breakdowns` | ✅ |
| Blind periodic incurs breakdowns | `test_blind_periodic_pm_policies_incur_breakdowns` | ✅ |
| Reproducibility (levers off) | `test_disabled_run_reproduces_original_four_component_cost` | ✅ |
| Full suite | 28 passed (excl. npm/sweep-dependent UI artifact tests) | ✅ |

---

**Status**: Ready for Capstone Submission.
