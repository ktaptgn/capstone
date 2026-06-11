# C5.1 Presentation Result Summary

## One-line Result

`H_TIME` is the recommended current presentation policy using the weighted rank-score helper, while KPI-specific winners should be shown to explain trade-offs.

## Best Policy by KPI

| KPI | Best Policy | Reason |
| --- | --- | --- |
| Total cost | H_TIME | lower is better; leading/tied policy set: H_TIME. |
| Demand fulfillment | H_TIME | higher is better; leading/tied policy set: H_TIME. |
| Unmet demand | H_TIME | lower is better; leading/tied policy set: H_TIME. |
| Queue time | H1 / H4 | lower is better; leading/tied policy set: H1 / H4. |
| PM cost | H1 / H4 | lower is better; leading/tied policy set: H1 / H4. |
| Available trucks | H0 / H1 / H2 / H3 / H4 / H_TIME | higher is better; leading/tied policy set: H0 / H1 / H2 / H3 / H4 / H_TIME. |

## Recommended Policy for Presentation

- Recommended by current KPI helper: `H_TIME`
- Phrase carefully: recommended under current C5.1 assumptions, not globally optimal.

## Trade-off Message

- Show total cost, demand fulfillment, unmet demand, queue time, PM cost, and availability together.
- Explain why a policy can be strong on one KPI and weak on another.

## Slide Candidate Tables

- Policy KPI summary table
- H0 improvement table
- Ranking and composite helper table
- Trade-off notes for the recommended policy
