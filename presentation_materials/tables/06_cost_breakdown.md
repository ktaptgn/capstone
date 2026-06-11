# 06 Cost Breakdown

Source used: outputs/c5_1/summary/policy_comparison.csv, outputs/c5_1/logs/*.json, configs/cost_model_c5_1.yaml. Queue and failure cost are N/A because the official cost model does not expose separate queue/failure cost fields.

| Policy | PM Direct Cost | PM Downtime Cost | Tire Life / Degradation Cost | Queue Cost | Failure Cost | Target Shortfall Cost | Total Cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H0 | 520.833 | 625 | 17.481 | N/A | N/A | 695.333 | 1858.648 |
| H1 | 200.667 | 240.667 | 9.198 | N/A | N/A | 6612 | 7062.531 |
| H2 | 402.667 | 483 | 15.041 | N/A | N/A | 2438.667 | 3339.374 |
| H3 | 605.833 | 715.667 | 17.915 | N/A | N/A | 385.333 | 1724.749 |
| H4 | 200.667 | 240.667 | 9.198 | N/A | N/A | 6612 | 7062.531 |
