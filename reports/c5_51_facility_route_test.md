# C5.51 Facility Route Test

C5.51 is not a replacement for C5.4 or C5.5.
C5.51 is an ablation test that keeps the C5.5 facility layout but restores C5.4-style route ranking.
The purpose is to separate the effect of facility layout from the effect of action-space design.

## Objective

C5.51 inherits the C5.5 proxy facility layout but changes dispatch from direct facility-destination selection to route ranking. Each route is a Shovel x Crusher pair:

- R_A1: Shovel A -> Crusher 1
- R_A2: Shovel A -> Crusher 2
- R_B1: Shovel B -> Crusher 1
- R_B2: Shovel B -> Crusher 2
- R_C1: Shovel C -> Crusher 1
- R_C2: Shovel C -> Crusher 2

The research question is whether C5.4-style route ranking stabilizes the H1/H2 production-risk trade-off that became too conservative in the C5.5 direct-destination smoke test.

## What Was Inherited From C5.5

- 25 total trucks, 20 operating trucks, and 5 standby/reserve trucks.
- Three shovels: Shovel A, Shovel B, and Shovel C.
- Two crushers: Crusher 1 and Crusher 2.
- One PM bay facility with two simultaneous service slots.
- C5.4/C5.5 reliability and cost model: tire, engine, brake HI; frailty; sensor noise; Weibull-like hazard; PM/CM/downtime logic; normalized CU/TCO objective.
- Policy roster: H0, H_TIME, H1, H2, H3, H4.
- Evaluation seed set and operating regimes.

## What Changed From C5.5

| Item | C5.5 | C5.51 |
|---|---|---|
| Dispatch action | Direct facility destination actions | Ranked route IDs |
| Empty truck decision | SEND_TO_SHOVEL_A/B/C, PM, standby | R_A1/R_A2/R_B1/R_B2/R_C1/R_C2 |
| Loaded truck decision | SEND_TO_CRUSHER_1/2, emergency PM, safe stop | Not exposed to policy; route execution handles shovel and crusher together |
| PM scheduling | Separate PM rule before dispatch | Same |
| Facility layout | 3 shovels, 2 crushers, PM bay capacity 2 | Same |
| Main diagnostic | Did facility actions make H1/H2 too conservative? | Does route ranking restore dispatch stability? |

## C5.4 vs C5.5 vs C5.51

| Version | Layout | Dispatch surface | Purpose |
|---|---|---|---|
| C5.4 | 25-truck C5 scale, abstract Route A/B/C surface, 2 shovel / 1 crusher config metadata | Route-level dispatch | Main reliability-series joint PM + dispatch comparison |
| C5.5 | 3 shovels, 2 crushers, PM bay capacity 2 | Direct facility destination dispatch | Test C5.1-style destination choices on the C5.4 PM/reliability stack |
| C5.51 | 3 shovels, 2 crushers, PM bay capacity 2 | Route-level dispatch using Shovel x Crusher pairs | Separate facility-layout effects from action-space effects |

## Route Definitions

The route table is defined in `configs/c5_51.yaml`. Values are C5.51 experimental assumptions and are not actual Escondida route values.

| Route | Path | Grade | Hardness | Cycle | Capacity | Interpretation |
|---|---|---:|---:|---:|---:|---|
| R_A1 | Shovel A -> Crusher 1 | 0.90 | 1.20 | 1.35 | 58 | High-grade, close-crusher but queue-prone |
| R_A2 | Shovel A -> Crusher 2 | 0.90 | 1.20 | 1.55 | 68 | High-grade, stable processing but longer travel |
| R_B1 | Shovel B -> Crusher 1 | 0.80 | 1.00 | 1.15 | 62 | Balanced, shorter but queue-prone |
| R_B2 | Shovel B -> Crusher 2 | 0.80 | 1.00 | 1.30 | 75 | Balanced, stable processing |
| R_C1 | Shovel C -> Crusher 1 | 0.70 | 0.85 | 0.95 | 66 | Low-grade, fast, queue-prone |
| R_C2 | Shovel C -> Crusher 2 | 0.70 | 0.85 | 1.10 | 82 | Low-grade, longer but stable |

