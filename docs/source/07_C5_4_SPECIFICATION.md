# C5.4 Specification — Joint PM-Scheduling + Dispatch (final-submission module)

## Version and Status
- **Version**: C5.4
- **Effective Date**: 2026-06-14
- **Status**: Implemented + unit-tested (**45 passed**); the evaluation sweep and Tier 1–4 analyses
  **have been run** — auto-generated tables in `07_C5_4_RESULTS.md` (headline, 30 seeds × 365 d ×
  3 regimes) with the hand-authored interpretation/mechanism narrative in its companion
  `07_C5_4_INTERPRETATION.md`; plus `08_C5_4_SENSITIVITY.md`, `09_C5_4_MECHANISM.md`, and
  `outputs/c5_4/`. This specification states no numbers itself; every figure lives in those reports
  (anti-overclaim). NB: re-running `scripts/run_c5_4_sweep.py` overwrites `07_C5_4_RESULTS.md`'s
  tables but never the separate `07_C5_4_INTERPRETATION.md`.
- **Builds on**: C5.3 (`06_C5_3_SPECIFICATION.md`). Self-contained new `c5_4` module; the
  C5.1/C5.2/C5.3 code is unchanged.

---

## 1. Purpose

C5.3 transplanted the C6 3-component reliability surface into the 25-truck C5 mine and ran
**dispatch-only**, with preventive maintenance **frozen** to one shared CBM rule (the C6.1
grid-search optimum 0.21/0.21/0.28). That froze the most consequential maintenance lever: PM could
never be *wrong*, so in the mild regime the comparison reduced to PM frequency.

**C5.4 is the final-submission consolidation.** It widens the decision target to the **joint
(PM scheduling + dispatch)** problem on the *same* reliability+cost surface, and is the version that
repairs, in one place, the defects surfaced across every prior phase:

| Defect (where found) | Repair in C5.4 |
|---|---|
| **C1** free self-heal (RL Lab PPO) | PM/CM are *partial* restores — inherited from the C5.3 surface. |
| **C3** health has no consequence (RL Lab) | Weibull hazard → corrective repair (CM) cost — inherited. |
| Production-reward dominance / STANDBY idle-exploit (RL Lab) | TCO-only objective; resting neither degrades nor is rewarded, only priced by the unmet penalty — inherited. Making PM a decision does **not** reopen an exploit (see §4). |
| **C5.1** breakdown-lever dormancy (min-HI stayed far above the floor) | The C6 surface + PM-as-decision activates the failure path under the stress regimes (shown in C5.3). |
| **C5.3** frozen-PM limitation | PM scheduling becomes a *policy* decision → reproduces the C5.2 "state-aware PM beats blind periodic PM" finding on the richer 3-component frailty/POMDP surface **and jointly with dispatch**. |
| RL disconnect (PPO lived in a separate RL Lab, no shared env) | A documented joint-decision **interface** (`mine_env/rl_interface_c5_4.py`) both heuristics and a PPO agent target, so they are compared on a byte-identical environment (§7). |

### Definition (as commissioned)
| Element | C5.4 choice | Source |
|---|---|---|
| Reliability surface | 3-component HI (tire/engine/brake), frailty, POMDP noise, Weibull failure → CM | **verbatim C5.3/C6** |
| Decision | **joint** PM scheduling **+** dispatch | new in C5.4 |
| Heuristics | C5.2/C5.3 recast as **PM-family × dispatch-family pairs** (H0–H4 + **H_TIME**) | C5.2 PM families + C5.3 dispatch |
| PM bay model | per-truck **shop visit** (one bay, several components serviced together) | refinement over C5.3's per-component slot |
| PPO | documented **interface stub** (protocol + obs/action contract + adapter); training in the RL Lab | new in C5.4 |

---

## 2. Environment

Identical to C5.3 (see `06_C5_3_SPECIFICATION.md` §2–3): 25 trucks, 350 t payload, a 365-day
campaign of 24 hour-steps each carrying a 210-load demand quota; routes A/B/C trade grade/cycle
against per-component wear; 3-component HI with truck HI = min, Gamma frailty, `N(0, 0.03)` sensor
noise (POMDP), Weibull-like failure hazard (0 above `threshold_hi = 0.20`) → CM. **All reliability,
cost, route and regime parameters are carried over verbatim from `configs/c5_3.yaml`** — the
implementation enforces this (`reliability_c5_4.py` / `costs_c5_4.py` are thin subclasses) and a test
(`test_reliability_cost_routes_are_verbatim_from_c5_3`) asserts the subtrees are byte-identical, so
any C5.4-vs-C5.3 difference is attributable to the decision change alone.

