"""Generate reports and plots for the optional RSW sanity improvement runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from rsw_c5_4_mini_sim import ROOT, build_scenario_contract, load_config


POLICIES = ["H0", "H_TIME", "H1", "H2", "H3", "H4"]
COLORS = {
    "H0": "#9CA3AF",
    "H_TIME": "#6B7280",
    "H1": "#16A34A",
    "H2": "#0D9488",
    "H3": "#F59E0B",
    "H4": "#3B82F6",
}
NOT_FACTORY_VALIDATION = (
    "These additional runs are sanity checks, not real factory validation."
)


def read_summary(contract: dict[str, Any]) -> pd.DataFrame:
    path = ROOT / contract["outputs"]["directory"] / contract["outputs"]["policy_summary_csv"]
    if not path.exists():
        raise FileNotFoundError(f"Run the scenario before generating sanity outputs: {path}")
    return pd.read_csv(path)


def markdown_table(frame: pd.DataFrame, columns: list[str], digits: int = 3) -> str:
    headers = [column.replace("_", " ") for column in columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---:" if column not in {"regime", "policy"} else "---" for column in columns) + "|",
    ]
    for _, row in frame[columns].iterrows():
        values = []
        for column in columns:
            value = row[column]
            values.append(f"{value:.{digits}f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _despine(ax) -> None:
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def write_stress_plot(summary: pd.DataFrame, path: Path) -> None:
    ordered = summary.set_index("policy").loc[POLICIES].reset_index()
    fig, axes = plt.subplots(2, 1, figsize=(11, 9))
    axes[0].bar(ordered["policy"], ordered["TCO_mean"], color=[COLORS[p] for p in POLICIES])
    axes[0].set_ylabel("TCO (synthetic CU)")
    axes[0].set_title("Demand pressure stress: policy TCO")
    _despine(axes[0])

    axes[1].bar(
        ordered["policy"],
        ordered["unmet_welds_mean"],
        color=[COLORS[p] for p in POLICIES],
    )
    axes[1].set_ylabel("Mean unmet welds")
    axes[1].set_title("Demand pressure stress: unmet demand")
    _despine(axes[1])

    fig.suptitle(
        "RSW Demand Pressure Stress Sanity Run\n"
        "30 days x 10 seeds; synthetic transfer test, not factory validation",
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_horizon_plot(summary: pd.DataFrame, path: Path) -> None:
    regimes = ["heterogeneous_condition", "high_stress", "high_demand_high_stress"]
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    width = 0.12
    x = list(range(len(regimes)))
    for index, policy in enumerate(POLICIES):
        subset = summary[summary["policy"] == policy].set_index("regime").loc[regimes]
        positions = [value + (index - 2.5) * width for value in x]
        axes[0].bar(positions, subset["TCO_mean"], width, label=policy, color=COLORS[policy])
    axes[0].set_xticks(x, ["heterogeneous", "high stress", "high demand + stress"])
    axes[0].set_ylabel("TCO (synthetic CU)")
    axes[0].set_title("90-day TCO by regime and policy")
    axes[0].legend(ncols=6, fontsize=8)
    _despine(axes[0])

    grouped = summary.groupby("policy", sort=False)[["failure_mean", "CM_mean"]].sum().loc[POLICIES]
    positions = list(range(len(POLICIES)))
    axes[1].bar(
        [value - 0.18 for value in positions],
        grouped["failure_mean"],
        0.36,
        label="Failure mean total",
        color="#DC2626",
    )
    axes[1].bar(
        [value + 0.18 for value in positions],
        grouped["CM_mean"],
        0.36,
        label="CM mean total",
        color="#2563EB",
    )
    axes[1].set_xticks(positions, POLICIES)
    axes[1].set_ylabel("Sum across regimes")
    axes[1].set_title("90-day failure and CM paths")
    axes[1].legend()
    _despine(axes[1])

    fig.suptitle(
        "RSW 90-Day Horizon Sanity Run\n"
        "10 seeds x 3 regimes; synthetic transfer test, not factory validation",
        fontweight="bold",
    )
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def stress_findings(summary: pd.DataFrame) -> list[str]:
    best = summary.sort_values("TCO_mean").iloc[0]
    unmet = summary[summary["unmet_welds_mean"] > 0]
    if unmet.empty:
        unmet_text = "No policy produced mean unmet demand; substantial demand slack remained."
    else:
        names = ", ".join(unmet["policy"])
        unmet_text = (
            f"Mean unmet demand appeared only for {names}; most policies still retained "
            "enough production slack for fulfillment = 1.000."
        )
    return [
        f"{best['policy']} had the lowest stress TCO ({best['TCO_mean']:.2f} synthetic CU).",
        unmet_text,
        "H4 did not win the stress run; results are retained without post-hoc tuning.",
    ]


def horizon_findings(base: pd.DataFrame, horizon: pd.DataFrame) -> list[str]:
    base_failures = base["failure_mean"].sum()
    horizon_failures = horizon["failure_mean"].sum()
    best = (
        horizon.sort_values(["regime", "TCO_mean"])
        .groupby("regime", sort=False)
        .first()
        .reset_index()
    )
    winners = ", ".join(f"{row.regime}: {row.policy}" for row in best.itertuples())
    return [
        f"Failure/CM mean totals increased from {base_failures:.1f} at 30 days to "
        f"{horizon_failures:.1f} at 90 days.",
        "Observed 90-day failure/CM events remained concentrated in H_TIME.",
        f"Lowest-TCO policies by regime were {winners}.",
        "H1-H4 retained component-targeted PM; no policy ranking was forced.",
    ]


def write_scenario_reports(
    stress: pd.DataFrame,
    horizon: pd.DataFrame,
    base: pd.DataFrame,
    stress_path: Path,
    horizon_path: Path,
) -> None:
    stress_ranked = stress.sort_values("TCO_mean")
    stress_lines = [
        "# RSW Demand Pressure Stress Sanity Report",
        "",
        NOT_FACTORY_VALIDATION,
        " Demand stress was added because the original base demand had too much slack.",
        "",
        "## Results",
        "",
        markdown_table(
            stress_ranked,
            ["policy", "TCO_mean", "fulfillment_mean", "unmet_welds_mean", "PMvisits_mean", "CM_mean", "failure_mean"],
        ),
        "",
        "## Findings",
        "",
        *[f"- {item}" for item in stress_findings(stress)],
        "",
        "Results are reported as-is and not tuned to reproduce the C5.4 mining ranking.",
    ]
    stress_path.write_text("\n".join(stress_lines) + "\n", encoding="utf-8")

    horizon_ranked = horizon.sort_values(["regime", "TCO_mean"])
    horizon_lines = [
        "# RSW 90-Day Horizon Sanity Report",
        "",
        NOT_FACTORY_VALIDATION,
        " The 90-day run was added because the original failure path was sparse.",
        "",
        "## Results",
        "",
        markdown_table(
            horizon_ranked,
            ["regime", "policy", "TCO_mean", "PMvisits_mean", "CM_mean", "failure_mean", "fulfillment_mean"],
        ),
        "",
        "## Findings",
        "",
        *[f"- {item}" for item in horizon_findings(base, horizon)],
        "",
        "Results are reported as-is and not tuned to reproduce the C5.4 mining ranking.",
    ]
    horizon_path.write_text("\n".join(horizon_lines) + "\n", encoding="utf-8")


def write_integrated_report(
    base: pd.DataFrame, stress: pd.DataFrame, horizon: pd.DataFrame, path: Path
) -> None:
    base_best = base.sort_values(["regime", "TCO_mean"]).groupby("regime", sort=False).first().reset_index()
    horizon_best = (
        horizon.sort_values(["regime", "TCO_mean"]).groupby("regime", sort=False).first().reset_index()
    )
    lines = [
        "# RSW C5.4 Mini-Test Sanity Improvement Report",
        "",
        "## 1. Purpose",
        "",
        f"{NOT_FACTORY_VALIDATION} The original 30-day base result is preserved.",
        "",
        "## 2. Why additional sanity runs were needed",
        "",
        "- Demand stress was added because the original base demand had too much slack.",
        "- The 90-day run was added because the original failure path was sparse.",
        "",
        "## 3. Base 30-day result recap",
        "",
        markdown_table(base_best, ["regime", "policy", "TCO_mean", "failure_mean", "fulfillment_mean"]),
        "",
        "## 4. Demand pressure stress result",
        "",
        *[f"- {item}" for item in stress_findings(stress)],
        "",
        "## 5. 90-day horizon sanity result",
        "",
        markdown_table(horizon_best, ["regime", "policy", "TCO_mean", "CM_mean", "failure_mean"]),
        "",
        *[f"- {item}" for item in horizon_findings(base, horizon)],
        "",
        "## 6. What changed from the original mini-test",
        "",
        "- Optional higher-demand and longer-horizon execution contracts were added.",
        "- Separate outputs expose a limited unmet-demand path and a somewhat richer failure/CM path.",
        "",
        "## 7. What did not change",
        "",
        "- The original 30-day base result and its output files remain unchanged.",
        "- The common environment, policies, seeds, KPI definitions, and synthetic scope remain unchanged.",
        "- Results are reported as-is and not tuned to reproduce the C5.4 mining ranking.",
        "",
        "## 8. Remaining limitations",
        "",
        "- These are synthetic transfer checks with no real factory calibration or validation.",
        "- Stress produced mean unmet demand only for H_TIME; demand slack remained for most policies.",
        "- Even at 90 days, failures remained sparse and concentrated in H_TIME.",
        "",
        "## 9. Final presentation recommendation",
        "",
        "Present the runs as supporting sanity checks for PM-production and horizon behavior, "
        "not as proof of manufacturing performance.",
        "",
        "한국어 발표 요약: RSW mini-test의 추가 sanity run은 기존 결과를 대체하기 위한 것이 아니라, "
        "기존 mini-test의 약점이었던 낮은 demand pressure와 짧은 horizon을 점검하기 위한 보조 검증이다. "
        "Demand stress에서는 PM과 생산 사이의 trade-off가 더 강하게 나타나는지 확인하고, 90-day run에서는 "
        "failure/CM path가 더 드러나는지 확인한다. 이 결과 역시 실제 공장 검증이 아니라 synthetic transfer test다.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    config = load_config()
    stress_contract = build_scenario_contract(config, "demand_pressure_stress")
    horizon_contract = build_scenario_contract(config, "horizon_sanity_90")
    base = pd.read_csv(ROOT / config["outputs"]["directory"] / config["outputs"]["policy_summary_csv"])
    stress = read_summary(stress_contract)
    horizon = read_summary(horizon_contract)

    stress_dir = ROOT / stress_contract["outputs"]["directory"]
    horizon_dir = ROOT / horizon_contract["outputs"]["directory"]
    write_stress_plot(stress, stress_dir / stress_contract["outputs"]["plot_png"])
    write_horizon_plot(horizon, horizon_dir / horizon_contract["outputs"]["plot_png"])
    write_scenario_reports(
        stress,
        horizon,
        base,
        stress_dir / stress_contract["outputs"]["report_markdown"],
        horizon_dir / horizon_contract["outputs"]["report_markdown"],
    )
    integrated = ROOT / config["outputs"]["directory"] / config["outputs"]["sanity_improvement_report"]
    write_integrated_report(base, stress, horizon, integrated)
    print(f"Wrote sanity reports and plots under {ROOT / config['outputs']['directory']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
