# C5.5 Facility-Destination Test

C5.5 is not a correction of C5.4.
C5.5 is an experimental branch that tests whether the C5.4 reliability/PM-scheduling logic still works when the dispatch surface is changed from abstract routes to C5.1-style facility destinations.

## What Was Inherited From C5.4

- 25-truck fleet scale, 365-day default horizon, 1-hour step, and 30 held-out evaluation seeds.
- Component-level reliability for tire, engine, and brake.
- Gamma frailty, noisy observed health index, Weibull-like failure hazard, and component HI recovery.
- PM scheduling families: calendar, operating-hours, condition, risk-priority, cost-value, and flow-backpressure.
- Normalized CU objective: PM + CM + downtime + degradation + unmet demand.
- Operating regimes: heterogeneous_condition, high_stress, and high_demand_high_stress.
- Policy family roster: H0, H_TIME, H1, H2, H3, H4.

## What Changed In C5.5

- Route A/B/C dispatch was replaced by facility destination ranking.
- Empty trucks rank Shovel A, Shovel B, Shovel C, PM bay, or standby.
- Loaded trucks rank Crusher 1, Crusher 2, emergency PM, or safe stop.
- The simulator adds the minimal state machine:
  `available_empty -> loaded -> available_empty`, with PM/CM downtime states preserved.
- The PM bay is modeled as one maintenance facility with two simultaneous service slots.
- New output metrics include shovel choice distribution, crusher choice distribution, PM bay utilization, max simultaneous PM, reserve activation, standby decisions, and effective output.

## Why Replace Route A/B/C

C5.4's Route A/B/C surface is useful for reliability and dispatch comparisons, but it is abstract. C5.5 tests whether the same PM/reliability logic still behaves coherently when dispatch is expressed as operational destinations: shovels for empty trucks and crushers for loaded trucks. This keeps C5.4 intact while probing the C5.1-style facility decision framing.

The C5.5 facilities are proxy simulation facilities only. They are not actual Escondida facilities and should not be described as a mine digital twin.

## C5.1 vs C5.4 vs C5.5

| Item | C5.1 | C5.4 | C5.5 |
|---|---|---|---|
| Main purpose | C5 mine scheduling simulation and heuristic comparison | Joint PM scheduling + Route A/B/C dispatch on reliability surface | Experimental test of C5.4 PM/reliability on facility-destination dispatch |
| Dispatch surface | Facility/task concepts | Abstract Route A/B/C | Shovel and crusher destination choices |
| Reliability | Component PM/cost baseline | Tire/engine/brake HI, frailty, sensor noise, hazard | Inherits C5.4 reliability unchanged |
| Maintenance | PM actions | PM scheduling is part of policy decision | Inherits C5.4 PM families with 1 PM facility and 2 service slots |
| Fleet | 25-truck C5 scale | 25 trucks | 25 total, 20 operating, 5 standby/reserve |
| Policies | H0-H4 baseline/heuristics | H0, H_TIME, H1-H4 joint policies | Same roster, adapted to facility destination ranking |
| Objective | Normalized CU framing | Normalized TCO/CU | Normalized TCO/CU retained |
| Status | Project foundation | Current main reliability-series module | Experimental branch/module |

## Facility Layout

| Facility type | Facilities | C5.5 proxy characteristics |
|---|---|---|
| Loading | Shovel A, Shovel B, Shovel C | A is high-grade/far/rough, B is balanced, C is low-grade/near/smooth |
| Dumping/processing | Crusher 1, Crusher 2 | Crusher 1 is closer/lower capacity; Crusher 2 is farther/higher capacity |
| Maintenance | PM bay facility | 1 facility with 2 simultaneous service slots |
| Fleet | Trucks | 25 total, 20 operating, 5 standby/reserve |

## Policy Adaptation

| Policy | C5.4 concept | C5.5 adaptation |
|---|---|---|
| H0 | Calendar PM + blind route rotation | Calendar PM + blind round-robin shovels/crushers |
| H_TIME | Operating-hours PM + blind route rotation | Operating-hours PM + blind round-robin shovels/crushers |
| H1 | CBM PM + health routing | Protect weak components by avoiding high-stress facilities; may standby very weak trucks |
| H2 | Risk-priority PM + risk-aware routing | Score facility value minus component risk/stress cost |
| H3 | Cost-value PM + value routing | Prefer high-grade/high-output shovel choices and efficient crusher service |
| H4 | Flow/backpressure PM + capacity routing | Prefer facilities with more remaining capacity and preserve production flow |

## Smoke Test Result

Smoke experiment executed:

- Regime: heterogeneous_condition
- Seeds: 101, 102, 103
- Horizon: 30 days
- Policies: H0, H_TIME, H1, H2, H3, H4
- Output: `outputs/c5_5/summary/c5_5_policy_comparison.csv`

| Rank | Policy | Mean TCO | Fulfillment | Failures/run | PM visits/run | PM utilization |
|---:|---|---:|---:|---:|---:|---:|
| 1 | H3 | 2709.0 | 0.996 | 10.3 | 273.0 | 0.600 |
| 2 | H4 | 3383.0 | 0.982 | 59.0 | 148.3 | 0.467 |
| 3 | H_TIME | 4268.3 | 0.973 | 51.0 | 120.0 | 0.833 |
| 4 | H0 | 4493.8 | 0.973 | 49.7 | 132.0 | 0.907 |
| 5 | H1 | 6205.6 | 0.585 | 0.0 | 132.3 | 0.228 |
| 6 | H2 | 7774.7 | 0.418 | 0.0 | 60.7 | 0.097 |

Interpretation: the smoke run completed and all policies produced valid facility decisions. H3 was lowest-TCO in this short smoke run. H1/H2 avoided failures but were too conservative on production, producing high unmet-demand cost. This is an experimental result, not a reason to tune parameters until a fuller comparison is run.

## Full Experiment Result

Not run in this pass. The recommended full run is:

- Regimes: heterogeneous_condition, high_stress, high_demand_high_stress
- Seeds: 101-130
- Horizon: 365 days
- Command: `python scripts/run_c5_5_sweep.py --regimes heterogeneous_condition,high_stress,high_demand_high_stress`

## Known Limitations

- C5.5 uses proxy facility parameters and should not be claimed as an actual mine digital twin.
- The state machine is intentionally minimal and does not model detailed travel, loading, dumping, operators, or PM crews as separate agents.
- Crusher service time is represented through destination scoring and wear/cycle factors, not a detailed queueing network.
- Reserve trucks are included structurally, but reserve activation remains simple.
- H1/H2 are currently conservative under the facility surface; the smoke result shows a fulfillment trade-off that needs full-run review before any recommendation.

## Recommendation

C5.5 should remain experimental for now. It is useful because it proves the C5.4 PM/reliability stack can run on a C5.1-style facility destination surface without modifying C5.4. It should not replace C5.4 unless the full 365-day, 30-seed, 3-regime comparison shows stable value and the H1/H2 production-conservatism issue is understood without post-hoc tuning.
