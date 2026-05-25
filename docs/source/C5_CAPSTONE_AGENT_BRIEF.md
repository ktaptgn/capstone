# C5_CAPSTONE_AGENT_BRIEF.md

## Current Target: C5.1

C5.1 is the current implementation target.

C5.1 is not a full product build.  
C5.1 is the core simulation and heuristic comparison version.

---

## One-Line Definition

C5.1 compares H0 baseline and H1-H4 heuristic policies under the same virtual mine simulation environment, then exports logs and KPI summaries for visualization.

---

## In Scope

- C5.1 simulation config
- cost model
- maintenance actions
- common policy interface
- H0 baseline
- H1-H4 heuristic policy modules
- policy sweep
- KPI summary export
- simulation visualization MVP

---

## Do Not Implement Unless Explicitly Requested

- operator dashboard
- PM Android app
- dashboard-app integration
- PPO/RL training
- Drop Zone environment scenario

---

## Required Development Order

```text
1. Update C5.1 docs and config
2. Implement cost model
3. Implement maintenance actions
4. Implement common policy interface
5. Implement H0 baseline
6. Implement H1-H4 heuristics
7. Implement policy sweep
8. Generate KPI summary
9. Implement simulation visualization MVP
10. Add tests
```

---

## Policy Comparison Rule

All H0-H4 policies must run under:

- same mine environment
- same truck fleet
- same demand scenario
- same seed
- same KPI definitions

Any policy that changes the physical environment is not comparable as a heuristic.

---

## Drop Zone Rule

Drop Zone is not H4.

Drop Zone is a physical environment scenario.  
It must not be implemented in C5.1 unless separately requested.

---

## Expected Output Files

```text
outputs/c5_1/logs/H0_seed1.json
outputs/c5_1/logs/H1_seed1.json
outputs/c5_1/summary/policy_comparison.csv
outputs/c5_1/summary/policy_comparison.json
outputs/c5_1/summary/c5_1_policy_report.md
```
