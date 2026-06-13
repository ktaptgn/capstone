# 03_EVIDENCE_AND_SOURCE_REGISTER.md

## Purpose

This document separates evidence-based values, proxy assumptions, and deferred items for C5.1.

---

## Evidence-Based Inputs

| Item | Use |
|---|---|
| Public mine/company reports | Cost and production interpretation |
| Week 10 professor feedback | C5.1 problem framing |
| Week 11 mid-presentation comments | Presentation and scope direction |
| Week 12 team meeting | Heuristic comparison and dashboard/app separation |
| Team heuristic candidate documents | H1-H4 policy candidate pool |

---

## Proxy / Assumption-Based Inputs

| Item | C5.1 Treatment |
|---|---|
| Virtual mine scale | 0.1 scale proxy environment |
| Truck average payload | 350 tons as simplified operating payload |
| Cost model | Normalized cost unit for internal simulation |
| Production conversion | `ore_ton * grade` |
| PM action types | Scenario-based cost/time actions |
| Demand | Config-driven daily or period demand |

---

## Deferred Items

| Item | Reason |
|---|---|
| Drop Zone | Physical environment change; not comparable as heuristic |
| Operator dashboard implementation | Deferred until separate instruction |
| PM Android app implementation | Deferred until separate instruction |
| Dashboard-app integration | Deferred until separate instruction |
| PPO/RL training | Deferred after heuristic baseline is stable |
| Full Escondida digital twin | Out of scope |

---

## Reporting Rule

Internal calculations may use normalized units.  
Presentation/reporting may convert outputs into real-value proxy ranges, but must not claim actual mine accounting replication.
