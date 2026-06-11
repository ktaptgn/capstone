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
| H0 | `h0_baseline.py` | Existing/simple dispatch + PM due rule |
| H1 | `h1_bottleneck_dispatch.py` | Queue/processing bottleneck dispatch |
| H2 | `h2_pm_risk_priority.py` | HI/RUL/PM due priority |
| H3 | `h3_cost_unit_value.py` | Cost-based operational value |
| H4 | `h4_flow_backpressure.py` | Whole-system flow/backpressure |

---

## Non-Policy Scenario

Drop Zone is not a policy.  
Do not implement Drop Zone under H4.
