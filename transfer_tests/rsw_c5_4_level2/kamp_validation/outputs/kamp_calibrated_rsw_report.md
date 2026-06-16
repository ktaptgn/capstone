# KAMP-Calibrated RSW Partial Recheck Report

This is a partial external-data recheck using the KAMP welding dataset. It calibrates only the defect-risk proxy of the RSW mini-test. It does not validate PM scheduling, tip dressing timing, maintenance slots, downtime, or electrode wear HI.

KAMP 용접기 AI 데이터셋은 RSW mini-test의 defect-risk proxy를 보정하는 데만 사용했다. 이 데이터에는 전극 마모량, tip dressing 이력, 정비 downtime, maintenance slot 정보가 없기 때문에 PM scheduling 자체를 실제 데이터로 검증한 것으로 해석하면 안 된다.

This remains a synthetic transfer mini-test and is not real factory validation.

## Calibration scope

- Label granularity: `daily_aggregate`
- Calibration status: `suggested_only`
- Matched days: 8
- Weighted defect rate: 0.00378972
- Existing p_max: 0.06
- Suggested p_max: 0.06
- Center HI, slope, job severity, PM scheduling, maintenance capacity, downtime, and HI physics remain unchanged.

## KAMP-calibrated RSW result

| regime | best policy | TCO | defect mean | defect cost | fulfillment |
|---|---|---:|---:|---:|---:|
| heterogeneous_condition | H3 | 77.943 | 4.100 | 32.800 | 1.000000 |
| high_demand_high_stress | H4 | 126.178 | 4.100 | 32.800 | 1.000000 |
| high_stress | H3 | 112.002 | 4.300 | 34.400 | 1.000000 |

## Base versus KAMP-calibrated ranking

| regime | base ranking | KAMP-calibrated ranking | changed? |
|---|---|---|---|
| heterogeneous_condition | H3 < H1 < H4 < H2 < H_TIME < H0 | H3 < H1 < H4 < H2 < H_TIME < H0 | False |
| high_stress | H3 < H4 < H2 < H1 < H_TIME < H0 | H3 < H4 < H2 < H1 < H_TIME < H0 | False |
| high_demand_high_stress | H4 < H3 < H1 < H2 < H_TIME < H0 | H4 < H3 < H1 < H2 < H_TIME < H0 | False |

## Interpretation

- Maximum absolute TCO mean change: 0.000000 synthetic CU.
- Maximum absolute defect mean change: 0.000000.
- The suggested p_max did not exceed the existing conservative p_max lower bound, so the recheck preserves the base defect hazard and ranking.
- This does not mean KAMP calibration failed. It means this aggregate quality proxy does not justify a stronger defect hazard than the existing synthetic setting.
- RSW policy ranking remains primarily driven by PM and downtime structure, which KAMP does not validate.

## Limitations

- Result labels are daily/type aggregate counts, not per-weld labels.
- Only 8 days have matched defect counts; one raw-data day has no result row and was not assumed to have zero defects.
- The recheck cannot validate PM scheduling, tip dressing timing, maintenance slots, downtime, or electrode wear HI.
- Results are reported as-is without tuning policy rankings.
