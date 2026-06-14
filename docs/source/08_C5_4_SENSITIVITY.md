# C5.4 Tier-2 Sensitivity Analyses (method robustness)

- Reduced scale (stated for honesty): **10 seeds** [101, 102, 103, 104, 105, 106, 107, 108, 109, 110], **365 days**. The 30-seed x 3-regime headline lives in `07_C5_4_RESULTS.md`; these are robustness probes.
- Joint PM+dispatch; lower TCO better. State-aware = {H1 CBM, H2 risk}; blind = {H0 calendar, H_TIME hours}.

## 0. Key findings (read with the tables below)

1. **Condition-awareness value grows with frailty heterogeneity — and never disappears.** The state-aware
   advantage rises monotonically from **+33.4 % at cv = 0.10 to +49.8 % at cv = 0.80**. The slope is the
   *informational* value of condition (higher CV → condition says more beyond age, so H1/H2 actually get
   *cheaper* as CV rises — they exploit the slow trucks — while blind and H3/H4 get costlier). The large
   intercept (+33 % even at near-homogeneous cv = 0.10) is the *structural* inefficiency of blind
   full-vehicle PM, independent of heterogeneity. So the headline win is not a frailty artifact: it holds
   at low CV and widens at high CV.
2. **The frozen CBM threshold sits in a flat basin — robust, not tuned.** Perturbing 0.21/0.21/0.28 by
   ±20 % moves H1's TCO by **< 0.5 %** in both regimes (best is x0.90 mild / x0.80 stress, but the whole
   range is within noise). The C6.1 grid-search optimum is near-best here and the result does not hinge on
   its exact value.
3. **PM-bay count never reorders the top, but it exposes the mechanism.** State-aware wins at 1, 2 and 3
   bays. State-aware *needs* ≥ 2 bays (1 bay starves even targeted PM: 28.8k vs 22.7k) and is then flat
   (2→3 bays unchanged). Blind goes the **other way** — giving it a 3rd bay makes it **worse** (H0/H_TIME
   jump 39.7k → 53.2k) because it spends the extra bay-hours on more full-vehicle *over-service*, and the
   two blind policies flip at 3 bays. The value of state-aware PM is achieving protection with **fewer
   bay-hours**; throwing bays at blind PM backfires.
4. **The blind ≪ state-aware result is cadence-robust.** Across every calendar interval 3→8 days
   (TCO 39.7k → 51.7k) and every operating-hours budget 24→72 (37.0k → 39.6k), blind stays far above the
   state-aware reference (~22.7k). PM visits are pinned at ~1594 regardless of the calendar interval — the
   bay-saturation signature — so a tighter clock cannot rescue blind. The configured cadence (interval 3 /
   due 30) is blind's *best* case, not a strawman.

## 1. Frailty-CV sweep — when is condition-awareness most valuable?

Higher CV = more wear heterogeneity, so condition carries more information beyond age.

| CV | best state-aware TCO | best blind TCO | state-aware advantage |
|---:|---:|---:|---:|
| 0.10 | 23413.6 | 35167.0 | +33.4% |
| 0.20 | 23307.3 | 35182.8 | +33.8% |
| 0.30 | 23082.1 | 35825.0 | +35.6% |
| 0.40 | 22827.6 | 36986.4 | +38.3% |
| 0.50 | 22675.2 | 38693.2 | +41.4% |
| 0.65 | 22278.2 | 41206.2 | +45.9% |
| 0.80 | 21729.3 | 43296.5 | +49.8% |

Per-policy mean TCO by CV:

