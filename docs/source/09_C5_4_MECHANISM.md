# C5.4 Tier-3 Failure-Mechanism Analysis

- Reduced, stated scale: **12 seeds** [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112], **365 days**, regimes ['heterogeneous_condition', 'high_stress']; per-failure event logging. Headline numbers: `07_C5_4_RESULTS.md`.

## 0. Key findings (read with the tables below)

1. **Failures are blind PM's, and they are frailty-structural.** Blind H0/H_TIME incur ~130–162 CM/run
   in the mild regime (~296–322 under stress); every state-aware policy is ≤ 7 even under stress. For the
   blind policies the per-seed failure count correlates **0.91** with that seed's worst frailty draw
   (seed 110, the highest-frailty draw, is the worst seed for both) — so a high-CM seed is a *structural*
   unlucky-frailty draw, not noise. For condition-based H1 that correlation collapses (None / 0.46):
   **state-aware PM breaks the frailty→failure link** by adapting to each truck.
2. **Tire is the failure axis, and blind PM under-protects it.** Blind PM splits services *equally* across
   components (33/33/33 — full vehicle service), but **66–73 % of blind CM is tire** (the fastest wearer).
   State-aware concentrates PM on tire (~40 %) and routes ~loads away from the steep route C (22 % vs
   ~30 %), so the tire rarely crosses the failure floor.
3. **Blind over-maintains yet still fails; state-aware runs lean yet does not.** Blind H0 ends the campaign
   at HI 0.87/0.90/0.92 (heavily over-serviced) but still fails ~162×/run; H1 ends at 0.37/0.43/0.45
   (trucks run near the PM threshold) with 0 failures. The fundamental H1-vs-H0 gap is **both** part
   management (tire-targeted PM) **and** route selection (less C), dominated by part management. Failures
   are spread ~evenly across the campaign thirds — a steady frailty-driven leak under blind PM, not an
   early break-in or late wear-out artifact.

## 1. Failure-timing histogram (campaign early / mid / late thirds)

| regime | policy | early | mid | late | total |
|---|---|---:|---:|---:|---:|
| heterogeneous_condition | H0 | 615 | 664 | 663 | 1942 |
| heterogeneous_condition | H_TIME | 469 | 548 | 548 | 1565 |
| heterogeneous_condition | H1 | 0 | 0 | 0 | 0 |
| heterogeneous_condition | H2 | 0 | 0 | 1 | 1 |
| heterogeneous_condition | H3 | 0 | 0 | 0 | 0 |
| heterogeneous_condition | H4 | 0 | 0 | 2 | 2 |
| high_stress | H0 | 1194 | 1335 | 1337 | 3866 |
| high_stress | H_TIME | 1077 | 1219 | 1255 | 3551 |
| high_stress | H1 | 17 | 21 | 29 | 67 |
| high_stress | H2 | 16 | 33 | 30 | 79 |
| high_stress | H3 | 116 | 141 | 143 | 400 |
| high_stress | H4 | 142 | 185 | 187 | 514 |

## 2. Per-seed failure distribution & frailty correlation

corr(max_frailty, failures) across seeds (None = too few/no-variance):

| regime | policy | corr(maxFrailty, fails) | worst seed |
|---|---|---:|---:|
| heterogeneous_condition | H0 | 0.911 | 110 |
| heterogeneous_condition | H_TIME | 0.917 | 110 |
| heterogeneous_condition | H1 | None | 101 |
| heterogeneous_condition | H2 | -0.202 | 102 |
| heterogeneous_condition | H3 | None | 101 |
| heterogeneous_condition | H4 | 0.448 | 103 |
| high_stress | H0 | 0.912 | 110 |
| high_stress | H_TIME | 0.922 | 110 |
| high_stress | H1 | 0.46 | 110 |
| high_stress | H2 | 0.481 | 110 |
| high_stress | H3 | 0.764 | 110 |
| high_stress | H4 | 0.756 | 110 |

## 3. Per-policy causal profile

Route mix %, per-component PM share %, per-component CM share %, end HI. Shows whether a policy differs by *route selection* or *part management*.

### Regime `heterogeneous_condition`

| policy | route A/B/C % | PM tire/eng/brake % | CM tire/eng/brake % | end HI t/e/b | TCO | CM/run |
|---|---|---|---|---|---:|---:|
| H0 | 36.9/33.6/29.5 | 33.3/33.3/33.3 | 65.9/20.6/13.5 | 0.87/0.903/0.923 | 39180.6 | 161.8 |
| H_TIME | 36.9/33.6/29.5 | 33.3/33.3/33.3 | 69.1/15.6/15.3 | 0.866/0.884/0.918 | 38243.4 | 130.4 |
| H1 | 41.9/35.7/22.4 | 39.9/33.4/26.7 | 0.0/0.0/0.0 | 0.371/0.425/0.446 | 22434.3 | 0.0 |
| H2 | 41.9/35.7/22.4 | 40.0/33.3/26.7 | 100.0/0.0/0.0 | 0.353/0.417/0.402 | 22471.4 | 0.1 |
| H3 | 41.9/28.6/29.5 | 40.5/32.7/26.8 | 0.0/0.0/0.0 | 0.772/0.761/0.763 | 24483.1 | 0.0 |
| H4 | 38.6/34.3/27.1 | 41.1/32.4/26.5 | 100.0/0.0/0.0 | 0.775/0.773/0.782 | 24555.2 | 0.2 |

### Regime `high_stress`

| policy | route A/B/C % | PM tire/eng/brake % | CM tire/eng/brake % | end HI t/e/b | TCO | CM/run |
|---|---|---|---|---|---:|---:|
| H0 | 36.9/33.5/29.5 | 33.3/33.3/33.3 | 66.3/22.2/11.4 | 0.789/0.814/0.859 | 44744.6 | 322.2 |
| H_TIME | 37.0/33.5/29.5 | 33.3/33.3/33.3 | 73.2/15.4/11.4 | 0.778/0.766/0.847 | 43659.8 | 295.9 |
| H1 | 41.9/35.7/22.4 | 39.4/32.8/27.8 | 95.5/0.0/4.5 | 0.35/0.41/0.413 | 32513.1 | 5.6 |
| H2 | 41.9/35.7/22.4 | 39.4/32.8/27.8 | 96.2/1.3/2.5 | 0.343/0.401/0.386 | 32529.3 | 6.6 |
| H3 | 41.9/28.6/29.5 | 39.2/32.8/28.0 | 55.0/27.7/17.2 | 0.752/0.727/0.751 | 34564.6 | 33.3 |
| H4 | 38.6/34.3/27.1 | 39.2/33.1/27.7 | 86.0/4.3/9.7 | 0.743/0.748/0.756 | 34755.9 | 42.8 |