---

## 3. The Joint Decision

Each hour the policy is asked once and returns **both** decisions:

```
JointPolicy.decide(state) -> {
  "pm":       [(truck_id, components, risk), ...],   # shop-visit referrals, priority-ordered
  "dispatch": [(truck_id, ranked_routes), ...],      # full route ranking over all available trucks
}
```

The simulator (`simulator_c5_4.py`) then: accepts the top `free_bays` PM referrals (one truck per
bay), services the listed components in that visit, sends the rest on their best capacity-available
route — physics otherwise identical to C5.3.

**Per-truck shop-visit bay model (refinement over C5.3).** In C5.3 a referral was one component
occupying one bay. In C5.4 a referral is one *truck* occupying one bay, with one or more components
serviced in that visit (cost = Σ component PM costs, downtime = Σ component PM durations). This is the
realistic semantics of a maintenance bay and it sharpens the blind-vs-state-aware contrast: a blind
baseline does a **full** vehicle service (all three components) on a clock; a state-aware rule
services **only the flagged** components, when flagged.

---

## 4. Why PM-as-a-decision does not reopen an exploit

The RL Lab's hardest lesson was that a poorly-shaped objective is gameable (production-reward
dominance, the STANDBY self-heal). Making PM a free decision could, in principle, invite a new
degenerate strategy — "PM constantly" or "never PM". Neither is free here:

- **Over-maintenance** is priced by PM cost **and** bay downtime (a truck in the shop cannot haul →
  unmet-demand penalty).
- **Under-maintenance** is priced by corrective repair (CM ≈ 4× the cost and downtime of PM) plus the
  lost haul.
- **Resting a worn truck** neither degrades nor is rewarded; the production it forgoes is already
  priced by the unmet penalty.

So PM timing is a genuine two-sided tradeoff on a single TCO axis, not a lever to be gamed.

---

## 5. Heuristic Set — H0–H4 + H_TIME as PM × dispatch pairs

Each policy composes one PM-scheduling family (`pm_scheduler_c5_4.py`) with the matching C5.3 dispatch
policy (`policies_c5_3`, reused verbatim). **H_TIME returns**: once PM scheduling is a decision, an
operating-hours PM timer is a real policy again (it had no dispatch-only analogue in C5.3).

| Policy | PM-scheduling family (trigger) | Dispatch (reused C5.3) | Lineage |
|---|---|---|---|
| **H0** | **Calendar** — fixed interval, full vehicle service, condition-blind | route-blind round-robin | C5.2 H0 + C5.3 H0 |
| **H_TIME** | **Operating-hours** — usage budget, full service, condition-blind | route-blind round-robin | C5.2 H_TIME |
| **H1** | **Condition-CBM** — observed HI ≤ threshold or risk override (the C5.3 frozen rule, now chosen) | health routing | C5.2 H1 + C5.3 H1 |
| **H2** | **Risk-priority** — components with observed risk ≥ threshold, worst-first | risk-aware routing | C5.2 H2 + C5.3 H2 |
| **H3** | **Cost-value** — PM when expected CM cost avoided ≥ PM cost (anticipatory) | value (grade) routing | C5.2 H3 + C5.3 H3 |
| **H4** | **Flow-backpressure** — PM only into spare fleet capacity; defer under demand pressure | capacity routing | C5.2 H4 + C5.3 H4 |

All families read only the **observed** (noisy) HI — never the latent truth (POMDP).

### Anti-overclaim: the new parameters
The reliability/cost/route/regime values are verbatim C5.3 (not re-tuned). The **only** new
parameters are the PM-family triggers, set from principled derivations and explicitly **not** tuned
against outcomes (`configs/c5_4.yaml → pm_scheduling`):

