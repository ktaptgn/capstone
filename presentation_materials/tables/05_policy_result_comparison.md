# 05 Policy Result Comparison

Source used: outputs/c5_1/summary/policy_comparison.csv plus replay logs in outputs/c5_1/logs/*.json for PM count and downtime.

| Policy | Total Cost / TCO (CU) | Production / Throughput | PM Count | Failure Count | Downtime (hr) | Queue Cost | Target Shortfall | Main Interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H0 | 1858.648 | 6243.333 | 416.667 | N/A | 1250 | N/A | 347.667 | trade-off policy; compare cost, fulfillment, PM, queue together |
| H1 | 7062.531 | 3285 | 160.667 | N/A | 481.333 | N/A | 3306 | trade-off policy; compare cost, fulfillment, PM, queue together |
| H2 | 3339.374 | 5371.667 | 322.333 | N/A | 966 | N/A | 1219.333 | trade-off policy; compare cost, fulfillment, PM, queue together |
| H3 | 1724.749 | 6398.333 | 496 | N/A | 1431.333 | N/A | 192.667 | lowest CU cost and highest fulfillment in official 365-day sweep |
| H4 | 7062.531 | 3285 | 160.667 | N/A | 481.333 | N/A | 3306 | trade-off policy; compare cost, fulfillment, PM, queue together |

Conflict note: outputs/c5_1/analysis/policy_kpi_summary.csv contains smaller-scale KPI values than the official 365-day summary. This pack uses outputs/c5_1/summary/policy_comparison.csv for numeric policy comparison.
