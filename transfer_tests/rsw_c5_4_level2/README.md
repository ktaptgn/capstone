# RSW C5.4 Level 2 Mini Transfer Simulation

## Purpose

This folder defines a reduced-scale synthetic transfer test that reconstructs the C5.4 joint
preventive-maintenance scheduling and dispatch structure in a resistance spot welding (RSW)
setting.

This RSW simulation is a synthetic Level 2 transfer mini-test. It is not a real factory
validation. Its purpose is to reconstruct the C5.4 joint PM scheduling + dispatch structure in a
manufacturing RSW setting.

RSW 미니 시뮬레이션은 본 프로젝트의 메인 실험이 아니라 제조업 전이 가능성을 보여주는
보조 실험이다. C5.4의 truck/component/route/PM bay 구조를 RSW의 welding
gun/component/job family/maintenance slot 구조로 재구성했다. 실제 현장 적용을 위해서는
용접 로그, 전극 dressing 이력, 품질 검사 데이터로 파라미터 보정이 필요하다.

The mining C5.4 experiment remains the main project. This folder must not be presented as a real
factory model, a calibrated automotive process, or a replacement for the C5.4 mining result.

## Problem Definition

In an automotive-body RSW process, welding guns repeatedly produce welds while the electrode tip,
cooling unit, and actuator/clamp system degrade. Continued production increases completed welds
but also increases wear and defect/failure risk. Excessive preventive maintenance reduces risk
but consumes maintenance slots, creates downtime, and can increase unmet demand. The joint
decision is therefore which guns to assign to product/job families and which guns/components to
send to preventive maintenance, using noisy observed component health, gun-specific frailty,
production demand, and limited maintenance-slot capacity.

## C5.4-to-RSW Mapping

| C5.4 Mining | RSW Mini Transfer |
| --- | --- |
| Truck | RSW welding gun / welding cell |
| Tire HI | Electrode tip HI |
| Engine HI | Cooling / power supply HI |
| Brake HI | Actuator / clamp mechanism HI |
| Route A/B/C | Product/job family A/B/C |
| Route severity | Weld job severity |
| Dispatch | Production assignment to job family |
| PM bay | Maintenance / dressing slot |
| PM shop visit | Gun-level maintenance visit |
| Full vehicle service | Full gun service |
| Targeted component PM | Tip dressing / cooling maintenance / actuator maintenance |
| CM | Corrective repair after a failure event |
| Frailty | Gun-specific wear heterogeneity |
| Sensor noise | Noisy observed condition signal |
| Unmet demand | Uncompleted weld target |
| TCO | PM + CM + downtime + degradation + unmet demand + defect cost |

## Scope

Included:

- 10 synthetic RSW guns with three component health indices
- Gamma-distributed gun/component frailty and noisy observed HI
- Joint PM scheduling and job-family production assignment
- H0-H4 plus H_TIME under identical regimes, seeds, demand, and KPI definitions
- Reduced default run of 30 days and 10 seeds
- KPI, event, failure, mechanism, sensitivity, Excel, Markdown, and PNG outputs

Excluded:

- Real factory validation or claims about real automotive factory values
- PPO/RL training
- Operator dashboard or PM application
- Mining-model replacement
- Use of legacy C5/C5.1/PPO results as the RSW source of truth

## Fixed Step 1 Contracts

These contracts close details that were not fully specified in the task prompt. They are synthetic,
config-driven assumptions and must remain visible in generated reports.

### Demand allocation

- Daily demand is 210 completed welds.
- Base job-family demand is split equally: A = 70, B = 70, C = 70 welds/day.
- A regime demand factor scales each family target proportionally.
- Production assignments stop contributing completed welds after that job family's daily target is
  met. This prevents policies from satisfying demand only with the easiest family.

### Blind PM cadence

- H0 calendar full-service interval: 3 days.
- H_TIME operating-hours full-service threshold: 30 production hours.
- These values transfer the steelmanned C5.4 blind-baseline cadence into the mini-test; they are not
  claimed as real RSW maintenance standards.

### Defect and failure semantics

- A defect is a synthetic quality event sampled after production from component-condition risk. It
  adds `defect_event_cost` but does not automatically trigger CM or downtime.
- A failure is a component reliability event sampled after production. It triggers component CM,
  corrective cost, downtime, partial restoration, and a failure-log record.
