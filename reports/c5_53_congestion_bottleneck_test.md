# C5.53 Congestion Bottleneck Test

## Why C5.53 Was Needed

C5.52 proved that objective definition changes the policy ranking, but its logs could not prove whether route concentration creates route, shovel, or crusher bottlenecks. C5.53 keeps the C5.52 route/facility/grade-aware structure and adds deterministic congestion logging plus a separate congestion-aware TCO extension.

## New Instrumentation

- Dispatch events record preferred route, assigned route, fallback reason, route/shovel/crusher utilization before and after, queue delay components, base cycle time, route cycle factor, and realized cycle time.
- Daily summaries aggregate route/facility loads and attempts, fallback/rejected loads, queue hours, congestion cost, average realized cycle time, completed loads per hour, route HHI, and max route share.
- `total_tco_v1` keeps the legacy reliability-cost objective, `total_tco_v2` keeps the C5.52 grade-aware objective, and `total_tco_v3` adds congestion cost on top of v2.

## Literature-Informed Proxy Cycle-Time Calibration

C5.53 uses literature-informed proxy values for ultra-class truck speed, shovel loading time, crusher dumping/service time, and virtual route distance. These values are not real Escondida measurements. They are used to create a physically plausible bottleneck surface and are evaluated through sensitivity analysis.

- Truck speed proxy: OEM top speed reference is 64 km/h and is used only as an upper-bound sanity check. Base empty operating speed is 32 km/h; base loaded operating speed is 24 km/h.
- Loading proxy: 350 t payload is loaded through route shovel proxies with 100-110 t bucket payload, 35-42 second bucket cycles, and 0.7-0.9 minute spotting time.
- Crusher service proxy: spotting is 0.8 min, dumping is 1.2 min, and crusher acceptance is 1.6 min for Crusher 1 versus 1.1 min for Crusher 2.
- Route distance proxy: virtual empty/loaded distances are shortest for C routes, middle for B routes, and longest for A routes; Crusher 2 routes have longer loaded travel distance but lower service acceptance time.

| route | shovel | crusher | empty km | loaded km | empty speed km/h | loaded speed km/h | loading min | crusher service min | base cycle min | loads/truck-hour |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| R_A1 | SHOVEL_A | CRUSHER_1 | 3.5 | 4.5 | 27.2 | 19.2 | 3.70 | 3.60 | 29.08 | 2.06 |
| R_A2 | SHOVEL_A | CRUSHER_2 | 3.5 | 6.0 | 27.2 | 18.2 | 3.70 | 3.10 | 34.26 | 1.75 |
| R_B1 | SHOVEL_B | CRUSHER_1 | 2.5 | 3.5 | 32.0 | 24.0 | 3.33 | 3.60 | 20.37 | 2.95 |
| R_B2 | SHOVEL_B | CRUSHER_2 | 2.5 | 5.0 | 32.0 | 22.8 | 3.33 | 3.10 | 24.28 | 2.47 |
| R_C1 | SHOVEL_C | CRUSHER_1 | 1.5 | 2.5 | 36.8 | 26.4 | 3.03 | 3.60 | 14.76 | 4.06 |
| R_C2 | SHOVEL_C | CRUSHER_2 | 1.5 | 4.0 | 36.8 | 25.1 | 3.03 | 3.10 | 18.15 | 3.31 |

The resulting order is checked as a plausibility guardrail: R_C1 and R_C2 should be the fastest routes, B routes should sit in the middle, and A routes should be the slowest. The table is exported to `outputs/c5_53/analysis/c5_53_route_cycle_time_table.csv`.

## Policy x Regime Congestion Summary