## Policy Adaptation

| Policy | C5.51 route scoring |
|---|---|
| H0 | Calendar PM plus state-blind round-robin route ranking |
| H_TIME | Operating-hours PM plus state-blind round-robin route ranking |
| H1 | CBM PM plus health-aware route ranking that penalizes routes stressing weak components |
| H2 | Risk-priority PM plus `grade / cycle_time - risk-weighted stress` |
| H3 | Cost-value PM plus condition-blind `grade / cycle_time` |
| H4 | Flow-backpressure PM plus remaining route capacity / queue-pressure ranking |

## Smoke Test Result

Smoke experiment executed:

- Command: `python scripts\run_c5_51_sweep.py --days 30 --seeds 101,102,103 --regimes heterogeneous_condition`
- Regime: heterogeneous_condition
- Seeds: 101, 102, 103
- Horizon: 30 days
- Output: `outputs/c5_51/summary/c5_51_policy_comparison.csv`

| Rank | Policy | Mean TCO | Fulfillment | Failures/run | CM/run | PM visits/run | Downtime hours/run |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | H2 | 736.6 | 1.000 | 0.0 | 0.0 | 105.3 | 340 |
| 2 | H1 | 758.0 | 1.000 | 0.0 | 0.0 | 107.3 | 352 |
| 3 | H3 | 1424.9 | 1.000 | 0.0 | 0.0 | 200.3 | 681 |
| 4 | H4 | 1519.5 | 1.000 | 0.0 | 0.0 | 211.3 | 726 |
| 5 | H_TIME | 2903.9 | 1.000 | 5.7 | 5.7 | 126.0 | 1435 |
| 6 | H0 | 3152.4 | 1.000 | 11.0 | 11.0 | 132.0 | 1552 |

## C5.5 Comparison

Comparable C5.5 smoke result used the same regime, seeds, policies, and 30-day horizon.

| Policy | C5.5 fulfillment | C5.51 fulfillment | Change | C5.5 mean TCO | C5.51 mean TCO |
|---|---:|---:|---:|---:|---:|
| H1 | 0.585 | 1.000 | +0.415 | 6205.6 | 758.0 |
| H2 | 0.418 | 1.000 | +0.582 | 7774.7 | 736.6 |

Route-level dispatch improved the H1/H2 smoke behavior. In C5.5, H1/H2 avoided failures but under-dispatched severely, causing high unmet-demand cost. In C5.51, H1/H2 still avoided failures and achieved full fulfillment in the smoke run. This supports the ablation hypothesis that the direct facility-destination action space, not the facility layout alone, contributed to the C5.5 H1/H2 under-dispatch behavior.

## Route and Facility Behavior

- H2 concentrated on lower-risk C/B routes: R_B1, R_C1, and R_C2 made up nearly all selected loads.
- H1 also concentrated on R_C1/R_C2 with some R_B1/R_B2.
- H3 favored the highest `grade / cycle_time` routes and used R_A1, R_B1, R_C1, and R_C2.
- H4 distributed load more evenly across all six routes because its scoring emphasizes capacity and queue pressure.

## Known Limitations

- C5.51 route parameters are documented experimental assumptions, not real mine data.
- Route execution is intentionally simple: the simulator applies a full route as one dispatch/haul rather than modeling detailed shovel and crusher queues.
- PM crews are not modeled as separate decision variables; PM capacity remains integrated as the two-slot PM bay constraint.
- The smoke result is short-horizon evidence only. Full 365-day, 30-seed, 3-regime results are still needed before replacing or promoting any module.
- Lower C5.51 TCO relative to C5.5 should not be read as higher realism; it reflects action-space and simulator abstraction differences.

## Recommendation

C5.51 should remain an experimental ablation module. The smoke test suggests route-level dispatch stabilizes H1/H2 on the C5.5 facility layout, but the next step should be the full held-out comparison across all three regimes before changing the main C5.4/C5.5 narrative.
