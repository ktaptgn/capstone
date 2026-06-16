"""Create a descriptive KAMP-based defect-risk calibration proxy."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from kamp_welding_profile import DAILY_CSV, OUTPUT_DIR, PROFILE_CSV


RSW_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = RSW_ROOT / "rsw_c5_4_config.yaml"
CALIBRATION_JSON = OUTPUT_DIR / "kamp_defect_calibration.json"
NOT_SUPPORTED = [
    "PM scheduling validation",
    "tip dressing timing validation",
    "maintenance slot validation",
    "downtime validation",
    "electrode wear HI calibration",
]


def load_label_granularity() -> str:
    profile = pd.read_csv(PROFILE_CSV)
    selected = profile[profile["metric"] == "label_granularity"]
    if selected.empty:
        raise ValueError("Profile output does not declare label granularity.")
    return str(selected.iloc[0]["value"])


def build_calibration(
    daily: pd.DataFrame, config: dict[str, Any], label_granularity: str
) -> dict[str, Any]:
    matched = daily.dropna(subset=["defect_rate"]).copy()
    existing = config["reliability"]["defect_hazard"]
    if matched.empty or label_granularity == "unavailable":
        return {
            "label_granularity": "unavailable",
            "calibration_status": "not_applied",
            "matched_day_count": 0,
            "defect_rate_mean": None,
            "defect_rate_min": None,
            "defect_rate_max": None,
            "recommended_defect_hazard": None,
            "usage": "defect_hazard_calibration_only",
            "not_supported": NOT_SUPPORTED,
        }
    total_defects = float(matched["defect_count_total"].sum())
    total_welds = float(matched["n_welds"].sum())
    weighted_rate = total_defects / total_welds
    recommended_p_max = max(float(existing["p_max"]), min(0.08, weighted_rate * 10.0))
    variability_columns = [
        "force_std",
        "current_std",
        "voltage_std",
        "weld_time_std",
    ]
    correlations = {
        column: (
            None
            if matched[column].nunique() < 2 or matched["defect_rate"].nunique() < 2
            else round(float(matched[column].corr(matched["defect_rate"])), 6)
        )
        for column in variability_columns
    }
    return {
        "label_granularity": label_granularity,
        "calibration_status": "suggested_only",
        "matched_day_count": int(len(matched)),
        "unmatched_raw_day_count": int(daily["defect_rate"].isna().sum()),
        "defect_count_total": int(total_defects),
        "matched_weld_count": int(total_welds),
        "defect_rate_mean": round(weighted_rate, 8),
        "daily_defect_rate_mean": round(float(matched["defect_rate"].mean()), 8),
        "defect_rate_min": round(float(matched["defect_rate"].min()), 8),
        "defect_rate_max": round(float(matched["defect_rate"].max()), 8),
        "process_variability_defect_rate_correlation": correlations,
        "recommended_defect_hazard": {
            "p_max": round(recommended_p_max, 8),
            "center_hi": float(existing["center_hi"]),
            "slope": float(existing["slope"]),
            "job_severity_weight": float(existing["job_severity_weight"]),
            "status": "suggested_only",
        },
        "existing_defect_hazard": {
            key: existing[key] for key in ("p_max", "center_hi", "slope", "job_severity_weight")
        },
        "usage": "defect_hazard_calibration_only",
        "not_supported": NOT_SUPPORTED,
        "interpretation": (
            "Daily aggregate labels support descriptive defect-risk calibration only. "
            "They do not support per-weld supervised prediction or maintenance validation."
        ),
    }


def main() -> int:
    if not DAILY_CSV.exists() or not PROFILE_CSV.exists():
        raise FileNotFoundError("Run kamp_welding_profile.py before calibration.")
    daily = pd.read_csv(DAILY_CSV)
    with CONFIG_PATH.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    calibration = build_calibration(daily, config, load_label_granularity())
    CALIBRATION_JSON.write_text(
        json.dumps(calibration, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote calibration proxy to {CALIBRATION_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