| regime | policy | TCO v2 | TCO v3 | eff fulfillment | avg grade/load | failures | downtime | congestion h | cycle h | loads/h | HHI | max share | C-route share | route mix |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| heterogeneous_condition | H4 | 1609.5 | 1609.5 | 0.993 | 0.794 | 0.0 | 725.7 | 0.0 | 0.391 | 8.75 | 0.175 | 0.214 | 0.357 | R_A1 12.9%, R_A2 17.1%, R_B1 12.9%, R_B2 21.4%, R_C1 14.3%, R_C2 21.4% |
| heterogeneous_condition | H3 | 1664.9 | 1760.7 | 0.981 | 0.785 | 0.0 | 680.7 | 191.7 | 0.376 | 8.75 | 0.275 | 0.314 | 0.429 | R_A1 27.6%, R_A2 0.0%, R_B1 29.5%, R_B2 0.0%, R_C1 31.4%, R_C2 11.4% |
| heterogeneous_condition | H2 | 1824.8 | 1920.6 | 0.914 | 0.731 | 0.0 | 340.3 | 191.7 | 0.327 | 8.75 | 0.333 | 0.384 | 0.698 | R_A1 0.7%, R_A2 0.0%, R_B1 29.5%, R_B2 0.0%, R_C1 31.4%, R_C2 38.4% |
| heterogeneous_condition | H2_original | 1824.8 | 1920.6 | 0.914 | 0.731 | 0.0 | 340.3 | 191.7 | 0.327 | 8.75 | 0.333 | 0.384 | 0.698 | R_A1 0.7%, R_A2 0.0%, R_B1 29.5%, R_B2 0.0%, R_C1 31.4%, R_C2 38.4% |
| heterogeneous_condition | H2_value_guard | 1841.4 | 1937.2 | 0.914 | 0.732 | 0.0 | 353.7 | 191.7 | 0.328 | 8.75 | 0.331 | 0.380 | 0.695 | R_A1 1.0%, R_A2 0.0%, R_B1 29.5%, R_B2 0.0%, R_C1 31.4%, R_C2 38.0% |
| heterogeneous_condition | H1 | 1863.4 | 1939.5 | 0.912 | 0.730 | 0.0 | 352.3 | 152.2 | 0.326 | 8.75 | 0.301 | 0.390 | 0.705 | R_A1 0.3%, R_A2 0.0%, R_B1 20.4%, R_B2 8.8%, R_C1 31.4%, R_C2 39.0% |
| heterogeneous_condition | H1_original | 1863.4 | 1939.5 | 0.912 | 0.730 | 0.0 | 352.3 | 152.2 | 0.326 | 8.75 | 0.301 | 0.390 | 0.705 | R_A1 0.3%, R_A2 0.0%, R_B1 20.4%, R_B2 8.8%, R_C1 31.4%, R_C2 39.0% |
| heterogeneous_condition | H1_value_guard | 1846.8 | 1942.6 | 0.913 | 0.731 | 0.0 | 351.0 | 191.7 | 0.327 | 8.75 | 0.334 | 0.385 | 0.699 | R_A1 0.6%, R_A2 0.0%, R_B1 29.5%, R_B2 0.0%, R_C1 31.4%, R_C2 38.5% |
| heterogeneous_condition | H_TIME | 2903.9 | 2904.1 | 1.027 | 0.821 | 5.7 | 1434.7 | 0.5 | 0.415 | 8.75 | 0.184 | 0.220 | 0.224 | R_A1 22.0%, R_A2 21.9%, R_B1 22.0%, R_B2 11.6%, R_C1 11.6%, R_C2 10.8% |
| heterogeneous_condition | H0 | 3152.4 | 3152.6 | 1.027 | 0.822 | 11.0 | 1552.0 | 0.5 | 0.415 | 8.75 | 0.183 | 0.220 | 0.223 | R_A1 22.0%, R_A2 21.9%, R_B1 21.9%, R_B2 11.8%, R_C1 11.6%, R_C2 10.7% |

## H1/H2 vs H4 Bottleneck Interpretation

| regime | H1/H2 family mean C-route share | H1/H2 family mean congestion h | H1/H2 family mean HHI | H4 C-route share | H4 congestion h | H4 HHI | interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| heterogeneous_condition | 0.700 | 178.5 | 0.322 | 0.357 | 0.0 | 0.175 | H4 shows lower concentration and congestion |

## Findings

- C5.53 directly tests what C5.52 could only infer: whether route choice concentration creates queue delay, cycle time expansion, fallback, and extra TCO.
- H1/H2 should be read as reliability-cost policies first. If they keep concentrating on Shovel C routes, C5.53 can now show whether that concentration has a bottleneck penalty.
- H4 should be read as the diversification/backpressure comparator. If its HHI and congestion hours are lower while effective output remains competitive, it supports a congestion-aware production objective.
- H0/H_TIME remain useful baselines because they reveal whether high output is bought with failure, CM, downtime, or congestion cost.

## C5.54 / Value-Risk Sweep Implication

C5.54 is justified only if the C5.53 run shows material ranking movement between `total_tco_v2` and `total_tco_v3`, or if H1/H2 lose their advantage once C-route concentration is charged through congestion. If congestion is negligible at alpha/beta base settings, the next sweep should vary congestion alpha/beta before defining a new policy family.

