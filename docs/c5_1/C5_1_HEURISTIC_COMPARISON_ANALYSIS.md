# C5.1 Heuristic Comparison Analysis

## 1. Analysis Purpose

C5.1 compares H0 baseline and H1-H4 heuristics under the same virtual mine environment, seed set, demand scenario generation, and KPI definitions. This report analyzes the current generated outputs without changing simulation or policy logic.

## 2. Input Data

- Summary CSV: `C:/working/Capstone/outputs/c5_1/summary/policy_comparison.csv`
- Paired JSON summary: `C:/working/Capstone/outputs/c5_1/summary/policy_comparison.json`. Row count matches; policy set matches.
- Policy logs: `outputs/c5_1/logs/*.json`
- Execution command: `python scripts/run_c5_1_policy_sweep.py --config configs/c5_1.yaml --policies H0 H1 H2 H3 H4 --seeds 1 2 3`

## 3. KPI Summary

Policy-level mean values are shown below. Full mean/std/min/max/CV values are exported in `outputs/c5_1/analysis/policy_kpi_summary.csv`.

Missing required KPI columns: `failure_count`.

| policy_id | total_cost | pm_cost | unmet_demand | demand_fulfillment_rate | completed_loads | average_available_trucks | total_downtime | pm_count | failure_count | average_tire_hi | average_truck_hi | queue_time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H0 | 4,283.06 | 1,095.00 | 856.00 | 0.8701 | 5,735.00 | 3.5000 | 2,920.00 | 730.00 |  | 0.0646 | 0.7631 | 1.7869 |
| H1 | 1,858.65 | 520.83 | 347.67 | 0.9473 | 6,243.33 | 3.5000 | 1,250.00 | 416.67 |  | 0.8901 | 0.9046 | 2.2768 |
| H2 | 3,339.37 | 402.67 | 1,219.33 | 0.8150 | 5,371.67 | 3.5000 | 966.00 | 322.33 |  | 0.8590 | 0.8809 | 2.3242 |
| H3 | 1,724.75 | 605.83 | 192.67 | 0.9708 | 6,398.33 | 3.5000 | 1,431.33 | 496.00 |  | 0.9029 | 0.9099 | 2.7260 |
| H4 | 7,062.53 | 200.67 | 3,306.00 | 0.4984 | 3,285.00 | 3.5000 | 481.33 | 160.67 |  | 0.7916 | 0.8859 | 2.2150 |

## 4. H0 Baseline Improvement

| policy_id | total_cost_improvement_pct | pm_cost_improvement_pct | unmet_demand_improvement_pct | demand_fulfillment_delta | completed_loads_delta | available_trucks_delta | total_downtime_improvement_pct | pm_count_improvement_pct | average_tire_hi_improvement_pct | average_truck_hi_improvement_pct | queue_time_improvement_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | 56.6046 | 52.4353 | 59.3847 | 0.0771 | 508.33 | 0.0000 | 57.1918 | 42.9224 | 1,278.72 | 18.5402 | -27.4178 |
| H2 | 22.0329 | 63.2268 | -42.4455 | -0.0551 | -363.33 | 0.0000 | 66.9178 | 55.8447 | 1,230.46 | 15.4339 | -30.0684 |
| H3 | 59.7309 | 44.6728 | 77.4922 | 0.1006 | 663.33 | 0.0000 | 50.9817 | 32.0548 | 1,298.51 | 19.2421 | -52.5565 |
| H4 | -64.8946 | 81.6743 | -286.21 | -0.3717 | -2,450.00 | 0.0000 | 83.5160 | 77.9909 | 1,126.14 | 16.0943 | -23.9588 |

## 5. Policy Ranking

Composite score is a presentation helper only. It is not a global optimum proof.

| policy_id | composite_score | total_cost_rank | demand_fulfillment_rate_rank | unmet_demand_rank | total_downtime_rank | queue_time_rank | average_available_trucks_rank | pm_cost_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H3 | 0.8250 | 1 | 1 | 1 | 4 | 5 | 1 | 4 |
| H1 | 0.7250 | 2 | 2 | 2 | 3 | 3 | 1 | 3 |
| H0 | 0.4750 | 4 | 3 | 3 | 5 | 1 | 1 | 5 |
| H2 | 0.4500 | 3 | 4 | 4 | 2 | 4 | 1 | 2 |
| H4 | 0.2750 | 5 | 5 | 5 | 1 | 2 | 1 | 1 |

