# C5_1_SCOPE.md

## C5.1 Scope Lock

C5.1 is the core simulation and heuristic comparison version.

---

## In Scope

- C5.1 config
- cost model
- maintenance action model
- log schema
- common policy interface
- H0 baseline
- H1-H4 heuristics
- policy sweep
- KPI summary report
- simulation visualization MVP

---

## Out of Scope

- operator dashboard implementation
- PM Android app implementation
- dashboard-app integration
- PPO/RL training
- Drop Zone environment scenario implementation

---

## Core Fairness Rule

All policies must be compared under:

```text
same environment
same fleet
same demand
same seed
same KPI definitions
```

---

## Drop Zone Rule

Drop Zone is not a heuristic.  
It is a physical environment scenario and is deferred.
