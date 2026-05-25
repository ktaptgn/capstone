# C5_PM_BAY_AND_TIME_RISK_DEFENSE.md

## Purpose

This document defines PM bay and maintenance timing logic for C5.1.

---

## PM Bay Definition

```text
PM bay capacity = maximum number of trucks that can receive PM at the same time
```

C5.1 treats PM bay as an integrated maintenance capacity:

```text
service bay + crew + tools + tire handler + safety procedure
```

PM workforce is not modeled separately.

---

## C5.1 PM Action Set

| Action | Meaning |
|---|---|
| NO_PM | Continue operation |
| PM_TIRE | Tire-focused PM |
| PM_VEHICLE_BALANCED | Balanced cost/time vehicle PM |
| PM_VEHICLE_FAST_EXPENSIVE | Short duration, high cost PM |
| PM_VEHICLE_SLOW_CHEAP | Long duration, low cost PM |

---

## PM Logic

PM is not a separate project objective.  
PM is a scheduling constraint and action.

When a truck enters PM:

- it becomes unavailable
- PM bay capacity decreases
- downtime cost occurs
- PM cost occurs
- future risk may decrease

---

## Time Risk

Time risk may affect degradation or operating cost, but it should not explode the state/action space.

For C5.1:

- time risk can be a multiplier
- PM workforce scheduling remains excluded
- PM bay capacity remains the main maintenance bottleneck