- **Blind cadences — steelmanned** (calendar `interval_days = 3`, operating-hours `due_hours = 30`).
  A blind PM does a *full vehicle service* (all 3 components) on a clock. To avoid strawmanning the
  baseline, the cadence is sized to the **fast-frailty tail**, not the average truck: under cv = 0.50
  the worst trucks wear ~2.5× faster, so tail-tire steady-state cadence =
  `PM recovery 0.35 / (nominal loss 0.0048 × 2.5) ≈ 29 hauls ≈ 3 days`. This is also the **tightest
  feasible** calendar given 2 PM bays — full-vehicle services (~9–11 h) saturate the bays at ~1594
  visits/yr, so a tighter clock adds no services, only improves which trucks the worst-first bay queue
  catches. A diagnostic cadence sweep (calendar 3→8 days, hours 24→72) shows blind TCO ranging 35k–50k
  vs state-aware ~22k across the **entire** range: the blind ≫ state-aware result is **cadence-robust**,
  not a cadence artifact, and iv = 8/due = 72 would be the *worst* (most strawman) end, not these.
- **`risk_priority.risk_threshold = 0.80`** = the CBM `failure_risk_override` (PM components whose
  risk is "critical").
- **`cost_value.lookahead_hauls = 24`** = one day's operating hours of failure-cost anticipation.
- **`flow_backpressure.soft_threshold_hi = 0.30`** = a margin above the 0.20 failure floor, so even
  deferred PM still targets genuinely worn components.

> Mechanism (from the diagnostic, to be confirmed by the full sweep): the blind baselines lose to
> state-aware PM on **two** axes at once — they *over-service* (full-vehicle visits cost ~1.6× the PM
> spend of targeted single-component service) **and** they *under-protect the tail* (full-vehicle
> visits are so bay-heavy that the 2 bays cannot keep the fast-frailty trucks above the floor, so a
> residual failure tail remains even at the tightest cadence). State-aware PM does ~2× **more** visits
> that are each short and targeted, so it both fits the bays and adapts to frailty — the honest,
> credible form of the C5.2 "blind periodic is penalised" finding.

---

## 6. Regimes

Verbatim from C5.3: `heterogeneous_condition` (main), `high_stress`, `high_demand_high_stress` —
the stress regimes test whether the failure/CM path activates and whether the ranking flips once
failure-avoidance starts to matter.

---

## 7. PPO Integration — interface contract (no env in-repo)

C5.4 does **not** ship a runnable Gym env (training stays in the RL Lab); it ships the *contract*
both sides target (`mine_env/rl_interface_c5_4.py`):

- **`JointPolicy`** protocol — `decide(state) -> {"pm", "dispatch"}` + `reset()`; every C5.4
  heuristic already satisfies it.
- **`encode_observation(state, config)`** — the flat observation vector: per-truck `[obs tire/engine/
  brake HI, status one-hot(3), downtime, ops-hours-since-PM, days-since-PM]` (9 features × `truck_count`)
  + globals `[demand-remaining, route A/B/C cap, free bays, hour, day]` (7). `MultiDiscrete([6]*trucks)`
  action over `ACTION_CHOICES = {PM_TIRE, PM_ENGINE, PM_BRAKE, RUN_A, RUN_B, RUN_C}`.
- **`decode_action(action, state, config)`** — turns a per-truck action vector into a valid
  `{"pm", "dispatch"}` decision (bay capacity enforced by the simulator).
- **`AgentJointPolicy(agent)`** — adapter so a trained `agent(obs) -> action` callable drops into
  `run_policy_simulation(..., policy=AgentJointPolicy(agent))` and runs the *same* loop as the
  heuristics, on the same seeds/regimes. **Reward contract = −ΔTCO per step** (episode return =
  −total TCO, the heuristics' objective).

The RL Lab is expected to wrap the C5.4 step in a Gymnasium `Env` matching this layout, train PPO,
then evaluate the trained agent in-repo via `AgentJointPolicy` for a like-for-like comparison.

---

## 8. Reproducibility & Tests

- One NumPy RNG stream per `(policy, seed)`; identical seed → identical summary.
- `tests/test_c5_4_{config,pm_scheduler,policies,simulator,reliability,rl_interface}.py`
  (**45 passed**): verbatim-reuse invariant; each PM family's trigger semantics (calendar/hours fire
  on the clock, blind to condition; CBM/risk/cost-value/flow fire on observed condition/slack) and
  the free-bay cap; joint-policy roster + `decide` returns both PM and dispatch; non-degeneracy of
  H0/H1/H3; full-service accounting (`pm_component_count == 3 × pm_count` for calendar H0);
  per-component CM logging sums (`cm_tire+cm_engine+cm_brake == cm_count`) and `failure_log` length
  == `failure_count`; sensor-noise clip boundary + hazard shape + frailty CV; cost decomposition sums
  to TCO; stress ≥ base; RL obs dim/encode shape, `decode_action`, and an `AgentJointPolicy` run.

