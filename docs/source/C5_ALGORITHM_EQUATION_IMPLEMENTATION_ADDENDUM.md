# C5_ALGORITHM_EQUATION_IMPLEMENTATION_ADDENDUM.md

## Purpose

This document defines the C5.1 heuristic implementation set.

For C5.1, H0-H4 are more important than PPO/RL.  
RL is deferred until the heuristic comparison foundation is stable.

---

## C5.1 Policy Set

| Policy | Name | Main Decision |
|---|---|---|
| H0 | Periodic PM Baseline | Perform pure calendar-periodic PM |
| H1 | Due / Health PM | Apply the former H0 PM due and HI rule |
| H2 | PM Risk Priority | Decide PM by HI, tire HI, PM due, and operating pressure |
| H3 | Cost Unit Value | Choose action by expected value and cost |
| H4 | Flow / Backpressure | Dispatch by whole-system flow pressure |

---

## H0. Baseline

```text
IF truck calendar PM slot is due:
    send truck to PM_VEHICLE
ELSE:
    use first-truck/basic dispatch rule
```

---

## H1. Due / Health PM

```text
IF pm_due <= threshold OR Truck HI <= threshold OR Tire HI <= threshold:
    send truck to matching PM
ELSE:
    use existing/basic dispatch rule
```

Decision:

```text
apply the first matching due/health decision
```

Purpose:

- react to PM due time and equipment condition
- preserve the former H0 rule as the first heuristic above the periodic baseline
- keep the rule simple and interpretable

---

## H2. PM Risk Priority

```text
PMPriority(truck)
= tire_risk
+ truck_hi_risk
+ pm_due_urgency
+ expected_failure_risk
- production_opportunity_loss
- pm_bay_queue_penalty
```

Decision:

```text
IF PMPriority >= threshold AND PM bay available:
    send truck to PM
ELSE:
    dispatch normally
```

Purpose:

- prevent delayed PM
- avoid unnecessary PM under high production pressure
- reflect PM bay capacity

---

## H3. Cost Unit Value

```text
OperationalValue(action)
= expected_production_value
- pm_cost
- downtime_cost
- unmet_demand_penalty
- degradation_cost
- queue_cost
```

Decision:

```text
select action with maximum OperationalValue(action)
```

Purpose:

- convert production, PM, downtime, and degradation into one comparable value
- connect the heuristic directly to the cost model
- make the policy easier to explain in presentation

---

## H4. Flow / Backpressure

```text
FlowScore(route)
= downstream_need
- upstream_congestion
- route_travel_penalty
- pm_risk_penalty
```

Decision:

```text
select route/destination with maximum FlowScore(route)
```

Purpose:

- avoid local-only dispatch decisions
- consider the whole mine flow
- improve system-level throughput and congestion balance

---

## Drop Zone Rule

Drop Zone is not H4.

Drop Zone changes the physical environment by adding a new stockpile/drop-off node.  
Therefore it is not comparable with H1-H4 under the same environment.

Correct structure:

```text
H1-H4: same environment, different policies
Drop Zone: different environment scenario, same policy set
```

Drop Zone is deferred until separately requested.
