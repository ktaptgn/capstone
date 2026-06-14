# C5.4 Joint PM-Scheduling + Dispatch Results: H0-H4 + H_TIME (recast)

- Environment: 25-truck C5 mine + C6 routes A/B/C; 3-component HI (tire/engine/brake), frailty (Gamma wear heterogeneity) and C6 sensor noise. Decision target = JOINT PM-scheduling + dispatch; objective = total TCO (pm+cm+downtime+degradation+unmet).
- Policies (PM-family x dispatch-family pairs): H0 calendar+route-blind, H_TIME operating-hours+route-blind, H1 CBM+health, H2 risk+risk-aware, H3 cost-value+value, H4 flow+capacity.
- In-lab benchmark; not an official C5.1 ranking.

## Regime: `heterogeneous_condition`

- 365 days x 30 held-out seeds [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130]; lower TCO is better; best = **H2** (22367.1).

| rank | policy | TCO | PMvisits | PMcomps | CM/run | fail/run | fulfil | endHI | downHrs |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | H2 **(best)** | 22367.1 | 3070 | 3082 | 0.1 | 0.1 | 1.000 | 0.321 | 10901 |
| 2 | H1 | 22385.6 | 3071 | 3082 | 0.0 | 0.0 | 1.000 | 0.335 | 10912 |
| 3 | H3 | 23675.1 | 3183 | 3269 | 0.0 | 0.0 | 1.000 | 0.727 | 11552 |
| 4 | H4 | 23740.3 | 3196 | 3289 | 0.1 | 0.1 | 1.000 | 0.741 | 11575 |
| 5 | H_TIME | 36693.7 | 1588 | 4764 | 66.4 | 66.4 | 1.000 | 0.833 | 18176 |
| 6 | H0 | 37547.9 | 1594 | 4782 | 95.9 | 95.9 | 1.000 | 0.838 | 18572 |

Paired per-seed TCO vs H0 baseline (negative = cheaper than H0):

| seed | H2 | H1 | H3 | H4 | H_TIME | H0 |
|---|---:|---:|---:|---:|---:|---:|
| 101 | -14847.3 | -14846.9 | -14567.2 | -14463.2 | -1380.0 | +0.0 |
| 102 | -18862.7 | -18783.5 | -16773.3 | -16723.9 | -1748.3 | +0.0 |
| 103 | -18207.4 | -18054.8 | -12941.0 | -12897.9 | -852.2 | +0.0 |
| 104 | -16359.9 | -16464.6 | -13647.2 | -13583.5 | -645.7 | +0.0 |
| 105 | -16695.2 | -16764.3 | -14657.6 | -14597.4 | -1394.5 | +0.0 |
| 106 | -13164.7 | -13148.2 | -12726.1 | -12668.9 | -797.5 | +0.0 |
| 107 | -18833.8 | -18795.2 | -16169.6 | -16091.9 | -609.6 | +0.0 |
| 108 | -18437.2 | -18672.5 | -14240.3 | -14170.2 | -311.8 | +0.0 |
| 109 | -15530.6 | -15487.6 | -13780.3 | -13672.8 | -559.5 | +0.0 |
| 110 | -18988.4 | -18987.3 | -15336.9 | -15221.6 | -1525.6 | +0.0 |
| 111 | -14878.0 | -15239.5 | -15381.5 | -15324.0 | -126.7 | +0.0 |
| 112 | -15705.5 | -15711.5 | -16148.3 | -16089.8 | -1294.7 | +0.0 |
| 113 | -13779.1 | -13946.3 | -10968.7 | -10922.4 | -768.1 | +0.0 |
| 114 | -13273.1 | -13359.7 | -13437.0 | -13402.2 | -271.9 | +0.0 |
| 115 | -14475.1 | -14278.1 | -13089.9 | -13055.4 | -124.7 | +0.0 |
| 116 | -14029.0 | -14233.0 | -13472.6 | -13415.1 | -951.2 | +0.0 |
| 117 | -13961.4 | -14137.4 | -13089.6 | -13033.0 | -144.6 | +0.0 |
| 118 | -10478.0 | -10298.8 | -13480.9 | -13400.2 | -701.9 | +0.0 |
| 119 | -14607.2 | -14582.7 | -12291.3 | -12252.6 | -791.6 | +0.0 |
| 120 | -13836.1 | -13593.5 | -13415.9 | -13341.2 | -892.2 | +0.0 |
| 121 | -14922.5 | -14878.3 | -13677.8 | -13609.6 | -1183.6 | +0.0 |
| 122 | -13698.5 | -13440.7 | -14545.6 | -14499.6 | -718.4 | +0.0 |
| 123 | -13142.9 | -13259.3 | -12201.6 | -12150.6 | -1360.7 | +0.0 |
| 124 | -13193.1 | -13239.5 | -12513.6 | -12459.8 | -1212.9 | +0.0 |
| 125 | -14448.5 | -14524.3 | -15265.0 | -15216.5 | -490.0 | +0.0 |
| 126 | -14374.1 | -13712.7 | -14147.6 | -14089.4 | -18.0 | +0.0 |
| 127 | -15371.6 | -15379.1 | -13633.5 | -13557.6 | -1181.1 | +0.0 |
| 128 | -16371.1 | -16202.8 | -13586.6 | -13528.9 | -926.1 | +0.0 |
| 129 | -14752.5 | -14819.1 | -13144.8 | -13015.8 | -619.3 | +0.0 |
| 130 | -16198.8 | -16028.6 | -13851.2 | -13772.9 | -2023.9 | +0.0 |

