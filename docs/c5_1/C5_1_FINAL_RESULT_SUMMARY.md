# C5.1 Final Result Summary

## Current Recommendation

- Recommended policy: `H3`
- Weighted rank score: `0.8`
- Basis: current weighted KPI rank score

H3 is recommended under the current C5.1 KPI weighting. It is not a mathematical global optimum.

## Best KPI Policies

| KPI | Label | Best Policy | Value | Direction |
|---|---|---|---:|---|
| `total_cost` | 총 운영비용 | H3 | 1,724.748667 | lower is better |
| `demand_fulfillment_rate` | 수요 충족률 | H3 | 0.970774 | higher is better |
| `unmet_demand` | 미충족 수요 | H3 | 192.666667 | lower is better |
| `queue_time` | 대기시간 | H1 / H4 | 2.215000 | lower is better |
| `average_available_trucks` | 가용 트럭 수 | H0 / H1 / H2 / H3 / H4 | 3.500000 | higher is better |
| `pm_cost` | PM 비용 | H1 / H4 | 200.666667 | lower is better |
| `total_downtime` | 총 다운타임 | H1 / H4 | 481.333333 | lower is better |

## H0 Improvement Highlights

- H3 reduces total operating cost by `7.204125%` compared with H0.
- H3 improves demand fulfillment by `0.023514`.
- H3 reduces unmet demand by `44.582934%` in the analysis table.
- H3 has higher PM cost and queue time than some alternatives, so it should be explained as a trade-off, not as a universal best answer.

## Stability

- Most stable by total cost standard deviation: `H2`
- H2 total cost standard deviation: `15.089415`

## Trade-off Message

H3 is the current recommendation because it leads the production and cost-oriented KPIs used by the weighted rank score. H1 and H4 are still important because they lead queue time, PM cost, and total downtime. H2 is useful when stability is the explanation focus.

## Missing KPI

- Missing KPI: `failure_count`
- Reason: current generated C5.1 result data does not include this field.
- Presentation note: failure count is excluded from the current ranking calculation.

## Limitations

- Current comparison is a 3-seed first comparison.
- Cost values are normalized.
- Results depend on the current C5.1 assumptions.
- RL is deferred to a separate RL Lab or repository.
- Drop Zone is excluded from the H0-H4 comparison.