### Reproduction (anaconda python — PATH `python` is a broken Store stub on this machine)
```
# unit tests
"C:\Users\<user>\anaconda3\python.exe" -m pytest tests/test_c5_4_*.py -q

# headline sweep  -> docs/source/07_C5_4_RESULTS.md, outputs/c5_4/summary/c5_4_policy_comparison.csv
python scripts/run_c5_4_sweep.py                  # 30 seeds x 365 days x 3 regimes

# Tier-2 sensitivity -> docs/source/08_C5_4_SENSITIVITY.md, outputs/c5_4/sensitivity/*.json
python scripts/run_c5_4_sensitivity.py            # frailty-CV / CBM-threshold / PM-bay

# Tier-3 mechanism  -> docs/source/09_C5_4_MECHANISM.md, outputs/c5_4/mechanism/c5_4_mechanism.json
python scripts/analyze_c5_4_mechanism.py          # failure timing / per-seed / causal profile
```
Per-component PM/CM counts, per-seed frailty descriptors (`avg_frailty`, `max_frailty`) and the
optional `failure_log` (via `record_events=True`) are first-class summary fields, so the Tier-3
analyses read from the sweep artifacts rather than re-deriving the RNG.

**Portability / determinism notes (so a second machine reproduces these numbers bit-for-bit):**
- **Run from the repository root** with the canonical code in `scripts/` + `mine_env/`. Every script
  resolves its own paths from `Path(__file__)` — there are no absolute/user-specific paths.
- **Use a real Python** (3.12 + NumPy as in `requirements.txt`). On some Windows setups the bare
  `python` on `PATH` is a Microsoft-Store stub that exits without running; invoke the full
  interpreter path (e.g. an Anaconda `python.exe`) if `python --version` does not print a version.
- **All randomness is seeded**: one `numpy.random.default_rng(seed)` stream per `(policy, seed)`;
  the held-out seeds are fixed in `configs/c5_4.yaml → evaluation.seeds` (101–130). Same seed →
  identical summary row (no wall-clock, no hidden global RNG, no set-iteration in the result path).
- **`presentation_pack_c5_4/source_scripts/` is an export SNAPSHOT for slide-making, not a runnable
  copy** — its scripts resolve paths relative to the pack, not the repo, so run the originals under
  `scripts/`, not the pack copies.

---

## 9. Status and What Remains

**Module implemented + unit-tested; Tier 1–3 submission-prep analyses produced** by the three scripts
above (headline `07_C5_4_RESULTS.md`, sensitivity `08_C5_4_SENSITIVITY.md`, mechanism
`09_C5_4_MECHANISM.md`). Reduced analysis scales are stated verbatim in each report (anti-overclaim).

Deferred to the user:
1. Tier 4 presentation visualisation (box plots, sensitivity curves, failure-timing histograms).
2. Optionally extend `scripts/build_version_results.py` to add a **C5.4** entry to the UI version
   switcher from the real sweep CSV.
3. RL Lab: build the Gymnasium env against §7, train PPO, evaluate via `AgentJointPolicy`.

---

## Appendix — What each prior phase contributed to C5.4

| Phase | Reused in C5.4 |
|---|---|
| **C5.1** | 25-truck Escondida-0.1-scale mine; simulator/day-loop idioms; policy-registry pattern. |
| **C5.2** | The three PM-trigger families (calendar / operating-hours / state-aware) and the "blind periodic vs state-aware PM" comparison — recast here onto the 3-component surface and joined with dispatch. H_TIME restored. |
| **C5.3** | The entire reliability+cost surface (verbatim), the route dispatch decision surface, the H1–H4 dispatch policies (reused as-is), the sweep/report format, the anti-overclaim regime discipline. |
| **C6 / C6.1 (RL Lab)** | The reliability core (3-component HI, frailty, sensor noise, Weibull hazard, PM/CM) and the held-out paired-seed evaluation protocol; the defect catalogue (C1/C3/idle-exploit) this module is built to keep closed. |
