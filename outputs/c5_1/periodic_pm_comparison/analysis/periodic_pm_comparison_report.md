# C5.1 Heuristic Comparison Analysis

## 1. Analysis Purpose

C5.1 compares H0 baseline and H1-H4 heuristics under the same virtual mine environment, seed set, demand scenario generation, and KPI definitions. This report analyzes the current generated outputs without changing simulation or policy logic.

## 2. Input Data

- Summary CSV: `C:/working/Capstone/outputs/c5_1/periodic_pm_comparison/summary/policy_comparison.csv`
- Paired JSON summary: `C:/working/Capstone/outputs/c5_1/periodic_pm_comparison/summary/policy_comparison.json`. Row count matches; policy set matches.
- Policy logs: `outputs/c5_1/logs/*.json`
- Execution command: `python scripts/run_c5_1_policy_sweep.py --config configs/c5_1.yaml --policies H0 H1 H2 H3 H4 --seeds 1 2 3`

## 3. KPI Summary

Policy-level mean values are shown below. Full mean/std/min/max/CV values are exported in `outputs/c5_1/analysis/policy_kpi_summary.csv`.

Missing required KPI columns: `failure_count`.

| policy_id | total_cost | pm_cost | unmet_demand | demand_fulfillment_rate | completed_loads | average_available_trucks | total_downtime | pm_count | failure_count | average_tire_hi | average_truck_hi | queue_time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H0 | 1,858.65 | 520.83 | 347.67 | 0.9473 | 6,243.33 | 3.5000 | 1,250.00 | 416.67 |  | 0.8901 | 0.9046 | 2.2768 |
| H1 | 7,062.53 | 200.67 | 3,306.00 | 0.4984 | 3,285.00 | 3.5000 | 481.33 | 160.67 |  | 0.7916 | 0.8859 | 2.2150 |
| H2 | 3,339.37 | 402.67 | 1,219.33 | 0.8150 | 5,371.67 | 3.5000 | 966.00 | 322.33 |  | 0.8590 | 0.8809 | 2.3242 |
| H3 | 1,724.75 | 605.83 | 192.67 | 0.9708 | 6,398.33 | 3.5000 | 1,431.33 | 496.00 |  | 0.9029 | 0.9099 | 2.7260 |
| H4 | 7,062.53 | 200.67 | 3,306.00 | 0.4984 | 3,285.00 | 3.5000 | 481.33 | 160.67 |  | 0.7916 | 0.8859 | 2.2150 |
| H_PERIODIC | 4,283.06 | 1,095.00 | 856.00 | 0.8701 | 5,735.00 | 3.5000 | 2,920.00 | 730.00 |  | 0.0646 | 0.7631 | 1.7869 |
| H_TIME | 1,020.28 | 325.50 | 121.33 | 0.9816 | 6,469.67 | 3.5000 | 868.00 | 217.00 |  | 0.0836 | 0.9156 | 2.5467 |

## 4. H0 Baseline Improvement

| policy_id | total_cost_improvement_pct | pm_cost_improvement_pct | unmet_demand_improvement_pct | demand_fulfillment_delta | completed_loads_delta | available_trucks_delta | total_downtime_improvement_pct | pm_count_improvement_pct | average_tire_hi_improvement_pct | average_truck_hi_improvement_pct | queue_time_improvement_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | -279.98 | 61.4720 | -850.91 | -0.4488 | -2,958.33 | 0.0000 | 61.4933 | 61.4400 | -11.0670 | -2.0633 | 2.7147 |
| H2 | -79.6668 | 22.6880 | -250.72 | -0.1323 | -871.67 | 0.0000 | 22.7200 | 22.6400 | -3.5009 | -2.6205 | -2.0802 |
| H3 | 7.2041 | -16.3200 | 44.5829 | 0.0235 | 155.00 | 0.0000 | -14.5067 | -19.0400 | 1.4350 | 0.5921 | -19.7293 |
| H4 | -279.98 | 61.4720 | -850.91 | -0.4488 | -2,958.33 | 0.0000 | 61.4933 | 61.4400 | -11.0670 | -2.0633 | 2.7147 |
| H_PERIODIC | -130.44 | -110.24 | -146.21 | -0.0771 | -508.33 | 0.0000 | -133.60 | -75.2000 | -92.7469 | -15.6404 | 21.5180 |
| H_TIME | 45.1062 | 37.5040 | 65.1007 | 0.0343 | 226.33 | 0.0000 | 30.5600 | 47.9200 | -90.6046 | 1.2180 | -11.8551 |

## 5. Policy Ranking

Composite score is a presentation helper only. It is not a global optimum proof.

| policy_id | composite_score | total_cost_rank | demand_fulfillment_rate_rank | unmet_demand_rank | total_downtime_rank | queue_time_rank | average_available_trucks_rank | pm_cost_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H_TIME | 0.8833 | 1 | 1 | 1 | 3 | 6 | 1 | 3 |
| H3 | 0.7000 | 2 | 2 | 2 | 6 | 7 | 1 | 6 |
| H0 | 0.6500 | 3 | 3 | 3 | 5 | 4 | 1 | 5 |
| H_PERIODIC | 0.5000 | 5 | 4 | 4 | 7 | 1 | 1 | 7 |
| H2 | 0.4667 | 4 | 5 | 5 | 4 | 5 | 1 | 4 |
| H1 | 0.4000 | 6 | 6 | 6 | 1 | 2 | 1 | 1 |
| H4 | 0.4000 | 6 | 6 | 6 | 1 | 2 | 1 | 1 |