## 6. Seed Stability

| policy_id | total_cost_mean | total_cost_std | demand_fulfillment_rate_std | unmet_demand_std | total_downtime_std | queue_time_std | stability_label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H2 | 3,339.37 | 15.0894 | 0.0022 | 8.5049 | 8.7178 | 0.0051 | strong_and_stable |
| H3 | 1,724.75 | 33.6261 | 0.0026 | 17.9536 | 25.0067 | 0.0039 | strong_and_stable |
| H1 | 1,858.65 | 46.3431 | 0.0028 | 20.0333 | 6.9282 | 0.0061 | strong_and_stable |
| H4 | 7,062.53 | 54.0887 | 0.0025 | 33.0454 | 16.0416 | 0.0000 | weak_and_variable |
| H0 | 4,283.06 | 55.4014 | 0.0039 | 27.7128 | 0.0000 | 0.0000 | weak_and_variable |

## 7. Trade-off Analysis

- Cost vs demand fulfillment: lowest total cost = `H3`; highest demand fulfillment = `H3`. In the current run these are the same policy, so present both KPIs together.
- PM cost vs downtime/risk: lowest PM cost = `H4`. That does not automatically produce the lowest total cost or unmet demand.
- Queue time vs completed loads: lowest average queue time = `H0`; highest completed demand = `H3`. This shows queue reduction alone is not the final objective.
- Available trucks vs PM count: highest average available truck count = `H0 / H1 / H2 / H3 / H4`. Policies with more PM can still perform better on total cost if they prevent unmet-demand penalty.
- Tire/truck HI preservation vs production: best average tire HI = `H3`. The presentation recommendation should still use production and cost KPIs together.
- Composite helper: `H3` has the highest weighted presentation helper score. This is a display aid, not a mathematical proof of global optimality.

## 8. Policy-by-Policy Interpretation

## H0. Periodic PM Baseline

### Strong KPI
- queue_time, average_available_trucks

### Weak KPI
- total_cost, total_downtime, pm_cost

### Interpretation
- H0 ranks best on queue_time, average_available_trucks and is weakest on total_cost, total_downtime, pm_cost under the current C5.1 assumptions.

### Best Use Case
- Pure periodic PM baseline for judging improvement and fairness.

### Risk
- Ignores actual truck condition and demand; useful as a control, not a recommendation.

## H1. Due / Health PM

### Strong KPI
- average_available_trucks

### Weak KPI
- total_downtime

### Interpretation
- H1 ranks best on average_available_trucks and is weakest on total_downtime under the current C5.1 assumptions.

### Best Use Case
- Use when a simple PM due/HI-aware rule is sufficient without queue or cost optimization.

### Risk
- Does not optimize PM timing against queue pressure or operating cost.

## H2. PM Risk Priority

### Strong KPI
- average_available_trucks

### Weak KPI
- demand_fulfillment_rate, unmet_demand, queue_time

### Interpretation
- H2 ranks best on average_available_trucks and is weakest on demand_fulfillment_rate, unmet_demand, queue_time under the current C5.1 assumptions.

### Best Use Case
- Use when PM risk control is preferred but production shortfall must remain visible.

### Risk
- Middle performance can be hard to justify unless risk control is the presentation focus.

## H3. Cost Unit Value

### Strong KPI
- total_cost, demand_fulfillment_rate, unmet_demand, average_available_trucks

### Weak KPI
- total_downtime, queue_time, pm_cost

### Interpretation
- H3 ranks best on total_cost, demand_fulfillment_rate, unmet_demand, average_available_trucks and is weakest on total_downtime, queue_time, pm_cost under the current C5.1 assumptions.

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
- Use when flow/backpressure behavior is the focus.

### Risk
- Backpressure thresholds remain sensitive to the queue-state resolution.

## 9. Recommended Presentation Message

Use `H3` as the recommended policy for the current C5.1 presentation because it has the strongest weighted rank-score helper and should be discussed alongside KPI-specific winners. Avoid saying it is globally optimal.

## 10. Limitations

- Three seeds are enough for a first comparison, not full statistical proof.
- Cost values are normalized internal C5.1 values.
- Results depend on the current C5.1 assumptions and simplified environment.
- RL comparison is deferred to a separate RL Lab.
- Drop Zone is not part of the H0-H4 heuristic comparison.