- Seeds where each policy beats H0: H2 30/30, H1 30/30, H3 30/30, H4 30/30, H_TIME 30/30.

## Regime: `high_stress`

- 365 days x 30 held-out seeds [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130]; lower TCO is better; best = **H1** (32564.6).

| rank | policy | TCO | PMvisits | PMcomps | CM/run | fail/run | fulfil | endHI | downHrs |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | H1 **(best)** | 32564.6 | 3922 | 4013 | 2.4 | 2.4 | 1.000 | 0.317 | 15759 |
| 2 | H2 | 32584.2 | 3927 | 4012 | 3.6 | 3.6 | 1.000 | 0.302 | 15768 |
| 3 | H3 | 33689.7 | 3651 | 4130 | 13.3 | 13.3 | 1.000 | 0.717 | 16260 |
| 4 | H4 | 33807.0 | 3615 | 4145 | 17.4 | 17.4 | 1.000 | 0.719 | 16302 |
| 5 | H_TIME | 42519.7 | 1456 | 4368 | 256.4 | 256.4 | 1.000 | 0.652 | 20297 |
| 6 | H0 | 43361.6 | 1460 | 4380 | 276.7 | 276.7 | 1.000 | 0.715 | 20676 |

Paired per-seed TCO vs H0 baseline (negative = cheaper than H0):