- Defect and failure events are tracked separately. A production attempt that fails does not count
  as a completed weld.

### Downtime and multi-component visits

- Downtime is priced at `1.0 synthetic_CU` per gun-hour.
- One accepted PM referral occupies one maintenance slot for one gun.
- A visit may service one or more components.
- Multi-component PM duration is the sum of component PM durations.
- Multi-component CM duration is the maximum failed-component CM duration because corrective jobs
  are assumed to proceed in parallel during the same gun outage.

### Restoration

- PM and CM use additive partial restoration with per-component caps.
- No maintenance action restores a component to 1.0.

## Joint Decision Contract

Each simulation hour, a policy returns both maintenance referrals and production rankings:

```python
class JointPolicy:
    def reset(self):
        ...

    def decide(self, state) -> dict:
        return {
            "pm": [
                # (gun_id, components, risk_score)
            ],
            "dispatch": [
                # (gun_id, ranked_job_families)
            ],
        }
```

The simulator will:

1. Observe noisy component HI.
2. Request one joint policy decision.
3. Accept priority-ordered PM referrals up to free maintenance-slot capacity.
4. Exclude accepted PM guns from production for that hour.
5. Assign remaining guns to ranked job families with remaining demand.
6. Apply weld completion, wear, defect/failure sampling, cost, and logs.

Policies may read observed HI but must never read latent true HI.

## Policy Families

| Policy | PM scheduling | Production assignment |
| --- | --- | --- |
| H0 | Calendar full gun service | Condition-blind round-robin |
| H_TIME | Operating-hours full gun service | Condition-blind round-robin |
| H1 | Component CBM threshold / critical override | Health-aware severity routing |
| H2 | Worst-first component risk | Risk-aware routing |
| H3 | Expected CM cost avoided versus PM cost | Value and expected-risk routing |
| H4 | Backpressure PM with critical safety override | Remaining-demand and capacity routing |

The six Step 3 policy implementations live in `rsw_policies.py`. They share the same
`JointPolicy.decide(state) -> {"pm", "dispatch"}` contract. State-aware policies access only
`observed_<component>_hi` and `observed_gun_hi`; latent true HI and frailty are not policy inputs.
Policy decisions are implemented, but full episode execution and policy sweeps remain deferred to
the approved Step 4.

## Configuration

All Step 1 contracts and simulation parameters are defined in
`rsw_c5_4_config.yaml`. Future implementation steps should not duplicate these values as hardcoded
constants.

The default run is:

```text
10 guns x 2 maintenance slots x 30 days x 10 seeds x 3 regimes x 6 policies
```

The optional full run is 365 days x 30 seeds and must not be treated as the default mini-test.

## Current Step 2 Execution

The core environment, reliability, maintenance, cost, and logging surface is implemented. Step 2
supports a short smoke run only:

```bash
python transfer_tests/rsw_c5_4_level2/rsw_c5_4_mini_sim.py --smoke --days 2 --seed 101
```

The smoke runner uses a fixed non-policy schedule to exercise one targeted PM visit, one full PM
visit, production wear, demand fulfillment, downtime, TCO decomposition, and event/failure log
structures. It does not invoke or compare H0-H4/H_TIME.

## Current Step 3 Policy Status

`rsw_policies.py` implements the common JointPolicy contract and H0/H_TIME/H1/H2/H3/H4 decision
families. Step 3 validates policy decisions against constructed states only. The core smoke runner
still uses its fixed non-policy schedule, and no multi-policy episode sweep or ranking is produced
until Step 4.

## Current Step 4 Sweep

The policies are integrated into the shared episode loop. The approved reduced-scale sweep runs
all six policies under all three regimes using the same 10 seeds and 30-day horizon:

```bash
python transfer_tests/rsw_c5_4_level2/rsw_c5_4_mini_sim.py --sweep
```

Step 4 writes only the policy summary, event log, and failure log CSV files. Sensitivity, Excel,
Markdown report, and PNG generation remain deferred.

## Current Step 5 Analysis

Mechanism and the three approved sensitivity analyses are implemented in `rsw_analysis.py`:

```bash
python transfer_tests/rsw_c5_4_level2/rsw_analysis.py
```

