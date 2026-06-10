# C5_COST_AND_DEMAND_MODEL_v2.md

## Purpose

This document defines the C5.1 cost and demand model.

C5.1 does not replicate actual mine accounting.  
It uses normalized internal cost for policy comparison and report-level real-value conversion for interpretation.

---

## Core Principle

```text
Internal simulation: normalized cost unit
Presentation/report: real-value converted proxy
```

---

## Objective

```text
Minimize:
PM cost
+ downtime cost
+ unmet demand penalty
+ degradation cost
+ queue/idle loss
```

Subject to:

```text
Given demand should be satisfied as much as possible.
```

---

## Cost Groups

### 1. Runtime Fixed Cost

Used for reporting context. Not directly optimized in C5.1.

- personnel
- royalty
- fixed transport/logistics assumption

### 2. Controllable Variable Cost

Primary C5.1 optimization target.

- PM material cost
- PM labor/time proxy
- consumables
- downtime loss
- unmet demand penalty
- degradation cost

### 3. Year-End Accounting Cost

Handled as reporting-level summary, not per-event simulation cost.

- depreciation
- impairment
- miscellaneous

### 4. Excluded by Default

- outsourcing
- financial expenses
- shareholder distribution
- full corporate-level OPEX replication

---

## Demand Model

C5.1 uses configurable demand scenarios.

```yaml
demand:
  mode: daily
  base_daily_loads: 100
  variability: 0.15
  scenario: normal
```

Recommended scenarios:

| Scenario | Purpose |
|---|---|
| normal | Basic comparison |
| high_demand | Tests production pressure |
| pm_bottleneck | Tests PM bay pressure |
| rough_road | Tests degradation-aware decisions |

---

## Production Formula

```text
copper_output = ore_ton * grade
```

Post-crusher recovery rate and downstream processing are excluded for C5.1.
