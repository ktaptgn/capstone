# C5.1 Heuristic Comparison Analysis

## 1. Analysis Purpose

C5.1 compares H0 baseline and H1-H4 heuristics under the same virtual mine environment, seed set, demand scenario generation, and KPI definitions. This report analyzes the current generated outputs without changing simulation or policy logic.

## 2. Input Data

- Summary CSV: `C:/working/Capstone/tests/fixtures/policy_comparison_missing_failure_sample.csv`
- Paired JSON summary not found at `C:/working/Capstone/tests/fixtures/policy_comparison_missing_failure_sample.json`; CSV was used as the analysis source.
- Policy logs: `outputs/c5_1/logs/*.json`
- Execution command: `python scripts/run_c5_1_policy_sweep.py --config configs/c5_1.yaml --policies H0 H1 H2 H3 H4 --seeds 1 2 3`

## 3. KPI Summary

Policy-level mean values are shown below. Full mean/std/min/max/CV values are exported in `outputs/c5_1/analysis/policy_kpi_summary.csv`.

Missing required KPI columns: `failure_count`.

| policy_id | total_cost | pm_cost | unmet_demand | demand_fulfillment_rate | completed_loads | average_available_trucks | total_downtime | pm_count | failure_count | average_tire_hi | average_truck_hi | queue_time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H0 | 1,020.00 | 205.00 | 105.00 | 0.8950 | 895.00 | 7.0000 | 122.00 | 20.5000 |  | 0.7950 | 0.8150 | 2.5500 |
| H1 | 960.00 | 242.50 | 85.0000 | 0.9150 | 915.00 | 6.7500 | 131.00 | 24.5000 |  | 0.8150 | 0.8250 | 2.4250 |
| H2 | 1,090.00 | 162.50 | 155.00 | 0.8450 | 845.00 | 7.1500 | 101.00 | 16.5000 |  | 0.7750 | 0.7950 | 2.2250 |
| H3 | 910.00 | 255.00 | 52.5000 | 0.9475 | 947.50 | 6.5500 | 143.50 | 27.5000 |  | 0.8375 | 0.8475 | 2.6750 |
| H4 | 985.00 | 192.50 | 97.5000 | 0.9025 | 902.50 | 7.0000 | 111.00 | 19.5000 |  | 0.8025 | 0.8125 | 2.3250 |

## 4. H0 Baseline Improvement

| policy_id | total_cost_improvement_pct | pm_cost_improvement_pct | unmet_demand_improvement_pct | demand_fulfillment_delta | completed_loads_delta | available_trucks_delta | total_downtime_improvement_pct | pm_count_improvement_pct | average_tire_hi_improvement_pct | average_truck_hi_improvement_pct | queue_time_improvement_pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1 | 5.8824 | -18.2927 | 19.0476 | 0.0200 | 20.0000 | -0.2500 | -7.3770 | -19.5122 | 2.5157 | 1.2270 | 4.9020 |
| H2 | -6.8627 | 20.7317 | -47.6190 | -0.0500 | -50.0000 | 0.1500 | 17.2131 | 19.5122 | -2.5157 | -2.4540 | 12.7451 |
| H3 | 10.7843 | -24.3902 | 50.0000 | 0.0525 | 52.5000 | -0.4500 | -17.6230 | -34.1463 | 5.3459 | 3.9877 | -4.9020 |
| H4 | 3.4314 | 6.0976 | 7.1429 | 0.0075 | 7.5000 | 0.0000 | 9.0164 | 4.8780 | 0.9434 | -0.3067 | 8.8235 |

## 5. Policy Ranking

Composite score is a presentation helper only. It is not a global optimum proof.

| policy_id | composite_score | total_cost_rank | demand_fulfillment_rate_rank | unmet_demand_rank | total_downtime_rank | queue_time_rank | average_available_trucks_rank | pm_cost_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H3 | 0.7000 | 1 | 1 | 1 | 5 | 5 | 5 | 5 |
| H1 | 0.6250 | 2 | 2 | 2 | 4 | 3 | 4 | 4 |
| H4 | 0.5750 | 3 | 3 | 3 | 2 | 2 | 2 | 2 |
| H0 | 0.3250 | 4 | 4 | 4 | 3 | 4 | 2 | 3 |
| H2 | 0.3000 | 5 | 5 | 5 | 1 | 1 | 1 | 1 |

## 6. Seed Stability