| seed | H1 | H2 | H3 | H4 | H_TIME | H0 |
|---|---:|---:|---:|---:|---:|---:|
| 101 | -11499.2 | -11474.4 | -10312.1 | -10229.5 | -2043.9 | +0.0 |
| 102 | -13891.3 | -13841.2 | -11462.8 | -11388.0 | -1298.5 | +0.0 |
| 103 | -14822.3 | -15060.8 | -9962.8 | -9704.2 | -963.0 | +0.0 |
| 104 | -12247.8 | -12362.8 | -9997.4 | -9870.1 | -102.4 | +0.0 |
| 105 | -12356.6 | -12396.8 | -11406.4 | -11357.4 | -1092.3 | +0.0 |
| 106 | -8893.0 | -8927.6 | -8374.4 | -8306.9 | -1197.7 | +0.0 |
| 107 | -14025.4 | -13954.1 | -11965.8 | -11859.0 | -932.7 | +0.0 |
| 108 | -14090.4 | -13984.8 | -8655.4 | -8269.2 | -308.9 | +0.0 |
| 109 | -10397.0 | -10506.8 | -9157.5 | -9052.6 | -1162.6 | +0.0 |
| 110 | -15276.5 | -15072.6 | -10533.0 | -9689.7 | -952.4 | +0.0 |
| 111 | -8586.6 | -8523.8 | -9279.0 | -9204.5 | -2271.3 | +0.0 |
| 112 | -10692.1 | -10477.1 | -11053.0 | -10933.3 | -691.6 | +0.0 |
| 113 | -9912.1 | -9812.3 | -8548.9 | -8497.0 | -795.1 | +0.0 |
| 114 | -7961.9 | -8086.8 | -8616.3 | -8526.7 | -230.5 | +0.0 |
| 115 | -7939.0 | -7938.5 | -6960.9 | -6924.4 | -714.0 | +0.0 |
| 116 | -9722.9 | -9588.3 | -9942.4 | -9878.0 | -900.1 | +0.0 |
| 117 | -9514.0 | -9613.0 | -9360.5 | -9309.3 | -1195.2 | +0.0 |
| 118 | -9342.8 | -9168.5 | -10218.2 | -10168.2 | -732.8 | +0.0 |
| 119 | -10178.6 | -10110.6 | -8358.4 | -8297.7 | -1012.2 | +0.0 |
| 120 | -9214.0 | -9376.5 | -9065.2 | -8963.7 | -611.9 | +0.0 |
| 121 | -10308.0 | -10326.0 | -9081.9 | -8988.7 | -698.1 | +0.0 |
| 122 | -8193.5 | -8249.8 | -9480.7 | -9450.4 | -471.0 | +0.0 |
| 123 | -9926.7 | -9820.0 | -9241.9 | -9175.9 | -209.0 | +0.0 |
| 124 | -9989.5 | -10302.4 | -9544.3 | -9453.4 | -776.5 | +0.0 |
| 125 | -8952.2 | -8556.2 | -9192.6 | -9143.1 | -617.1 | +0.0 |
| 126 | -10008.8 | -10082.6 | -11024.0 | -10917.2 | -200.4 | +0.0 |
| 127 | -11225.6 | -11018.3 | -9602.3 | -9544.8 | +162.6 | +0.0 |
| 128 | -11642.5 | -11594.4 | -10266.2 | -10206.6 | -1439.1 | +0.0 |
| 129 | -11131.0 | -11158.4 | -9736.6 | -9652.0 | -306.7 | +0.0 |
| 130 | -11970.3 | -11936.7 | -9756.4 | -9677.8 | -1491.9 | +0.0 |

- Seeds where each policy beats H0: H1 30/30, H2 30/30, H3 30/30, H4 30/30, H_TIME 29/30.

## Regime: `high_demand_high_stress`

- 365 days x 30 held-out seeds [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130]; lower TCO is better; best = **H1** (47630.8).

| rank | policy | TCO | PMvisits | PMcomps | CM/run | fail/run | fulfil | endHI | downHrs |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | H1 **(best)** | 47630.8 | 3615 | 4308 | 44.1 | 44.1 | 0.934 | 0.275 | 17272 |
| 2 | H2 | 47654.6 | 3674 | 4300 | 46.4 | 46.4 | 0.934 | 0.262 | 17288 |
| 3 | H3 | 48046.9 | 3380 | 4382 | 42.4 | 42.4 | 0.934 | 0.647 | 17469 |
| 4 | H4 | 48070.8 | 3297 | 4374 | 48.2 | 48.2 | 0.934 | 0.646 | 17461 |
| 5 | H_TIME | 56673.4 | 1456 | 4368 | 346.2 | 346.2 | 0.934 | 0.579 | 21354 |
| 6 | H0 | 57397.1 | 1460 | 4380 | 360.1 | 360.1 | 0.934 | 0.621 | 21687 |

Paired per-seed TCO vs H0 baseline (negative = cheaper than H0):

