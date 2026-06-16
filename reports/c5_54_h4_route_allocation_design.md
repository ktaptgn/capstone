# C5.54 H4 Route Allocation Improvement Design

## 1. Why C5.54 Is Needed

C5.53 showed that the current official H4 policy is robust among official H0-H4 policies, but not necessarily route-allocation optimal.

Key C5.53 findings:

1. Hard TCO v3 preserved the original hard-threshold congestion result.
2. Soft TCO v4 added near-capacity congestion pressure without redefining v3.
3. H4 remained the best official H0-H4 policy under both hard and soft congestion.
4. `BALANCED_RR_H4_PM` beat H4 in all regimes, but it is only an audit comparator.
5. This suggests current H4 route allocation is not globally optimal.
6. The next official variant should combine H4's reliability/flow logic with stronger route allocation and effective fulfillment control.

From the C5.53 soft-threshold run, H4 remained the best official policy, but the synthetic comparator ranked first overall:

| regime | best official soft policy | best overall soft policy | H4 soft TCO | Balanced RR soft TCO |
|---|---|---|---:|---:|
| heterogeneous_condition | H4 | BALANCED_RR_H4_PM | 5775.0 | 5570.9 |
| high_stress | H4 | BALANCED_RR_H4_PM | 7964.3 | 7767.4 |
| high_demand_high_stress | H4 | BALANCED_RR_H4_PM | 9069.2 | 8905.0 |

The gap is meaningful enough to justify C5.54 route-allocation design exploration.

## 2. Why H5 Is Premature

H5 should not be created yet because the result is not a new policy proof. `BALANCED_RR_H4_PM` is a deliberately simple synthetic comparator:

- It uses H4's PM family.
- It rotates route priority round-robin.
- It does not include a full risk guard.
- It does not explicitly optimize grade-aware fulfillment.
- It does not prove that round-robin dispatch is operationally safe.

The right next step is C5.54 candidate design and controlled experiments. H5 would be justified only after a C5.54 candidate beats H4 reliably without increasing failure, CM, downtime, or hard congestion spikes.

## 3. What BALANCED_RR_H4_PM Proved

`BALANCED_RR_H4_PM` proved:

- H4's PM/flow foundation is strong.
- Route allocation can likely be improved beyond current H4.
- Better route balance can improve effective fulfillment.
- A simple balancing rule can outperform H4 on soft TCO v4 in the current test set.

It did not prove:

- Round-robin is the final route allocation policy.
- The comparator is safe under wider congestion sensitivity.
- The comparator handles route risk well.
- The comparator should be promoted directly to H5.

The comparator should be treated as a design signal, not as a deployable policy.

## 4. Candidate Variant Definitions

### Candidate 1: H4_BALANCED_CAPACITY

Purpose: keep H4's flow-aware PM family while improving route distribution and effective output.

Route score:

```text
score =
  w_capacity * capacity_score
- w_queue    * queue_penalty
+ w_balance  * balance_bonus
+ w_grade    * grade_value
- w_risk     * route_risk
```

Definitions:

- `capacity_score`: remaining route/facility capacity, including route, shovel, and crusher headroom.
- `queue_penalty`: C5.53 soft congestion pressure.
- `balance_bonus`: positive term for under-used routes, or penalty reduction for routes below target share.
- `grade_value`: route grade index or projected effective output gain.
- `route_risk`: route stress and expected degradation/failure risk.

Expected strengths:

- More balanced than current H4.
- Less naive than round-robin because it preserves capacity, queue, grade, and risk terms.
- Likely to improve effective fulfillment relative to H4 while keeping congestion low.

Risks:

- Weight interactions can be hard to interpret.
- Too much `w_balance` may force weak routes.
- Too much `w_grade` may push high-grade/high-stress A routes and increase wear.

### Candidate 2: H4_EFFECTIVE_FULFILLMENT_GUARD

Purpose: prevent H4 from being overly conservative on grade-adjusted output.

Logic:

```text
if projected_effective_fulfillment < target_effective_fulfillment:
    increase priority of higher-grade routes
else:
    use normal H4 flow-aware ranking
```

Recommended target levels:

```text
target_effective_fulfillment = 0.98, 0.99, 1.00
```

Expected strengths:

- Directly targets the observed H4 gap versus Balanced RR.
- Easy to interpret because it only activates when effective fulfillment is projected to lag.
- Keeps H4's current behavior when output is already adequate.

Risks:

- Guard activation can cause abrupt route switching.
- Overly high target, especially 1.00, may increase high-grade route stress.
- Needs projected effective fulfillment logic that is stable during the day, not only after the day ends.

### Candidate 3: H4_BALANCED_RR_GUARD

Purpose: capture the high effective fulfillment of `BALANCED_RR_H4_PM` while preventing uncontrolled congestion or route risk.

Logic:

```text
Rotate routes in balanced order,
but skip a route if:
- route utilization exceeds soft threshold
- shovel utilization exceeds soft threshold
- crusher utilization exceeds soft threshold
- route risk exceeds risk guard
```

Recommended soft utilization thresholds:

```text
soft_utilization_threshold = 0.85, 0.90, 0.95
```

Expected strengths:

- Closest official translation of the audit comparator.
- Simple and testable.
- Likely to improve route HHI and effective fulfillment.

Risks:

- Round-robin order may ignore useful marginal value information.
- It may be less adaptive than score-based selection during stress regimes.
- It can still over-select low-value routes if guard thresholds dominate route value.

## 5. DOE Factor Plan

Full factorial is too large:

```text
w_capacity: 3 levels
w_balance: 3 levels
w_grade: 3 levels
w_risk: 3 levels
soft_utilization_threshold: 3 levels
target_effective_fulfillment: 3 levels
```

A full grid would create 729 combinations before policies, regimes, and seeds. That is not appropriate for the first C5.54 pass.

Recommended staged design:

### Stage 1: 30-Day Smoke

Scope:

```text
days = 30
seeds = 101,102,103
regime = heterogeneous_condition
```

Policy set:

```text
H4
BALANCED_RR_H4_PM
H4_BALANCED_CAPACITY
H4_EFFECTIVE_FULFILLMENT_GUARD
H4_BALANCED_RR_GUARD
```

Reduced factor set:

| variant | factor settings |
|---|---|
| H4_BALANCED_CAPACITY | 6-9 fractional combinations around `w_capacity=1.0`, `w_balance=1.0`, `w_grade=1.0`, `w_risk=1.0` |
| H4_EFFECTIVE_FULFILLMENT_GUARD | target effective fulfillment `0.98`, `0.99`, `1.00` |
| H4_BALANCED_RR_GUARD | soft utilization threshold `0.85`, `0.90`, `0.95` |

Stage 1 success gate:

- No hard congestion spikes.
- Effective fulfillment improves versus H4 or stays close to Balanced RR.
- Failure/CM/downtime do not worsen materially.
- At least one candidate closes a meaningful share of the H4-to-Balanced RR soft TCO gap.

### Stage 2: 90-Day Base

Scope:

```text
days = 90
seeds = 101..110
regimes = heterogeneous_condition, high_stress, high_demand_high_stress
```

Policy set:

```text
Official baselines:
- H0
- H_TIME
- H1
- H2
- H3
- H4

Audit comparator:
- BALANCED_RR_H4_PM

C5.54 candidates:
- H4_BALANCED_CAPACITY
- H4_EFFECTIVE_FULFILLMENT_GUARD
- H4_BALANCED_RR_GUARD
```

Only the best Stage 1 parameter settings should advance.

### Stage 3: Soft-Threshold Sensitivity

Scope:

- Re-run Stage 2 winners under alternate soft-threshold settings.
- Keep hard TCO v3 and soft TCO v4 both visible.
- Do not tune soft threshold to force any candidate to win.

Suggested sensitivity axes:

```text
soft_start = 0.80, 0.85, 0.90
alpha_soft = low, base, high
beta_soft = 1.5, 2.0, 2.5
```