| policy_id | total_cost_mean | total_cost_std | demand_fulfillment_rate_std | unmet_demand_std | total_downtime_std | queue_time_std | stability_label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H4 | 985.00 | 7.0711 | 0.0035 | 3.5355 | 1.4142 | 0.0354 | strong_and_stable |
| H3 | 910.00 | 14.1421 | 0.0035 | 3.5355 | 2.1213 | 0.0354 | strong_and_stable |
| H1 | 960.00 | 14.1421 | 0.0071 | 7.0711 | 1.4142 | 0.0354 | strong_and_stable |
| H2 | 1,090.00 | 14.1421 | 0.0071 | 7.0711 | 1.4142 | 0.0354 | consistently_weak |
| H0 | 1,020.00 | 28.2843 | 0.0071 | 7.0711 | 2.8284 | 0.0707 | weak_and_variable |

## 7. Trade-off Analysis

- Cost vs demand fulfillment: lowest total cost = `H3`; highest demand fulfillment = `H3`. In the current run these are the same policy, so present both KPIs together.
- PM cost vs downtime/risk: lowest PM cost = `H2`. That does not automatically produce the lowest total cost or unmet demand.
- Queue time vs completed loads: lowest average queue time = `H2`; highest completed demand = `H3`. This shows queue reduction alone is not the final objective.
- Available trucks vs PM count: highest average available truck count = `H2`. Policies with more PM can still perform better on total cost if they prevent unmet-demand penalty.
- Tire/truck HI preservation vs production: best average tire HI = `H3`. The presentation recommendation should still use production and cost KPIs together.
- Composite helper: `H3` has the highest weighted presentation helper score. This is a display aid, not a mathematical proof of global optimality.

## 8. Policy-by-Policy Interpretation

## H0. Baseline

### Strong KPI
- average_available_trucks

### Weak KPI
- total_cost, demand_fulfillment_rate, unmet_demand, queue_time

### Interpretation
- H0 ranks best on average_available_trucks and is weakest on total_cost, demand_fulfillment_rate, unmet_demand, queue_time under the current C5.1 assumptions.

### Best Use Case
- Baseline reference for judging improvement and fairness.

### Risk
- Not optimized; useful as a control, not a recommendation.

## H1. Bottleneck Dispatch

### Strong KPI
- total_cost

### Weak KPI
- total_downtime, average_available_trucks, pm_cost

### Interpretation
- H1 ranks best on total_cost and is weakest on total_downtime, average_available_trucks, pm_cost under the current C5.1 assumptions.

### Best Use Case
- Use when preserving availability and holding queue pressure matters more than demand completion.

### Risk
- Large unmet demand in the current run despite low PM cost and strong availability.

## H2. PM Risk Priority

### Strong KPI
- total_downtime, queue_time, average_available_trucks, pm_cost

### Weak KPI
- total_cost, demand_fulfillment_rate, unmet_demand

### Interpretation
- H2 ranks best on total_downtime, queue_time, average_available_trucks, pm_cost and is weakest on total_cost, demand_fulfillment_rate, unmet_demand under the current C5.1 assumptions.

### Best Use Case
- Use when PM risk control is preferred but production shortfall must remain visible.

### Risk
- Middle performance can be hard to justify unless risk control is the presentation focus.

## H3. Cost Unit Value

### Strong KPI
- total_cost, demand_fulfillment_rate, unmet_demand

### Weak KPI
- total_downtime, queue_time, average_available_trucks, pm_cost

### Interpretation
- H3 ranks best on total_cost, demand_fulfillment_rate, unmet_demand and is weakest on total_downtime, queue_time, average_available_trucks, pm_cost under the current C5.1 assumptions.

### Best Use Case
- Use for the current balanced recommendation because it minimizes total cost while keeping demand fulfillment high.

### Risk
- Higher PM cost and queue time than some alternatives; recommendation should not be framed as global optimum.

## H4. Flow / Backpressure

### Strong KPI
- total_downtime

### Weak KPI
- total_cost

### Interpretation
- H4 ranks best on total_downtime and is weakest on total_cost under the current C5.1 assumptions.

### Best Use Case
- Use when flow/backpressure behavior is the focus; current implementation mirrors H1 on the observed KPI set.

### Risk
- Same observed results as H1 in the current environment, so it needs clearer scenario differentiation later.

## 9. Recommended Presentation Message

Use `H3` as the recommended policy for the current C5.1 presentation because it has the strongest weighted rank-score helper and should be discussed alongside KPI-specific winners. Avoid saying it is globally optimal.

## 10. Limitations

- Three seeds are enough for a first comparison, not full statistical proof.
- Cost values are normalized internal C5.1 values.
- Results depend on the current C5.1 assumptions and simplified environment.
- RL comparison is deferred to a separate RL Lab.
- Drop Zone is not part of the H0-H4 heuristic comparison.
