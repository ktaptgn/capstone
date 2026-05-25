# 00_CURRENT_PROJECT_DIRECTION.md

> This is the current direction lock document for C5.1.  
> If older C5 docs, previous RL experiments, or dashboard/app plans conflict with this document, follow this document.

---

## 1. Current Project Definition

C5.1 is a mine truck transport simulation and heuristic comparison project.

The project handles the following operational question:

> In a virtual open-pit mine truck transport system, which truck should run, wait, or enter PM so that demand is satisfied while PM cost and operating loss are reduced?

---

## 2. Current C5.1 Scope

### In Scope

| Area | Decision |
|---|---|
| Simulation | Virtual mine truck transport simulation |
| Main decision | Truck operating schedule and PM timing |
| Objective | Minimize PM cost and operating loss while satisfying demand |
| Constraint | Given demand must be satisfied as much as possible |
| Algorithm | H0 baseline + H1-H4 heuristics |
| RL | Deferred comparison target |
| Visualization | Simulation visualization MVP |
| Cost | Normalized internal cost with report-level value conversion |
| Drop Zone | Deferred environment scenario, not a heuristic |

### Out of Scope

| Area | Status |
|---|---|
| Operator dashboard implementation | Deferred |
| PM Android app implementation | Deferred |
| Dashboard-app integration | Deferred |
| PPO/RL training | Deferred |
| Drop Zone implementation | Deferred |
| Full Escondida digital twin | Excluded |
| Post-crusher processing and recovery-rate modeling | Excluded |

---

## 3. C5.1 Development Priority

```text
1. Scope lock
2. Config/schema
3. Cost model
4. Maintenance action model
5. Policy interface
6. H0 baseline
7. H1-H4 heuristic policies
8. Policy sweep
9. KPI summary
10. Simulation visualization MVP
```

---

## 4. Current Heuristic Set

| Policy | Name | Purpose |
|---|---|---|
| H0 | Baseline | Existing/simple dispatch and PM due rule |
| H1 | Bottleneck Dispatch | Reduce queue and processing bottleneck |
| H2 | PM Risk Priority | Prioritize PM using HI, tire HI, PM due, and operating pressure |
| H3 | Cost Unit Value | Choose actions by expected value and cost |
| H4 | Flow / Backpressure | Adjust dispatch using whole-system flow pressure |

---

## 5. Drop Zone Decision

Drop Zone is not part of H1-H4.

Correct comparison structure:

```text
Heuristic comparison:
Same environment + different policies

Drop Zone analysis:
Different environment scenario + same policies
```

Therefore, Drop Zone remains deferred until explicitly requested.
