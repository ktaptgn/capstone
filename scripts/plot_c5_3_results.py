"""Render the C5.3 capstone result chart from the sweep summary CSV.

Two panels: mean total TCO and mean corrective-maintenance (failure) count, grouped by
regime with one bar per dispatch policy. Condition-aware policies (H1/H2) are drawn in a
distinct hue so the headline -- condition-aware route dispatch wins, and avoids failures
under stress -- reads at a glance. Outputs PNG + SVG to outputs/c5_3/analysis/.
"""
from __future__ import annotations

import csv
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "outputs" / "c5_3" / "summary" / "c5_3_policy_comparison.csv"
OUT_DIR = ROOT / "outputs" / "c5_3" / "analysis"

REGIMES = ["heterogeneous_condition", "high_stress", "high_demand_high_stress"]
REGIME_LABELS = ["heterogeneous\ncondition", "high\nstress", "high demand\n+ stress"]
POLICIES = ["H0", "H1", "H2", "H3", "H4"]
POLICY_LABELS = {
    "H0": "H0 route-blind",
    "H1": "H1 health*",
    "H2": "H2 risk*",
    "H3": "H3 value",
    "H4": "H4 capacity",
}
# condition-aware (H1/H2) highlighted green; condition-blind muted
COLORS = {"H0": "#9CA3AF", "H1": "#16A34A", "H2": "#0D9488", "H3": "#F59E0B", "H4": "#3B82F6"}


def load_means(metric: str) -> dict[tuple[str, str], float]:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    means: dict[tuple[str, str], float] = {}
    for regime in REGIMES:
        for policy in POLICIES:
            vals = [
                float(r[metric])
                for r in rows
                if r["regime"] == regime and r["policy_id"] == policy
            ]
            means[(regime, policy)] = statistics.mean(vals) if vals else 0.0
    return means


def grouped_bars(ax, means, title, ylabel, value_fmt):
    n_pol = len(POLICIES)
    group_w = 0.82
    bar_w = group_w / n_pol
    for p_i, policy in enumerate(POLICIES):
        xs = [g + (p_i - (n_pol - 1) / 2) * bar_w for g in range(len(REGIMES))]
        ys = [means[(regime, policy)] for regime in REGIMES]
        ax.bar(xs, ys, bar_w, label=POLICY_LABELS[policy], color=COLORS[policy],
               edgecolor="white", linewidth=0.5)
    ax.set_xticks(range(len(REGIMES)))
    ax.set_xticklabels(REGIME_LABELS, fontsize=9)
    ax.set_title(title, fontsize=12, fontweight="bold", pad=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tco = load_means("total_tco")
    cm = load_means("cm_count")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))
    grouped_bars(ax1, tco, "Total cost of ownership (lower = better)", "mean TCO (normalized CU)", ".0f")
    grouped_bars(ax2, cm, "Corrective repairs / failures (lower = better)", "mean CM events per run", ".0f")
    ax2.legend(loc="upper left", fontsize=8, framealpha=0.9, title="* = condition-aware")

    fig.suptitle(
        "C5.3 — condition-aware route dispatch (H1/H2) beats condition-blind (H0/H3/H4) "
        "on TCO in every regime;\nunder stress it wins by avoiding failures "
        "(PM fixed and identical across all policies)",
        fontsize=11, y=1.02,
    )
    fig.tight_layout()
    png = OUT_DIR / "c5_3_results.png"
    svg = OUT_DIR / "c5_3_results.svg"
    fig.savefig(png, dpi=150, bbox_inches="tight")
    fig.savefig(svg, bbox_inches="tight")
    print(f"Wrote {png}\nWrote {svg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
