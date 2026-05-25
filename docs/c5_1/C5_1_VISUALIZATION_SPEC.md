# C5_1_VISUALIZATION_SPEC.md

## Purpose

The C5.1 visualization is a simulation replay MVP.

It is not the final operator dashboard.

---

## Required Features

- mine node map
- truck movement replay
- Shovel / Crusher / PM Bay
- truck state colors
- selected policy display
- Daily Demand
- Completed Loads
- Demand Fulfillment
- Available Trucks
- PM Cost

---

## Truck State Colors

| State | Display |
|---|---|
| RUNNING | green |
| LOADING | blue |
| DUMPING | orange |
| PM | purple |
| STANDBY | gray |
| PM_DUE_SOON | yellow outline |
| UNAVAILABLE | red |

---

## Exclusions

Do not include:

- operator dashboard tabs
- PM app functions
- work order actions
- PPO/RL result screens
- detailed H1-H4 formulas
