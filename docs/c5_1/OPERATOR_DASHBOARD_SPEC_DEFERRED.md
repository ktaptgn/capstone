# OPERATOR_DASHBOARD_SPEC_DEFERRED.md

## Status

Activated by separate user instruction on 2026-05-25 as an imported UI draft.

## Planned Role

The operator dashboard will be a control tower for policy comparison, schedule review, KPI monitoring, and PM instruction generation.

## C5.1 Boundary

The dashboard is a result consumption layer. It reads generated C5.1 summary, log, and work order snapshots from `public/c5_1/`.

It must not run the C5.1 simulation, duplicate H0-H4 policy logic, add RL training, or implement Drop Zone scenarios.
