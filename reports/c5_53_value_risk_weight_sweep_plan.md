# C5.53 Value-Risk Weight Sweep Plan

## Purpose

C5.53 should not be implemented yet. This proposal defines the next DOE-style experiment to search for a better value-risk balance after C5.52 showed that H1/H2 optimize reliability cost while H4 optimizes grade-aware value under base/high shortfall sensitivity.

## Why the Current Value Guard Was Too Weak

- The C5.52 value_guard variants only added a modest production-value term to H1/H2 scoring.
- Route shares barely moved: H1/H2 variants still concentrated on B/C and especially C routes.
- Effective fulfillment stayed around 0.912-0.924 for H1/H2 variants, far below H4 at roughly 0.993-0.994.
- The value term was not strong enough to overcome risk/stress penalties that push H1/H2 away from A/B value routes.

## Why One-Variable-at-a-Time Tuning Should Be Avoided

Changing only `w_value` or only `w_risk` can misread interactions. A route score is a coupled value-risk-queue decision: raising value weight can increase failures, raising risk weight can collapse effective output, and queue weight can change route capacity pressure. A DOE matrix is needed to see interactions without tuning parameters to force a preferred winner.

## Candidate Factor Matrix

| Factor | Levels | Rationale |
|---|---|---|
| `w_value` | 0.5, 1.0, 2.0, 4.0 | Test whether stronger production value moves H2 away from low-grade C routes |
| `w_risk` | 0.5, 1.0, 2.0 | Control component protection strength |
| `w_queue` | 0.5, 1.0 | Preserve flow/capacity balance without overbuilding queue simulation |
| `effective_shortfall_sensitivity` | low, base, high | Keep objective-sensitivity continuity with C5.52 |
| `policy_base` | H2, H4 | Test both risk-first plus value and flow-first plus risk guard |

Full factorial size: `4 x 3 x 2 x 3 x 2 = 144` configurations before seeds/regimes. This is likely too large for routine iteration.

## Primary Response

Recommended primary response: `total_tco_v2_base`.

Reason: C5.52 established that base shortfall sensitivity is strong enough to expose the production-value gap while not immediately collapsing the comparison into only output maximization.

## Guardrail Metrics

- `demand_fulfillment_rate >= 0.99`
- `effective_fulfillment_rate >= 0.98`
- `failure_count` not worse than H4 baseline
- `downtime_hours` not worse than H4 baseline by more than 10%
- Secondary: PM visits, CM count, Shovel C share, and route concentration

## Recommended Reduced Matrix for Runtime Control

Stage 1 screening, 32 configurations:

| Dimension | Reduced levels |
|---|---|
| `policy_base` | H2, H4 |
| `w_value` | 1.0, 2.0, 4.0 |
| `w_risk` | 0.5, 1.0 |
| `w_queue` | 0.5, 1.0 |
| sensitivity | base only for screening |

This gives `2 x 3 x 2 x 2 = 24` core configs. Add 8 anchor configs: C5.52 H2_original, H2_value_guard, H3, H4 across the same regimes/seeds for paired comparison.

Stage 2 confirmation: run the best 4-6 screening configs across low/base/high sensitivity and the full 3 regimes x 10 seeds x 90 days. Only then consider 365-day confirmation.

## Expected Outcome

- `H2_value_weighted` may improve effective output, but could raise failure, CM, degradation, or downtime as it selects higher-grade/stress routes.
- `H4_risk_guard` may retain output while reducing failure and downtime relative to H4.
- A balanced H5 may be justified only after the sweep shows a stable non-dominated combination across regimes and guardrails.

## C5.53 Implementation Criteria

Implement C5.53 only if the reduced sweep design is approved. The first implementation should be a parameterized experiment harness, not a new hardcoded policy winner. Do not tune parameters to make H1/H2 win; treat this as objective-sensitivity and Pareto-front exploration.
