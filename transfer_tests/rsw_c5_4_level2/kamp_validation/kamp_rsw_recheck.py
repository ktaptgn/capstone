"""Run the RSW mini-test with only the defect-risk proxy KAMP-calibrated."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


HERE = Path(__file__).resolve().parent
RSW_ROOT = HERE.parent
if str(RSW_ROOT) not in sys.path:
    sys.path.insert(0, str(RSW_ROOT))

from rsw_c5_4_mini_sim import aggregate_policy_summaries, load_config, run_policy_episode, write_csv

from kamp_defect_calibration import CALIBRATION_JSON


OUTPUT_DIR = HERE / "outputs"
SUMMARY_CSV = OUTPUT_DIR / "kamp_calibrated_rsw_summary.csv"
REPORT_MD = OUTPUT_DIR / "kamp_calibrated_rsw_report.md"
PLOT_PNG = OUTPUT_DIR / "kamp_calibrated_rsw_plot.png"
BASE_SUMMARY_CSV = RSW_ROOT / "outputs" / "rsw_c5_4_policy_summary.csv"
SCENARIO = "kamp_calibrated_defect_hazard"
POLICIES = ["H0", "H_TIME", "H1", "H2", "H3", "H4"]
REGIMES = ["heterogeneous_condition", "high_stress", "high_demand_high_stress"]
REQUIRED_DISCLAIMER = (
    "This is a partial external-data recheck using the KAMP welding dataset. It calibrates only "
    "the defect-risk proxy of the RSW mini-test. It does not validate PM scheduling, tip dressing "
    "timing, maintenance slots, downtime, or electrode wear HI."
)
KOREAN_DISCLAIMER = (
    "KAMP 용접기 AI 데이터셋은 RSW mini-test의 defect-risk proxy를 보정하는 데만 사용했다. "
    "이 데이터에는 전극 마모량, tip dressing 이력, 정비 downtime, maintenance slot 정보가 "
    "없기 때문에 PM scheduling 자체를 실제 데이터로 검증한 것으로 해석하면 안 된다."
)


def load_calibration(path: Path = CALIBRATION_JSON) -> dict[str, Any]:
    calibration = json.loads(path.read_text(encoding="utf-8"))
    if calibration.get("usage") != "defect_hazard_calibration_only":
        raise ValueError("Calibration usage is not restricted to defect hazard.")
    if not calibration.get("recommended_defect_hazard"):
        raise ValueError("No recommended defect hazard is available; recheck must not run.")
    return calibration


def apply_defect_hazard_only(
    config: dict[str, Any], calibration: dict[str, Any]
) -> dict[str, Any]:
    updated = copy.deepcopy(config)
    recommended = calibration["recommended_defect_hazard"]
    hazard = updated["reliability"]["defect_hazard"]
    for key in ("p_max", "center_hi", "slope", "job_severity_weight"):
        hazard[key] = float(recommended[key])
    return updated


def run_recheck(
    calibration: dict[str, Any],
    days: int = 30,
    seeds: list[int] | None = None,
    regimes: list[str] | None = None,
    policies: list[str] | None = None,
) -> list[dict[str, Any]]:
    base = load_config()
    seeds = seeds or [int(seed) for seed in base["simulation"]["seeds"]]
    regimes = regimes or REGIMES
    policies = policies or POLICIES
    rows: list[dict[str, Any]] = []
    for regime in regimes:
        config = apply_defect_hazard_only(load_config(regime=regime), calibration)
        for policy in policies:
            for seed in seeds:
                result = run_policy_episode(
                    config,
                    policy,
                    seed,
                    days=days,
                    record_events=False,
                    scenario=SCENARIO,
                )
                rows.append(result.summary)
            selected = [row for row in rows if row["regime"] == regime and row["policy"] == policy]
            mean_tco = sum(float(row["TCO"]) for row in selected) / len(selected)
            mean_defects = sum(float(row["defects"]) for row in selected) / len(selected)
            print(f"{regime} {policy}: TCO={mean_tco:.2f} defects={mean_defects:.2f}", flush=True)
    return aggregate_policy_summaries(rows)


def _best_by_regime(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.sort_values(["regime", "TCO_mean"])
        .groupby("regime", sort=False)
        .first()
        .reset_index()
    )


def _ranking(frame: pd.DataFrame, regime: str) -> str:
    selected = frame[frame["regime"] == regime].sort_values("TCO_mean")
    return " < ".join(selected["policy"].astype(str))


def write_report(
    base: pd.DataFrame,
    calibrated: pd.DataFrame,
    calibration: dict[str, Any],
    path: Path = REPORT_MD,
) -> None:
    best = _best_by_regime(calibrated)
    comparison_lines = [
        "| regime | base ranking | KAMP-calibrated ranking | changed? |",
        "|---|---|---|---|",
    ]
    for regime in REGIMES:
        base_ranking = _ranking(base, regime)
        calibrated_ranking = _ranking(calibrated, regime)
        comparison_lines.append(
            f"| {regime} | {base_ranking} | {calibrated_ranking} | "
            f"{base_ranking != calibrated_ranking} |"
        )
    result_lines = [
        "| regime | best policy | TCO | defect mean | defect cost | fulfillment |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in best.itertuples():
        result_lines.append(
            f"| {row.regime} | {row.policy} | {row.TCO_mean:.3f} | {row.defect_mean:.3f} | "
            f"{row.defect_cost_mean:.3f} | {row.fulfillment_mean:.6f} |"
        )
    merged = base.merge(
        calibrated,
        on=["regime", "policy"],
        suffixes=("_base", "_kamp"),
    )
    tco_change = float((merged["TCO_mean_kamp"] - merged["TCO_mean_base"]).abs().max())
    defect_change = float((merged["defect_mean_kamp"] - merged["defect_mean_base"]).abs().max())
    recommended = calibration["recommended_defect_hazard"]
    existing = calibration["existing_defect_hazard"]
    lines = [
        "# KAMP-Calibrated RSW Partial Recheck Report",
        "",
        REQUIRED_DISCLAIMER,
        "",
        KOREAN_DISCLAIMER,
        "",
        "This remains a synthetic transfer mini-test and is not real factory validation.",
        "",
        "## Calibration scope",
        "",
        f"- Label granularity: `{calibration['label_granularity']}`",
        f"- Calibration status: `{calibration['calibration_status']}`",
        f"- Matched days: {calibration['matched_day_count']}",
        f"- Weighted defect rate: {calibration['defect_rate_mean']:.8f}",
        f"- Existing p_max: {existing['p_max']}",
        f"- Suggested p_max: {recommended['p_max']}",
        "- Center HI, slope, job severity, PM scheduling, maintenance capacity, downtime, and HI "
        "physics remain unchanged.",
        "",
        "## KAMP-calibrated RSW result",
        "",
        *result_lines,
        "",
        "## Base versus KAMP-calibrated ranking",
        "",
        *comparison_lines,
        "",
        "## Interpretation",
        "",
        f"- Maximum absolute TCO mean change: {tco_change:.6f} synthetic CU.",
        f"- Maximum absolute defect mean change: {defect_change:.6f}.",
        "- The suggested p_max did not exceed the existing conservative p_max lower bound, so the "
        "recheck preserves the base defect hazard and ranking.",
        "- This does not mean KAMP calibration failed. It means this aggregate quality proxy does "
        "not justify a stronger defect hazard than the existing synthetic setting.",
        "- RSW policy ranking remains primarily driven by PM and downtime structure, which KAMP "
        "does not validate.",
        "",
        "## Limitations",
        "",
        "- Result labels are daily/type aggregate counts, not per-weld labels.",
        "- Only 8 days have matched defect counts; one raw-data day has no result row and was not "
        "assumed to have zero defects.",
        "- The recheck cannot validate PM scheduling, tip dressing timing, maintenance slots, "
        "downtime, or electrode wear HI.",
        "- Results are reported as-is without tuning policy rankings.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_plot(base: pd.DataFrame, calibrated: pd.DataFrame, path: Path = PLOT_PNG) -> None:
    regime = "heterogeneous_condition"
    base_view = base[base["regime"] == regime].set_index("policy").loc[POLICIES]
    calibrated_view = calibrated[calibrated["regime"] == regime].set_index("policy").loc[POLICIES]
    positions = list(range(len(POLICIES)))
    fig, axes = plt.subplots(2, 1, figsize=(11, 9))
    for ax in axes:
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    axes[0].bar(
        [value - 0.18 for value in positions],
        base_view["TCO_mean"],
        0.36,
        label="Base",
        color="#94A3B8",
    )
    axes[0].bar(
        [value + 0.18 for value in positions],
        calibrated_view["TCO_mean"],
        0.36,
        label="KAMP-calibrated defect proxy",
        color="#2563EB",
    )
    axes[0].set_xticks(positions, POLICIES)
    axes[0].set_ylabel("TCO (synthetic CU)")
    axes[0].set_title("Base vs KAMP-calibrated TCO")
    axes[0].legend()

    axes[1].bar(
        [value - 0.18 for value in positions],
        base_view["defect_mean"],
        0.36,
        label="Base",
        color="#94A3B8",
    )
    axes[1].bar(
        [value + 0.18 for value in positions],
        calibrated_view["defect_mean"],
        0.36,
        label="KAMP-calibrated defect proxy",
        color="#DC2626",
    )
    axes[1].set_xticks(positions, POLICIES)
    axes[1].set_ylabel("Mean defect events")
    axes[1].set_title("Base vs KAMP-calibrated defect mean")
    axes[1].legend()
    fig.suptitle(
        "KAMP Welding Dataset Partial Defect-Risk Recheck\n"
        "Heterogeneous condition; not real factory validation",
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    calibration = load_calibration()
    summary_rows = run_recheck(calibration)
    write_csv(SUMMARY_CSV, summary_rows)
    calibrated = pd.DataFrame(summary_rows)
    base = pd.read_csv(BASE_SUMMARY_CSV)
    write_report(base, calibrated, calibration)
    write_plot(base, calibrated)
    print(f"Wrote KAMP-calibrated RSW outputs to {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
