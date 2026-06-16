from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RSW_ROOT = ROOT / "transfer_tests" / "rsw_c5_4_level2"
KAMP_ROOT = RSW_ROOT / "kamp_validation"
OUTPUT_DIR = KAMP_ROOT / "outputs"


def _load(name: str):
    path = KAMP_ROOT / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(KAMP_ROOT))
    sys.path.insert(0, str(RSW_ROOT))
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_kamp_profile_outputs_created():
    for name in (
        "kamp_dataset_profile.csv",
        "kamp_dataset_profile.md",
        "kamp_daily_quality_summary.csv",
    ):
        path = OUTPUT_DIR / name
        assert path.exists()
        assert path.stat().st_size > 0


def test_kamp_label_granularity_is_declared():
    calibration = json.loads((OUTPUT_DIR / "kamp_defect_calibration.json").read_text(encoding="utf-8"))
    assert calibration["label_granularity"] == "daily_aggregate"
    assert calibration["calibration_status"] == "suggested_only"
    assert calibration["matched_day_count"] == 8
    assert calibration["unmatched_raw_day_count"] == 1


def test_kamp_calibration_does_not_claim_pm_validation():
    calibration = json.loads((OUTPUT_DIR / "kamp_defect_calibration.json").read_text(encoding="utf-8"))
    unsupported = " | ".join(calibration["not_supported"]).lower()
    assert calibration["usage"] == "defect_hazard_calibration_only"
    assert "pm scheduling validation" in unsupported
    assert "tip dressing timing validation" in unsupported
    readme = (KAMP_ROOT / "README.md").read_text(encoding="utf-8")
    assert "KAMP welding data can support defect-risk calibration, not PM scheduling validation." in readme


def test_kamp_recheck_outputs_do_not_overwrite_base():
    base_files = [
        RSW_ROOT / "outputs" / "rsw_c5_4_policy_summary.csv",
        RSW_ROOT / "outputs" / "rsw_c5_4_event_log.csv",
        RSW_ROOT / "outputs" / "rsw_c5_4_failure_log.csv",
    ]
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in base_files}
    assert (OUTPUT_DIR / "kamp_calibrated_rsw_summary.csv").resolve().parent == OUTPUT_DIR.resolve()
    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in base_files}
    assert before == after


def test_kamp_override_changes_only_defect_hazard():
    recheck = _load("kamp_rsw_recheck")
    calibration = recheck.load_calibration()
    config = recheck.load_config(regime="high_stress")
    updated = recheck.apply_defect_hazard_only(config, calibration)
    original_hazard = config["reliability"]["defect_hazard"]
    updated_hazard = updated["reliability"]["defect_hazard"]
    config_without_hazard = json.loads(json.dumps(config))
    updated_without_hazard = json.loads(json.dumps(updated))
    del config_without_hazard["reliability"]["defect_hazard"]
    del updated_without_hazard["reliability"]["defect_hazard"]
    assert config_without_hazard == updated_without_hazard
    assert set(updated_hazard) == set(original_hazard)


def test_kamp_summary_has_required_columns():
    summary = pd.read_csv(OUTPUT_DIR / "kamp_calibrated_rsw_summary.csv")
    required = {
        "scenario",
        "regime",
        "policy",
        "seed_count",
        "TCO_mean",
        "TCO_std",
        "defect_mean",
        "defect_cost_mean",
        "PMvisits_mean",
        "CM_mean",
        "failure_mean",
        "fulfillment_mean",
        "completed_welds_mean",
        "unmet_welds_mean",
        "downtime_hours_mean",
        "endHI_mean",
    }
    assert len(summary) == 18
    assert required.issubset(summary.columns)
    assert set(summary["scenario"]) == {"kamp_calibrated_defect_hazard"}


def test_kamp_report_contains_not_real_factory_validation():
    report = (OUTPUT_DIR / "kamp_calibrated_rsw_report.md").read_text(encoding="utf-8")
    assert "not real factory validation" in report
    assert "It calibrates only the defect-risk proxy" in report
    assert "It does not validate PM scheduling, tip dressing timing" in report
    assert "PM scheduling 자체를 실제 데이터로 검증한 것으로 해석하면 안 된다." in report
