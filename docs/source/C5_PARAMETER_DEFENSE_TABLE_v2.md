# C5_PARAMETER_DEFENSE_TABLE_v2.md

## Purpose

This table separates fixed C5.1 parameters, proxy assumptions, and deferred items.

---

## Fixed C5.1 Parameters

| Parameter | C5.1 Value | Status | Reason |
|---|---:|---|---|
| simulation_method | DES | Fixed | Event-based truck operation |
| mine_scale | 0.1 | Proxy | Simplified virtual mine |
| truck_avg_payload_ton | 350 | Proxy | Simplified average payload |
| crusher_count | 2 | Fixed | Current C5 environment |
| use_recovery_rate | false | Fixed | Excluded to reduce process complexity |
| use_post_crusher_process | false | Fixed | C5.1 focuses on transport and PM |
| use_drop_zone | false | Fixed default | Deferred scenario |
| rl_enabled | false | Fixed default | RL deferred |
| dashboard_enabled | false | Fixed default | Deferred until separate instruction |
| pm_app_enabled | false | Fixed default | Deferred until separate instruction |

---

## Policy Parameters

| Parameter | Value |
|---|---|
| policy_set | H0, H1, H2, H3, H4 |
| comparison_rule | same environment, same seed, same demand |
| output | logs, KPI summary, visualization replay |

---

## Cost Parameters

| Group | C5.1 Treatment |
|---|---|
| PM cost | controllable variable cost |
| downtime cost | controllable operating loss |
| unmet demand penalty | core objective penalty |
| depreciation/impairment | year-end accounting summary |
| outsourcing | excluded by default |
| royalty/personnel | fixed reporting context |

---

## Deferred Parameters

| Parameter | Reason |
|---|---|
| drop_zone_capacity | Drop Zone scenario deferred |
| drop_zone_construction_cost | Drop Zone scenario deferred |
| PM workforce scheduling | Outside current scope |
| PPO hyperparameters | RL deferred |
| dashboard feature flags | Deferred |
| app feature flags | Deferred |