The analysis covers failure timing, component PM/CM share, job-family mix, max-frailty/failure
correlation, blind versus state-aware behavior, frailty CV, H1 CBM threshold, and maintenance-slot
count. Excel, the final report, and PNG remain deferred to Step 6.

## Current Step 6 Deliverables

The Excel workbook, final Markdown report, and presentation PNG are generated from the reviewed
Step 4/5 CSV outputs:

```bash
python transfer_tests/rsw_c5_4_level2/rsw_outputs.py
```

These deliverables retain actual mini-test results and include explicit synthetic-transfer and
not-real-factory-validation statements.

## Optional Sanity Improvement Runs

These optional runs preserve the original 30-day base result. They are synthetic sanity checks,
not real factory validation, and their results were not tuned to reproduce the C5.4 mining
ranking.

### Demand Pressure Stress Run

Purpose:
The base 30-day run has large demand slack, so all policies reach fulfillment = 1.000. This
optional run raises daily demand to expose PM-production trade-off and unmet-demand behavior.

Command:

```bash
python transfer_tests/rsw_c5_4_level2/rsw_c5_4_mini_sim.py --demand-stress
```

Outputs:
`outputs/stress/`

Actual result:
H3 had the lowest TCO. Mean unmet demand appeared only for H_TIME (`1.5` welds/run;
fulfillment `0.999971`), so most policies still retained substantial production slack. H4 was
second by TCO; no ranking was forced.

### 90-Day Horizon Sanity Run

Purpose:
The base 30-day run has sparse failure events. This optional run extends the horizon to 90 days to
check whether failure/CM paths become more visible.

Command:

```bash
python transfer_tests/rsw_c5_4_level2/rsw_c5_4_mini_sim.py --horizon-sanity-90
```

Outputs:
`outputs/horizon_90/`

Actual result:
Failure/CM mean totals increased from `1.2` in the 30-day base summary to `2.8` in the 90-day
summary and remained concentrated in H_TIME. H4 had the lowest TCO under heterogeneous condition
and high demand + high stress; H3 was lowest under high stress. H1-H4 retained component-targeted
PM.

### Sanity Reports And Plots

After both optional runs:

```bash
python transfer_tests/rsw_c5_4_level2/rsw_sanity_outputs.py
```

This generates the two scenario reports, two presentation PNGs, and
`outputs/rsw_c5_4_sanity_improvement_report.md`.

Recommended complete execution order:

```bash
# Existing base run and deliverables
python transfer_tests/rsw_c5_4_level2/rsw_c5_4_mini_sim.py --sweep
python transfer_tests/rsw_c5_4_level2/rsw_analysis.py
python transfer_tests/rsw_c5_4_level2/rsw_outputs.py

# Optional sanity runs and deliverables
python transfer_tests/rsw_c5_4_level2/rsw_c5_4_mini_sim.py --demand-stress
python transfer_tests/rsw_c5_4_level2/rsw_c5_4_mini_sim.py --horizon-sanity-90
python transfer_tests/rsw_c5_4_level2/rsw_sanity_outputs.py
```

Important:
These runs do not replace the base mini-test and are not real factory validation. The demand
stress exposed only a limited unmet-demand path, and failures remained sparse even at 90 days.

## Outputs

```text
outputs/
  rsw_c5_4_policy_summary.csv
  rsw_c5_4_policy_summary.xlsx
  rsw_c5_4_event_log.csv
  rsw_c5_4_failure_log.csv
  rsw_c5_4_sensitivity.csv
  rsw_c5_4_sensitivity.md
  rsw_c5_4_policy_comparison.png
  rsw_c5_4_report.md
  rsw_c5_4_sanity_improvement_report.md
  stress/
    rsw_c5_4_demand_stress_policy_summary.csv
    rsw_c5_4_demand_stress_event_log.csv
    rsw_c5_4_demand_stress_failure_log.csv
    rsw_c5_4_demand_stress_report.md
    rsw_c5_4_demand_stress_plot.png
  horizon_90/
    rsw_c5_4_90day_policy_summary.csv
    rsw_c5_4_90day_event_log.csv
    rsw_c5_4_90day_failure_log.csv
    rsw_c5_4_90day_report.md
    rsw_c5_4_90day_plot.png
```

All reports prioritize actual simulation results over expected policy behavior.
