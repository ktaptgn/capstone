"""C5.4 Tier-4 presentation visuals, rendered from the analysis artifacts (no re-simulation).

Reads the sweep CSV + the Tier-2/3 JSON outputs and renders four presentation figures (PNG+SVG)
to outputs/c5_4/analysis/, plus one combined 2x2 dashboard:

  1. tco_boxplots      -- per-policy TCO distribution by regime (variance + outliers).
  2. failure_vs_endhi  -- per-seed failures vs end-of-campaign HI (CBM-threshold validity:
                          state-aware runs lean near the threshold yet does NOT fail; blind runs
                          high-HI/over-serviced yet fails).
  3. frailty_cv_curve  -- state-aware vs blind TCO as frailty CV rises (condition-awareness value).
  4. failure_timing    -- failures by campaign third (early/mid/late) per policy.

Inputs (must exist -- run run_c5_4_sweep.py / run_c5_4_sensitivity.py / analyze_c5_4_mechanism.py):
  outputs/c5_4/summary/c5_4_policy_comparison.csv
  outputs/c5_4/sensitivity/c5_4_sensitivity_frailty_cv.json
  outputs/c5_4/mechanism/c5_4_mechanism.json
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "outputs" / "c5_4" / "summary" / "c5_4_policy_comparison.csv"
FRAILTY_JSON = ROOT / "outputs" / "c5_4" / "sensitivity" / "c5_4_sensitivity_frailty_cv.json"
MECH_JSON = ROOT / "outputs" / "c5_4" / "mechanism" / "c5_4_mechanism.json"
OUT_DIR = ROOT / "outputs" / "c5_4" / "analysis"

REGIMES = ["heterogeneous_condition", "high_stress", "high_demand_high_stress"]
REGIME_LABELS = {
    "heterogeneous_condition": "heterogeneous condition",
    "high_stress": "high stress",
    "high_demand_high_stress": "high demand + stress",
}
POLICIES = ["H0", "H_TIME", "H1", "H2", "H3", "H4"]
POLICY_LABELS = {
    "H0": "H0 calendar (blind)",
    "H_TIME": "H_TIME hours (blind)",
    "H1": "H1 CBM+health*",
    "H2": "H2 risk*",
    "H3": "H3 cost-value",
    "H4": "H4 flow",
}
# blind = greys; state-aware CBM/risk = greens (highlight, marked *); cost-value/flow = amber/blue
COLORS = {
    "H0": "#9CA3AF", "H_TIME": "#6B7280",
    "H1": "#16A34A", "H2": "#0D9488",
    "H3": "#F59E0B", "H4": "#3B82F6",
}


def _despine(ax):
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def load_rows():
    return list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))


# --- 1. TCO box plots -----------------------------------------------------------------------
def _boxplot_panel(ax, rows, regime):
    data = [
        [float(r["total_tco"]) for r in rows if r["regime"] == regime and r["policy_id"] == p]
        for p in POLICIES
    ]
    bp = ax.boxplot(data, patch_artist=True, widths=0.6, showfliers=True,
                    medianprops=dict(color="black", linewidth=1.3),
                    flierprops=dict(marker="o", markersize=3, markerfacecolor="none", alpha=0.5))
    for patch, p in zip(bp["boxes"], POLICIES):
        patch.set_facecolor(COLORS[p])
        patch.set_alpha(0.85)
        patch.set_edgecolor("white")
    ax.set_xticks(range(1, len(POLICIES) + 1))
    ax.set_xticklabels(POLICIES, fontsize=9)
    ax.set_title(REGIME_LABELS[regime], fontsize=11, fontweight="bold")
    _despine(ax)


def fig_tco_boxplots(rows):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, regime in zip(axes, REGIMES):
        _boxplot_panel(ax, rows, regime)
    axes[0].set_ylabel("total TCO (normalized CU)", fontsize=10)
    fig.suptitle("C5.4 — TCO distribution across 30 seeds (lower = better). State-aware H1/H2 are "
                 "lowest and tightest; blind H0/H_TIME are high and high-variance.",
                 fontsize=12, fontweight="bold", y=1.00)
    fig.tight_layout()
    return fig


# --- 2. failures vs end-HI scatter ----------------------------------------------------------
def _scatter_panel(ax, rows, regime):
    for p in POLICIES:
        xs = [float(r["avg_truck_hi"]) for r in rows if r["regime"] == regime and r["policy_id"] == p]
        ys = [float(r["failure_count"]) for r in rows if r["regime"] == regime and r["policy_id"] == p]
        ax.scatter(xs, ys, s=34, color=COLORS[p], alpha=0.8, edgecolor="white", linewidth=0.5,
                   label=POLICY_LABELS[p])
    ax.axvline(0.20, color="#DC2626", linestyle="--", linewidth=1, alpha=0.7)
    ax.text(0.205, ax.get_ylim()[1] * 0.92, "failure floor 0.20", color="#DC2626", fontsize=8)
    ax.set_title(REGIME_LABELS[regime], fontsize=11, fontweight="bold")
    ax.set_xlabel("end-of-campaign avg truck HI", fontsize=10)
    _despine(ax)
    ax.grid(axis="both", alpha=0.2)


def fig_failure_vs_endhi(rows):
    panels = ["heterogeneous_condition", "high_stress"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    for ax, regime in zip(axes, panels):
        _scatter_panel(ax, rows, regime)
    axes[0].set_ylabel("failures (CM events) per run", fontsize=10)
    axes[1].legend(loc="upper right", fontsize=8, framealpha=0.9)
    fig.suptitle("C5.4 — failures vs end HI (each point = one seed). Blind (grey) ends HIGH-HI "
                 "(over-serviced) yet FAILS; state-aware (green) runs LEAN near the threshold yet "
                 "does not — CBM-threshold validity.", fontsize=11, fontweight="bold", y=1.00)
    fig.tight_layout()
    return fig


# --- 3. frailty-CV curve --------------------------------------------------------------------
def fig_frailty_curve():
    data = json.loads(FRAILTY_JSON.read_text(encoding="utf-8"))
    rows = data["rows"]
    cvs = [r["cv"] for r in rows]
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    for p in POLICIES:
        ys = [r["policies"][p]["tco"] for r in rows]
        ax.plot(cvs, ys, marker="o", markersize=4, color=COLORS[p], label=POLICY_LABELS[p],
                linewidth=2 if p in ("H1", "H2") else 1.4,
                linestyle="-" if p in ("H1", "H2", "H0", "H_TIME") else "--")
    sa = [r["best_state_aware_tco"] for r in rows]
    bl = [r["best_blind_tco"] for r in rows]
    ax.fill_between(cvs, sa, bl, color="#16A34A", alpha=0.08)
    for x, lo, hi, r in zip(cvs, sa, bl, rows):
        if r["cv"] in (0.10, 0.50, 0.80):
            ax.annotate(f"+{r['state_aware_advantage_pct']:.0f}%", (x, (lo + hi) / 2),
                        fontsize=8, color="#15803D", ha="center")
    ax.set_xlabel("frailty CV (wear heterogeneity)", fontsize=10)
    ax.set_ylabel("mean TCO (normalized CU)", fontsize=10)
    ax.set_title("C5.4 — condition-awareness value vs frailty heterogeneity\n"
                 "state-aware advantage grows +33% → +50% as CV rises (shaded = state-aware vs blind gap)",
                 fontsize=11, fontweight="bold")
    ax.legend(loc="center left", fontsize=8, framealpha=0.9)
    _despine(ax)
    fig.tight_layout()
    return fig


# --- 4. failure-timing histogram ------------------------------------------------------------
def _timing_panel(ax, timing, regime):
    thirds = ["early", "mid", "late"]
    hatch = {"early": "", "mid": "//", "late": ".."}
    x = range(len(POLICIES))
    bottoms = [0.0] * len(POLICIES)
    for t in thirds:
        vals = [timing.get(f"{regime}|{p}", {}).get(t, 0) for p in POLICIES]
        ax.bar(x, vals, bottom=bottoms, width=0.62,
               color=[COLORS[p] for p in POLICIES], alpha=0.85,
               edgecolor="white", linewidth=0.5, hatch=hatch[t])
        bottoms = [b + v for b, v in zip(bottoms, vals)]
    ax.set_xticks(list(x))
    ax.set_xticklabels(POLICIES, fontsize=9)
    ax.set_title(REGIME_LABELS[regime], fontsize=11, fontweight="bold")
    _despine(ax)


def fig_failure_timing():
    mech = json.loads(MECH_JSON.read_text(encoding="utf-8"))
    timing = mech["timing"]
    panels = ["heterogeneous_condition", "high_stress"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    for ax, regime in zip(axes, panels):
        _timing_panel(ax, timing, regime)
    axes[0].set_ylabel("total failures over 12 seeds", fontsize=10)
    legend = [Line2D([0], [0], marker="s", color="w", markerfacecolor="#6B7280", markersize=9,
                     label="early third"),
              Line2D([0], [0], marker="s", color="w", markerfacecolor="#6B7280", markersize=9,
                     label="mid (//)"),
              Line2D([0], [0], marker="s", color="w", markerfacecolor="#6B7280", markersize=9,
                     label="late (..)")]
    axes[1].legend(handles=legend, loc="upper right", fontsize=8, framealpha=0.9)
    fig.suptitle("C5.4 — failures by campaign third. Blind H0/H_TIME fail steadily across the whole "
                 "campaign (frailty leak); state-aware stays near zero.",
                 fontsize=11, fontweight="bold", y=1.00)
    fig.tight_layout()
    return fig


def _save(fig, name):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        path = OUT_DIR / f"{name}.{ext}"
        fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Wrote {OUT_DIR / (name + '.png')} (+svg)")


def main() -> int:
    rows = load_rows()
    _save(fig_tco_boxplots(rows), "c5_4_tco_boxplots")
    _save(fig_failure_vs_endhi(rows), "c5_4_failure_vs_endhi")
    _save(fig_frailty_curve(), "c5_4_frailty_cv_curve")
    _save(fig_failure_timing(), "c5_4_failure_timing")
    plt.close("all")
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