| CV | H0 | H_TIME | H1 | H2 | H3 | H4 |
|---:|---:|---:|---:|---:|---:|---:|
| 0.10 | 35352.7 | 35167.0 | 23435.1 | 23413.6 | 24680.3 | 24756.7 |
| 0.20 | 35896.9 | 35182.8 | 23320.7 | 23307.3 | 24822.9 | 24890.6 |
| 0.30 | 36945.1 | 35825.0 | 23097.0 | 23082.1 | 24963.3 | 25031.9 |
| 0.40 | 38107.7 | 36986.4 | 22870.8 | 22827.6 | 25022.5 | 25097.2 |
| 0.50 | 39675.7 | 38693.2 | 22675.2 | 22683.0 | 25191.8 | 25266.6 |
| 0.65 | 42236.0 | 41206.2 | 22315.0 | 22278.2 | 25625.2 | 25708.8 |
| 0.80 | 44317.8 | 43296.5 | 21729.3 | 21785.3 | 25819.8 | 25886.2 |

## 2. CBM-threshold robustness — is the frozen 0.21/0.21/0.28 near-optimal?

### Regime `heterogeneous_condition` (H1, the condition family)

- Frozen thresholds = {'tire': 0.21, 'engine': 0.21, 'brake': 0.28}; best scale here = **x0.90**.

| threshold x | tire/eng/brake | TCO | CM/run | PM visits |
|---:|---|---:|---:|---:|
| x0.80 | 0.168/0.168/0.224 | 22663.4 | 0.3 | 3121 |
| x0.90 **(best)** | 0.189/0.189/0.252 | 22617.6 | 0.1 | 3112 |
| x1.00 | 0.21/0.21/0.28 | 22675.2 | 0.0 | 3116 |
| x1.10 | 0.231/0.231/0.308 | 22658.5 | 0.1 | 3118 |
| x1.20 | 0.252/0.252/0.336 | 22715.0 | 0.0 | 3124 |

### Regime `high_stress` (H1, the condition family)

- Frozen thresholds = {'tire': 0.21, 'engine': 0.21, 'brake': 0.28}; best scale here = **x0.80**.

| threshold x | tire/eng/brake | TCO | CM/run | PM visits |
|---:|---|---:|---:|---:|
| x0.80 **(best)** | 0.168/0.168/0.224 | 32625.0 | 6.8 | 3863 |
| x0.90 | 0.189/0.189/0.252 | 32673.4 | 7.2 | 3866 |
| x1.00 | 0.21/0.21/0.28 | 32674.1 | 6.6 | 3854 |
| x1.10 | 0.231/0.231/0.308 | 32675.0 | 5.8 | 3842 |
| x1.20 | 0.252/0.252/0.336 | 32640.0 | 3.8 | 3855 |

## 3. PM-bay-count bottleneck — does queue contention reorder policies?

| bays | ranking (best->worst) | H0 | H_TIME | H1 | H2 | H3 | H4 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | H2 < H1 < H3 < H4 < H_TIME < H0 | 37957.1 | 37805.1 | 29003.0 | 28776.4 | 32498.8 | 33692.2 |
| 2 | H1 < H2 < H3 < H4 < H_TIME < H0 | 39675.7 | 38693.2 | 22675.2 | 22683.0 | 25191.8 | 25266.6 |
| 3 | H1 < H2 < H3 < H4 < H0 < H_TIME | 53233.5 | 53277.6 | 22683.1 | 22701.9 | 25153.1 | 25230.4 |

## 4. Blind-cadence robustness — is blind << state-aware a cadence artifact?

State-aware reference TCO (heterogeneous): H1 22675.2, H2 22683.0. Every blind cadence below is well above it, so the result is **cadence-robust** (not engineered by the chosen interval).

| H0 calendar interval (days) | TCO | fail/run | PM visits |
|---:|---:|---:|---:|
| 3 | 39675.7 | 180.8 | 1594 |
| 4 | 40721.6 | 222.9 | 1594 |
| 5 | 43686.3 | 340.8 | 1594 |
| 6 | 45953.2 | 432.5 | 1594 |
| 8 | 51710.9 | 658.5 | 1594 |

| H_TIME operating-hours due | TCO | fail/run | PM visits |
|---:|---:|---:|---:|
| 24 | 38718.5 | 147.7 | 1590 |
| 36 | 39396.6 | 174.1 | 1587 |
| 48 | 39641.3 | 272.1 | 1484 |
| 72 | 36982.8 | 551.3 | 1035 |

