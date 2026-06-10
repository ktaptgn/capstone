# C5_1_POLICY_SPEC.md

## Common Policy Interface

```python
class BasePolicy:
    policy_id: str

    def decide(self, state):
        return {
            "truck_id": "...",
            "action": "...",
            "destination": "...",
            "reason_code": "...",
            "score": 0.0
        }
```

---

## Common Action Space

```text
RUN_TO_SHOVEL
RUN_TO_CRUSHER
STANDBY
PM_TIRE
PM_VEHICLE
```

---

## Policies

| Policy | File | Description |
|---|---|---|
| H0 | `h0_baseline.py` | Pure calendar-periodic PM baseline using `periodic_pm_interval_days` |
| H1 | `h1_due_health.py` | Former H0: simple PM due / Truck HI / Tire HI rule |
| H2 | `h2_pm_risk_priority.py` | HI/RUL/PM due priority |
| H3 | `h3_cost_unit_value.py` | Cost-based operational value |
| H4 | `h4_flow_backpressure.py` | Whole-system flow/backpressure |

---

## Additional Comparison Baseline

| Policy | File | Description |
|---|---|---|
| H_TIME | `h_time_periodic_pm.py` | PM due-time reference policy that triggers `PM_VEHICLE` when `pm_due_hours <= pm_due_threshold_hours` |

`H_TIME` remains an additional PM due-time comparison policy. The former `H_PERIODIC` policy is now the official H0 baseline. The former bottleneck-dispatch H1 implementation is retained only as excluded legacy source and is not registered as a runnable C5.1 heuristic.

No H0-H4 policy contains a half-year or 180-day large-scale periodic PM rule. H0 uses only the config-driven `periodic_pm_interval_days` baseline interval.

---

## Non-Policy Scenario

Drop Zone is not a policy.  
Do not implement Drop Zone under H4.
