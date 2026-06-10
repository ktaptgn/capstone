# C5_1_LOG_SCHEMA.md

## Purpose

C5.1 logs are the data contract between the simulation, policy comparison, visualization MVP, and future dashboard/app.

---

## Required Fields

```json
{
  "time": "day/hour",
  "policy_id": "H1",
  "truck_id": "T07",
  "truck_state": "RUNNING | LOADING | HAULING | DUMPING | PM | STANDBY",
  "location": "Shovel A | Crusher 1 | PM Bay | Road",
  "destination": "Crusher 1",
  "action": "RUN | STANDBY | PM_TIRE | PM_VEHICLE",
  "reason_code": "PM_DUE_SOON",
  "payload_ton": 350,
  "ore_grade": 0.008,
  "produced_copper": 2.8,
  "truck_hi": 0.72,
  "tire_hi": 0.64,
  "pm_due_hours": 12,
  "pm_cost": 0.0,
  "downtime_hours": 0,
  "daily_demand": 100,
  "completed_loads": 64,
  "available_trucks": 18,
  "queue_time": 14,
  "total_cost": 0.0
}
```

---

## Output Folder

```text
outputs/c5_1/logs/
```