## 6. Seed Stability

| policy_id | total_cost_mean | total_cost_std | demand_fulfillment_rate_std | unmet_demand_std | total_downtime_std | queue_time_std | stability_label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H2 | 3,339.37 | 15.0894 | 0.0022 | 8.5049 | 8.7178 | 0.0051 | strong_and_stable |
| H3 | 1,724.75 | 33.6261 | 0.0026 | 17.9536 | 25.0067 | 0.0039 | strong_and_stable |
| H_TIME | 1,020.28 | 42.2866 | 0.0031 | 21.1266 | 0.0000 | 0.0027 | strong_and_stable |
| H0 | 1,858.65 | 46.3431 | 0.0028 | 20.0333 | 6.9282 | 0.0061 | strong_and_stable |
| H1 | 7,062.53 | 54.0887 | 0.0025 | 33.0454 | 16.0416 | 0.0000 | weak_and_variable |
| H4 | 7,062.53 | 54.0887 | 0.0025 | 33.0454 | 16.0416 | 0.0000 | weak_and_variable |
| H_PERIODIC | 4,283.06 | 55.4014 | 0.0039 | 27.7128 | 0.0000 | 0.0000 | weak_and_variable |

## 7. Trade-off Analysis

- Cost vs demand fulfillment: lowest total cost = `H_TIME`; highest demand fulfillment = `H_TIME`. In the current run these are the same policy, so present both KPIs together.
- PM cost vs downtime/risk: lowest PM cost = `H1 / H4`. That does not automatically produce the lowest total cost or unmet demand.
- Queue time vs completed loads: lowest average queue time = `H_PERIODIC`; highest completed demand = `H_TIME`. This shows queue reduction alone is not the final objective.
- Available trucks vs PM count: highest average available truck count = `H0 / H1 / H2 / H3 / H4 / H_PERIODIC / H_TIME`. Policies with more PM can still perform better on total cost if they prevent unmet-demand penalty.
- Tire/truck HI preservation vs production: best average tire HI = `H3`. The presentation recommendation should still use production and cost KPIs together.
- Composite helper: `H_TIME` has the highest weighted presentation helper score. This is a display aid, not a mathematical proof of global optimality.

## 8. Policy-by-Policy Interpretation

## H0. Baseline

### Strong KPI
- average_available_trucks

### Weak KPI
- total_downtime, queue_time, pm_cost

### Interpretation
- H0 ranks best on average_available_trucks and is weakest on total_downtime, queue_time, pm_cost under the current C5.1 assumptions.

### Best Use Case
- Baseline reference for judging improvement and fairness.

### Risk
- Not optimized; useful as a control, not a recommendation.

## H1. Bottleneck Dispatch

### Strong KPI
- total_downtime, average_available_trucks, pm_cost

### Weak KPI
- total_cost, demand_fulfillment_rate, unmet_demand

### Interpretation
- H1 ranks best on total_downtime, average_available_trucks, pm_cost and is weakest on total_cost, demand_fulfillment_rate, unmet_demand under the current C5.1 assumptions.

### Best Use Case
- Use when preserving availability and holding queue pressure matters more than demand completion.

### Risk
- Large unmet demand in the current run despite low PM cost and strong availability.

## H2. PM Risk Priority

### Strong KPI
- average_available_trucks

### Weak KPI
- total_cost, demand_fulfillment_rate, unmet_demand, total_downtime, queue_time, pm_cost

### Interpretation
- H2 ranks best on average_available_trucks and is weakest on total_cost, demand_fulfillment_rate, unmet_demand, total_downtime, queue_time, pm_cost under the current C5.1 assumptions.

### Best Use Case
- Use when PM risk control is preferred but production shortfall must remain visible.

### Risk
- Middle performance can be hard to justify unless risk control is the presentation focus.

## H3. Cost Unit Value

### Strong KPI
- average_available_trucks

### Weak KPI
- total_downtime, queue_time, pm_cost

### Interpretation
- H3 ranks best on average_available_trucks and is weakest on total_downtime, queue_time, pm_cost under the current C5.1 assumptions.

### Best Use Case
- Use for the current balanced recommendation because it minimizes total cost while keeping demand fulfillment high.

### Risk
- Higher PM cost and queue time than some alternatives; recommendation should not be framed as global optimum.

## H4. Flow / Backpressure

### Strong KPI
- total_downtime, average_available_trucks, pm_cost

### Weak KPI
- total_cost, demand_fulfillment_rate, unmet_demand

### Interpretation
- H4 ranks best on total_downtime, average_available_trucks, pm_cost and is weakest on total_cost, demand_fulfillment_rate, unmet_demand under the current C5.1 assumptions.

### Best Use Case
- Use when flow/backpressure behavior is the focus; current implementation mirrors H1 on the observed KPI set.

### Risk
- Same observed results as H1 in the current environment, so it needs clearer scenario differentiation later.

## 9. Recommended Presentation Message

Use `H_TIME` as the recommended policy for the current C5.1 presentation because it has the strongest weighted rank-score helper and should be discussed alongside KPI-specific winners. Avoid saying it is globally optimal.

## 10. Limitations

- Three seeds are enough for a first comparison, not full statistical proof.
- Cost values are normalized internal C5.1 values.
- Results depend on the current C5.1 assumptions and simplified environment.
- RL comparison is deferred to a separate RL Lab.
- Drop Zone is not part of the H0-H4 heuristic comparison.
