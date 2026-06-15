# C5.4 Tier-2 Sensitivity — Key Findings

> **Hand-authored companion to `08_C5_4_SENSITIVITY.md`.** The tables in that file are auto-generated
> by `scripts/run_c5_4_sensitivity.py` and are **overwritten on every run**; this narrative is kept
> here so a re-run never clobbers it. All numbers trace to the tables in `08_C5_4_SENSITIVITY.md`.

## Key findings (read with the tables in `08_C5_4_SENSITIVITY.md`)

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
