# KAMP Welding Dataset Profile

## Dataset structure

| sheet | rows | columns | missing | duplicates |
|---|---:|---:|---:|---:|
| Raw data | 11939 | 10 | 0 | 0 |
| result | 23 | 7 | 20 | 0 |
| data set | 10 | 3 | 0 | 0 |

- Scaled CSV: 11939 rows x 5 columns, encoding `cp949`.
- Scaled CSV row count matches raw data: `True`.
- Scaled CSV missing values: 71; label column present: `False`.
- The dataset contains per-weld process-variable logs for force, current, voltage, and weld time.

## Raw process-log coverage

- Date range: 2020-03-24 to 2020-04-07 (9 unique dates).
- Machine_Name unique count: 1.
- Item No unique count: 1.

| variable | mean | std | min | max |
|---|---:|---:|---:|---:|
| force | 2.787925 | 1.455966 | 1.740000 | 10.540000 |
| current | 14.711208 | 0.099000 | 14.520000 | 15.070000 |
| voltage | 2.704223 | 0.024700 | 2.464000 | 2.861000 |
| weld_time | 71.724123 | 0.632049 | 70.000000 | 73.000000 |

## Result sheet structure

- Rows: 23; total reported defect count: 39; defect types: 3.
- Result `idx` values are result-row sequence values. Although they overlap the first raw row indices, each result row contains a defect count and defect type, so this is not a one-to-one per-weld label.

## Label granularity decision

- Declared granularity: **daily_aggregate**
- Reason: Result rows are date/defect-type counts; no key maps each raw weld to one defect label.
- The result sheet is interpreted as date/type aggregate defect counts, not per-weld labels.
- Per-weld supervised defect prediction is therefore not supported.
- Daily rows with matched defect counts: 8 of 9.

## Supported use

- Descriptive daily defect-rate estimation.
- Suggested-only calibration of the RSW synthetic defect-risk proxy.

## Not supported

- PM scheduling validation
- Tip dressing timing validation
- Maintenance slot validation
- Downtime validation
- Electrode wear or HI calibration
- The dataset does not include PM history, tip dressing history, maintenance slots, or downtime.

This is not real factory validation. The KAMP data can only support a partial external-data quality-risk recheck.