## 6. Metrics and Success Criteria

Required metrics:

```text
total_tco_v2
total_tco_v3_hard
total_tco_v4_soft_congestion
effective_fulfillment_rate
effective_output
route_hhi
max_route_share
congestion_delay_hours_hard
congestion_delay_hours_soft
failure_count
cm_count
downtime_hours
pm_visits
avg_realized_cycle_time
```

A C5.54 candidate is promising only if it:

1. Beats or matches H4 under `total_tco_v4_soft_congestion`.
2. Does not increase failure, CM, or downtime excessively.
3. Keeps route HHI close to or below H4.
4. Achieves effective fulfillment closer to `BALANCED_RR_H4_PM`.
5. Avoids large hard-threshold congestion spikes.
6. Performs robustly across all three regimes.

Operational guardrails:

| metric | guardrail |
|---|---|
| total_tco_v4_soft_congestion | <= H4 baseline, or materially closer to Balanced RR without reliability damage |
| effective_fulfillment_rate | >= H4 and ideally >= 0.99 |
| route_hhi | <= H4 or not materially worse |
| hard congestion hours | not worse than H4 by more than a small tolerance |
| failure_count | not worse than H4 baseline |
| downtime_hours | not worse than H4 by more than 10% |
| CM count | not worse than H4 baseline |

## 7. Implementation Constraints

C5.54 must preserve prior modules:

- Do not modify C5.4.
- Do not modify C5.5.
- Do not modify C5.51.
- Do not modify C5.52.
- Do not modify C5.53 except by reading outputs or inheriting its interfaces.
- Do not create H5 yet.
- Do not claim `BALANCED_RR_H4_PM` is a final policy.
- Do not tune variants to force a win.
- Treat C5.54 as route-allocation design exploration.

Recommended implementation shape when requested later:

```text
configs/c5_54.yaml
mine_env/config_c5_54.py
mine_env/policies_c5_54/
mine_env/simulator_c5_54.py
scripts/run_c5_54_sweep.py
scripts/analyze_c5_54_results.py
tests/test_c5_54_config.py
tests/test_c5_54_policies.py
tests/test_c5_54_simulator.py
reports/c5_54_route_allocation_experiment.md
```

C5.54 should inherit C5.53 proxy cycle-time, hard/soft congestion metrics, grade-aware output metrics, and the existing route/facility structure.

## 8. Recommended First Implementation Target

Recommended first target: `H4_BALANCED_RR_GUARD`.

Reason:

- It is the closest official, guarded version of the synthetic comparator that exposed the opportunity.
- It has the fewest tunable weights.
- It directly tests whether Balanced RR's advantage survives capacity, soft congestion, and risk guards.
- It is easier to debug than the multi-weight `H4_BALANCED_CAPACITY` score.

Recommended first Stage 1 settings:

```text
soft_utilization_threshold = 0.90
risk_guard = H4 route risk baseline percentile or stress-cost ceiling
route order = rotating route list, with skip-on-guard behavior
PM family = H4 flow_backpressure
```

Second target: `H4_EFFECTIVE_FULFILLMENT_GUARD`.

Reason:

- If `H4_BALANCED_RR_GUARD` improves route balance but still misses grade-aware output, the effective fulfillment guard can be layered next.

Third target: `H4_BALANCED_CAPACITY`.

Reason:

- It is the most flexible but also the most tune-sensitive; it should follow after simpler candidate behavior is understood.

## 9. Recommended Next Command

When implementation is explicitly requested, start with a C5.54 scaffold and only the first candidate:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; pytest tests\test_c5_53_config.py tests\test_c5_53_policies.py tests\test_c5_53_congestion.py -q
```

Then implement `H4_BALANCED_RR_GUARD` as the first C5.54 candidate and run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; python scripts\run_c5_54_sweep.py --days 30 --seeds 101,102,103 --regimes heterogeneous_condition --policies H4,BALANCED_RR_H4_PM,H4_BALANCED_RR_GUARD --no-event-log
```

