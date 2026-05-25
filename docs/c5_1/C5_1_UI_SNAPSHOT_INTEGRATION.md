# C5.1 UI Snapshot Integration

## Purpose

The imported operator dashboard and PM worker app consume generated C5.1 result files without running the simulation.

## Data Flow

```text
policy sweep
-> outputs/c5_1/logs/*.json
-> outputs/c5_1/summary/policy_comparison.json
-> export_work_orders.py
-> outputs/c5_1/work_orders/*.json
-> export_ui_snapshots.py
-> ui/*/public/c5_1/*.json
-> UI apps load snapshots with mock fallback
```

## Boundaries

- The UI layer reads C5.1 outputs only.
- The UI layer does not run policy sweep, cost calculation, or maintenance scheduling logic.
- RL training files and Drop Zone scenarios remain outside this official UI import.
