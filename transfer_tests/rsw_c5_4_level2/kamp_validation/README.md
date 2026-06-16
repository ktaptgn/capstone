# KAMP Welding Dataset Partial Recheck

## Purpose

Use the KAMP welding dataset as a partial external-data sanity check for the RSW mini-test's
synthetic defect-risk proxy. This is not real factory validation.

## Dataset files

- `data/kamp_welding/Welding Data Set_01.xlsx`
- `data/kamp_welding/scaled_data.csv`

## What the dataset can support

- Audit of per-weld force, current, voltage, and weld-time process logs.
- Daily aggregate defect-rate description where raw and result dates match.
- Suggested-only calibration of the synthetic RSW defect hazard.

## What the dataset cannot support

- PM scheduling validation
- Tip dressing timing validation
- Maintenance slot or downtime validation
- Electrode wear or component-HI calibration
- Per-weld supervised defect prediction from the provided aggregate result sheet

## How defect-risk calibration is performed

The result sheet is treated as daily/defect-type aggregate counts. The matched-day weighted defect
rate is multiplied by 10 and capped at `0.08`; the existing RSW `p_max` is retained as a conservative
lower bound. Existing center HI, slope, and job-severity settings remain unchanged. Because the
label is aggregate and only eight dates match, the recommendation is marked `suggested_only`.

## How to run

```bash
python transfer_tests/rsw_c5_4_level2/kamp_validation/kamp_welding_profile.py
python transfer_tests/rsw_c5_4_level2/kamp_validation/kamp_defect_calibration.py
python transfer_tests/rsw_c5_4_level2/kamp_validation/kamp_rsw_recheck.py
pytest tests/test_rsw_kamp_validation.py -q
```

## Outputs

All outputs are written under `kamp_validation/outputs/` so existing RSW base and sanity outputs are
not overwritten.

## Limitations

The result sheet does not provide a reliable per-weld defect label. PM history, tip dressing
history, maintenance slots, downtime, and electrode wear measurements are absent.

## Presentation-safe interpretation

KAMP welding data can support defect-risk calibration, not PM scheduling validation.

The KAMP dataset provides a manufacturing-data-based quality-risk proxy only. It does not turn the
synthetic RSW mini-test into real factory validation.