| seed | H1 | H2 | H3 | H4 | H_TIME | H0 |
|---|---:|---:|---:|---:|---:|---:|
| 101 | -9128.2 | -9176.3 | -9320.0 | -9317.6 | -1277.6 | +0.0 |
| 102 | -12455.0 | -12238.7 | -10776.2 | -10855.2 | -503.5 | +0.0 |
| 103 | -13002.4 | -12862.6 | -8744.1 | -8345.5 | -428.5 | +0.0 |
| 104 | -11303.2 | -11379.1 | -10527.4 | -10575.3 | -1076.1 | +0.0 |
| 105 | -11988.0 | -11903.3 | -10384.5 | -10594.9 | -210.7 | +0.0 |
| 106 | -7174.7 | -6948.5 | -8029.8 | -8034.0 | -832.0 | +0.0 |
| 107 | -13065.1 | -13019.1 | -11650.5 | -11822.0 | -467.4 | +0.0 |
| 108 | -11933.4 | -11823.4 | -7922.6 | -7761.7 | -536.9 | +0.0 |
| 109 | -9493.1 | -9398.4 | -9636.2 | -9646.6 | -1405.1 | +0.0 |
| 110 | -10002.6 | -10578.5 | -9218.6 | -8327.1 | -1346.5 | +0.0 |
| 111 | -7386.4 | -7429.1 | -8371.5 | -8337.8 | -1208.6 | +0.0 |
| 112 | -10250.0 | -10112.8 | -11198.4 | -11240.6 | -753.1 | +0.0 |
| 113 | -7983.0 | -7782.3 | -8049.2 | -8093.9 | -325.8 | +0.0 |
| 114 | -7833.0 | -7710.7 | -8319.0 | -8366.5 | -408.3 | +0.0 |
| 115 | -8110.0 | -8166.2 | -7520.6 | -7572.1 | -1093.5 | +0.0 |
| 116 | -11214.7 | -11207.3 | -9824.8 | -9854.9 | -748.9 | +0.0 |
| 117 | -8494.6 | -8304.9 | -8582.8 | -8616.6 | -624.5 | +0.0 |
| 118 | -7591.5 | -8354.1 | -9746.6 | -9594.0 | -1083.3 | +0.0 |
| 119 | -9519.0 | -9174.5 | -7502.2 | -7547.3 | +15.1 | +0.0 |
| 120 | -7607.7 | -7469.3 | -8108.5 | -8099.9 | -506.6 | +0.0 |
| 121 | -8461.1 | -8297.9 | -8146.8 | -8207.9 | -303.9 | +0.0 |
| 122 | -7196.1 | -7045.1 | -9050.4 | -9076.3 | -350.4 | +0.0 |
| 123 | -11157.4 | -10755.8 | -9608.6 | -9595.5 | -311.6 | +0.0 |
| 124 | -7373.0 | -8158.5 | -9660.1 | -9933.0 | -1290.4 | +0.0 |
| 125 | -7077.1 | -7117.7 | -8724.4 | -8743.7 | -247.5 | +0.0 |
| 126 | -8807.2 | -8800.1 | -11051.4 | -11114.2 | -718.2 | +0.0 |
| 127 | -12788.1 | -12658.0 | -9256.1 | -8668.3 | +156.4 | +0.0 |
| 128 | -12449.9 | -12574.5 | -11440.4 | -11515.3 | -1485.4 | +0.0 |
| 129 | -10784.1 | -10479.6 | -9506.9 | -9647.3 | -687.5 | +0.0 |
| 130 | -11359.2 | -11349.5 | -10625.2 | -10683.1 | -1649.1 | +0.0 |

- Seeds where each policy beats H0: H1 30/30, H2 30/30, H3 30/30, H4 30/30, H_TIME 28/30.

## Cross-regime summary

| regime | ranking (best->worst) | best |
|---|---|---|
| heterogeneous_condition | H2 < H1 < H3 < H4 < H_TIME < H0 | H2 |
| high_stress | H1 < H2 < H3 < H4 < H_TIME < H0 | H1 |
| high_demand_high_stress | H1 < H2 < H3 < H4 < H_TIME < H0 | H1 |

---

## Interpretation (why this ranking, and why the order is stable)

**1. Headline.** Joint **state-aware PM + dispatch** (H1 CBM+health, H2 risk) beats **blind periodic PM**
(H0 calendar, H_TIME operating-hours) on TCO by **40.4 % / 24.9 % / 17.0 %** in the
heterogeneous / high_stress / high_demand_high_stress regimes — and does so on **30/30 paired seeds**
in every regime (H_TIME beats H0 on 28–30/30). The ranking
**H1≈H2 < H3≈H4 < H_TIME < H0** is identical across all three regimes; only the within-pair order
shifts.

