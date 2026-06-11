# C5.1 Policy Trade-off Notes

- Cost vs demand fulfillment: lowest total cost = `H_TIME`; highest demand fulfillment = `H_TIME`. In the current run these are the same policy, so present both KPIs together.
- PM cost vs downtime/risk: lowest PM cost = `H1 / H4`. That does not automatically produce the lowest total cost or unmet demand.
- Queue time vs completed loads: lowest average queue time = `H1 / H4`; highest completed demand = `H_TIME`. This shows queue reduction alone is not the final objective.
- Available trucks vs PM count: highest average available truck count = `H0 / H1 / H2 / H3 / H4 / H_TIME`. Policies with more PM can still perform better on total cost if they prevent unmet-demand penalty.
- Tire/truck HI preservation vs production: best average tire HI = `H3`. The presentation recommendation should still use production and cost KPIs together.
- Composite helper: `H_TIME` has the highest weighted presentation helper score. This is a display aid, not a mathematical proof of global optimality.
