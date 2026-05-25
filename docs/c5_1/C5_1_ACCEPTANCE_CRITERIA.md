# C5_1_ACCEPTANCE_CRITERIA.md

## Required Completion Criteria

```text
[ ] C5.1 configs are present and loadable.
[ ] Drop Zone default is false.
[ ] RL default is false.
[ ] H0-H4 use the same policy interface.
[ ] H0-H4 run under the same config and seed.
[ ] policy sweep generates JSON logs.
[ ] policy sweep generates CSV and JSON KPI summaries.
[ ] total_cost, pm_cost, unmet_demand, demand_fulfillment_rate are calculated.
[ ] simulation visualization MVP can replay generated logs.
[ ] no operator dashboard code is implemented.
[ ] no PM app code is implemented.
[ ] no dashboard-app integration code is implemented.
```

---

## Tests

Recommended tests:

```text
tests/test_c5_1_config.py
tests/test_c5_1_policy_interface.py
tests/test_c5_1_cost_model.py
tests/test_c5_1_policy_sweep.py
tests/test_c5_1_log_schema.py
```