**2. Why H1 and H2 swap (and why it doesn't matter).** H1 (CBM threshold) and H2 (risk-priority) fire PM
on near-identical signals — the observed HI versus the same HI mapped through the risk score — so under
the 0.03 sensor noise they refer almost the same components and finish within seed-level noise of each
other (Δ < 0.1 % every regime). H2 is nominally best in the mild regime, H1 in both stress regimes; the
flip is noise, not a real ordering. The defended signal is **state-aware ≫ blind**, exactly as in C5.3.

**3. The mechanism (full detail in `09_C5_4_MECHANISM.md`).** With identical reliability physics, the
blind baselines lose on **two axes at once**:
- **They over-service.** H0/H_TIME do *full-vehicle* services (PM components ≈ 3× visits) on a fixed
  clock and end the campaign over-maintained (end HI 0.84/0.83) — wasted PM and downtime.
- **They under-protect the tail.** Those full-vehicle visits are so bay-heavy that the 2 PM bays cap out
  at ~1460–1594 visits/yr, so the fast-frailty trucks are never caught and fail: CM rises from
  ~66–96/run (mild) to ~257–360/run (extreme), and ~66 % of it is **tire** (the fastest-wearing part
  that equal-share blind PM systematically under-services).

State-aware H1/H2 instead do **~2× more** PM visits that are each **short and targeted** (≈1 component,
concentrated on the tire), so they fit the bays, run trucks **lean** (end HI 0.32) and reach ~0 failures
(mild) / ≤ 7 (stress) — paying *less* PM cost while avoiding the CM + downtime blow-up.

**4. The H3/H4 second tier.** Cost-value (H3) and flow/backpressure (H4) PM beat blind comfortably but
sit ~6 % above H1/H2 in the mild regime and grow a real failure tail under stress (CM 13→42 and 17→48
per run) because their triggers *tolerate more wear*: H3 only PMs once the anticipated CM cost justifies
it (later than the CBM threshold), and H4 defers PM under demand pressure. They end with high HI
(0.65–0.74) — fewer, later services — which is cheaper than blind but costlier than lean CBM.

**5. The advantage shrinks as stress rises (40 % → 25 % → 17 %).** Where reliability is a discretionary
efficiency lever (mild regime), blind PM's needless over-service dominates its loss; as wear/hazard rise,
every policy must PM more and the failure path activates for all, so the *relative* gap narrows — but
state-aware stays on top on 28–30/30 seeds throughout. Under extreme demand (fulfilment 0.934 for every
policy, demand > total route capacity) the binding constraint becomes throughput, not maintenance, and
the H1/H2-vs-H3/H4 margin compresses to < 1 %.

**6. Anti-overclaim notes.**
- The blind cadence is **steelmanned** (calendar interval 3 / hours due 30 — the fast-frailty-tail,
  tightest-feasible value; iv = 8 would make blind look ~25 % worse). The cadence sweep in
  `08_C5_4_SENSITIVITY.md` confirms blind ≫ state-aware across the whole interval 3→8 range, so the
  result is **cadence-robust, not an artifact**.
- `endHI` is an **end-of-campaign snapshot**: state-aware's low value (0.32) is the *intended* behaviour
  (running trucks near the PM threshold), not poor health — read it with the timing/causal analysis in
  `09`.
- **Fulfilment = 1.000 for every policy** in both non-extreme regimes (even blind meets demand), so the
  entire TCO gap is *maintenance efficiency* (pm + cm + downtime), not lost production — a clean
  comparison on the axis C5.4 is about.

---

## Presentation figures (Tier 4)

Rendered by `scripts/plot_c5_4_results.py` from the analysis artifacts (no re-simulation) to
`outputs/c5_4/analysis/` as PNG + SVG:

| figure | shows |
|---|---|
| `c5_4_tco_boxplots` | per-policy TCO distribution across 30 seeds, faceted by regime — state-aware lowest and tightest, blind high and high-variance. |
| `c5_4_failure_vs_endhi` | per-seed failures vs end-of-campaign HI — blind ends high-HI (over-serviced) yet fails; state-aware runs lean (~0.3) yet does not (CBM-threshold validity). |
| `c5_4_frailty_cv_curve` | mean TCO vs frailty CV per policy — the state-aware advantage widens +33 % → +50 % as heterogeneity rises (shaded gap). |
| `c5_4_failure_timing` | failures by campaign third (early/mid/late) — blind fails steadily across the whole campaign (frailty leak); state-aware ~0. |

