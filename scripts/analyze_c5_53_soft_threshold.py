"""Analyze C5.53 hard versus soft-threshold congestion results."""
from __future__ import annotations

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = PROJECT_ROOT / "outputs" / "c5_53" / "summary" / "c5_53_policy_comparison.csv"
DEFAULT_ANALYSIS_DIR = PROJECT_ROOT / "outputs" / "c5_53" / "analysis"
DEFAULT_REPORT = PROJECT_ROOT / "reports" / "c5_53_soft_threshold_congestion_analysis.md"

OFFICIAL_POLICIES = {"H0", "H_TIME", "H1", "H2", "H3", "H4"}
H1_H2_FAMILY = {"H1", "H2", "H1_original", "H1_value_guard", "H2_original", "H2_value_guard"}

OUTPUT_FIELDS = [
    "regime",
    "policy",
    "total_tco_v2",
    "total_tco_v3_hard",
    "total_tco_v4_soft_congestion",
    "congestion_delay_hours_hard",
    "congestion_delay_hours_soft",
    "congestion_cost_hard",
    "congestion_cost_soft",
    "route_hhi",
    "max_route_share",
    "max_route_utilization",
    "max_shovel_utilization",
    "max_crusher_utilization",
    "effective_fulfillment_rate",
    "effective_output",
    "failure_count",
    "cm_count",
    "downtime_hours",
    "pm_visits",
    "rank_tco_v3_hard",
    "rank_tco_v4_soft",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def mean(rows: list[dict[str, str]], key: str) -> float:
    vals = [float(row[key]) for row in rows if row.get(key, "") != ""]
    return statistics.mean(vals) if vals else 0.0


def aggregate(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["regime"], row["policy_id"])].append(row)

    out: list[dict[str, object]] = []
    for (regime, policy), items in sorted(grouped.items()):
        out.append(
            {
                "regime": regime,
                "policy": policy,
                "total_tco_v2": mean(items, "total_tco_v2"),
                "total_tco_v3_hard": mean(items, "total_tco_v3_hard"),
                "total_tco_v4_soft_congestion": mean(items, "total_tco_v4_soft_congestion"),
                "congestion_delay_hours_hard": mean(items, "congestion_delay_hours_hard"),
                "congestion_delay_hours_soft": mean(items, "congestion_delay_hours_soft"),
                "congestion_cost_hard": mean(items, "congestion_cost_hard"),
                "congestion_cost_soft": mean(items, "congestion_cost_soft"),
                "route_hhi": mean(items, "route_hhi"),
                "max_route_share": mean(items, "max_route_share"),
                "max_route_utilization": mean(items, "max_route_utilization"),
                "max_shovel_utilization": mean(items, "max_shovel_utilization"),
                "max_crusher_utilization": mean(items, "max_crusher_utilization"),
                "effective_fulfillment_rate": mean(items, "effective_fulfillment_rate"),
                "effective_output": mean(items, "effective_output"),
                "failure_count": mean(items, "failure_count"),
                "cm_count": mean(items, "cm_count"),
                "downtime_hours": mean(items, "total_downtime_hours"),
                "pm_visits": mean(items, "pm_count"),
                "rank_tco_v3_hard": 0,
                "rank_tco_v4_soft": 0,
            }
        )

    for regime in sorted({row["regime"] for row in out}):
        regime_rows = [row for row in out if row["regime"] == regime]
        for rank, row in enumerate(
            sorted(regime_rows, key=lambda item: float(item["total_tco_v3_hard"])), start=1
        ):
            row["rank_tco_v3_hard"] = rank
        for rank, row in enumerate(
            sorted(regime_rows, key=lambda item: float(item["total_tco_v4_soft_congestion"])),
            start=1,
        ):
            row["rank_tco_v4_soft"] = rank
    return out


def write_csv(rows: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: round(value, 6) if isinstance(value, float) else value
                    for key, value in row.items()
                    if key in OUTPUT_FIELDS
                }
            )


def find(rows: list[dict[str, object]], regime: str, policy: str) -> dict[str, object] | None:
    return next((row for row in rows if row["regime"] == regime and row["policy"] == policy), None)


def best_policy(rows: list[dict[str, object]], regime: str, key: str, official_only: bool = False):
    candidates = [row for row in rows if row["regime"] == regime]
    if official_only:
        candidates = [row for row in candidates if row["policy"] in OFFICIAL_POLICIES]
    return min(candidates, key=lambda row: float(row[key]))


def make_tradeoff(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for regime in sorted({row["regime"] for row in rows}):
        h4 = find(rows, regime, "H4")
        h3 = find(rows, regime, "H3")
        balanced = find(rows, regime, "BALANCED_RR_H4_PM")
        best_h12 = min(
            [row for row in rows if row["regime"] == regime and row["policy"] in H1_H2_FAMILY],
            key=lambda row: float(row["total_tco_v4_soft_congestion"]),
        )
        best_official = best_policy(rows, regime, "total_tco_v4_soft_congestion", official_only=True)
        best_overall = best_policy(rows, regime, "total_tco_v4_soft_congestion", official_only=False)
        out.append(
            {
                "regime": regime,
                "best_official_soft_policy": best_official["policy"],
                "best_overall_soft_policy": best_overall["policy"],
                "h4_soft_tco": h4["total_tco_v4_soft_congestion"] if h4 else 0.0,
                "h3_soft_tco": h3["total_tco_v4_soft_congestion"] if h3 else 0.0,
                "best_h1_h2_soft_policy": best_h12["policy"],
                "best_h1_h2_soft_tco": best_h12["total_tco_v4_soft_congestion"],
                "balanced_rr_soft_tco": balanced["total_tco_v4_soft_congestion"] if balanced else 0.0,
                "balanced_beats_h4": bool(
                    balanced and h4 and balanced["total_tco_v4_soft_congestion"] < h4["total_tco_v4_soft_congestion"]
                ),
                "h4_remains_best_official": bool(best_official["policy"] == "H4"),
            }
        )
    return out


def write_tradeoff(rows: list[dict[str, object]], path: Path) -> None:
    fields = [
        "regime",
        "best_official_soft_policy",
        "best_overall_soft_policy",
        "h4_soft_tco",
        "h3_soft_tco",
        "best_h1_h2_soft_policy",
        "best_h1_h2_soft_tco",
        "balanced_rr_soft_tco",
        "balanced_beats_h4",
        "h4_remains_best_official",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: round(value, 6) if isinstance(value, float) else value
                    for key, value in row.items()
                }
            )


def table_rows(rows: list[dict[str, object]], regime: str, key: str) -> list[str]:
    ranked = sorted(
        [row for row in rows if row["regime"] == regime],
        key=lambda row: float(row[key]),
    )
    lines = []
    for row in ranked:
        lines.append(
            f"| {regime} | {row['policy']} | {row['rank_tco_v3_hard']} | "
            f"{row['rank_tco_v4_soft']} | {float(row['total_tco_v3_hard']):.1f} | "
            f"{float(row['total_tco_v4_soft_congestion']):.1f} | "
            f"{float(row['congestion_delay_hours_hard']):.2f} | "
            f"{float(row['congestion_delay_hours_soft']):.2f} | "
            f"{float(row['effective_fulfillment_rate']):.3f} | "
            f"{float(row['failure_count']):.1f} | "
            f"{float(row['downtime_hours']):.1f} |"
        )
    return lines


def write_report(rows: list[dict[str, object]], tradeoff: list[dict[str, object]], path: Path) -> None:
    regimes = sorted({row["regime"] for row in rows})
    lines = [
        "# C5.53 Soft-Threshold Congestion Analysis",
        "",
        "## Why This Variant Was Needed",
        "",
        "The H4 zero-congestion audit found no calculation bypass. H4 uses the same C5.53 congestion path as H1/H2/H3, but the hard-threshold formula only penalizes utilization above 1.0. That can under-penalize near-capacity operation, especially for capacity-aware policies that stay just below the hard cap.",
        "",
        "## Audit Recap",
        "",
        "- H4 route and facility load recording is valid.",
        "- H4 route/facility utilization is calculated.",
        "- Existing `total_tco_v3` is preserved as the hard-threshold result.",
        "- `BALANCED_RR_H4_PM` is an audit-only synthetic comparator, not an official policy.",
        "",
        "## Formula",
        "",
        "Hard congestion remains:",
        "",
        "```text",
        "hard_queue_delay = alpha_hard * max(utilization - 1.0, 0.0) ** beta_hard",
        "```",
        "",
        "Soft congestion adds near-capacity pressure:",
        "",
        "```text",
        "soft_start = 0.85",
        "effective_pressure = max((utilization - soft_start) / (1.0 - soft_start), 0.0)",
        "soft_queue_delay = alpha_soft * effective_pressure ** beta_soft",
        "queue_delay_soft_total = soft_queue_delay + hard_queue_delay",
        "```",
        "",
        "## Policy x Regime Ranking",
        "",
        "| regime | policy | hard rank | soft rank | TCO v3 hard | TCO v4 soft | hard congestion h | soft congestion h | effective fulfillment | failures | downtime h |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for regime in regimes:
        lines.extend(table_rows(rows, regime, "total_tco_v4_soft_congestion"))
    lines += [
        "",
        "## H4 Comparisons Under Soft Threshold",
        "",
        "| regime | H4 soft TCO | H3 soft TCO | best H1/H2 variant | best H1/H2 soft TCO | Balanced RR soft TCO | H4 best official? | Balanced beats H4? |",
        "|---|---:|---:|---|---:|---:|---|---|",
    ]
    for row in tradeoff:
        lines.append(
            f"| {row['regime']} | {float(row['h4_soft_tco']):.1f} | "
            f"{float(row['h3_soft_tco']):.1f} | {row['best_h1_h2_soft_policy']} | "
            f"{float(row['best_h1_h2_soft_tco']):.1f} | "
            f"{float(row['balanced_rr_soft_tco']):.1f} | "
            f"{row['h4_remains_best_official']} | {row['balanced_beats_h4']} |"
        )
    all_h4_best = all(bool(row["h4_remains_best_official"]) for row in tradeoff)
    any_balanced_beats = any(bool(row["balanced_beats_h4"]) for row in tradeoff)
    lines += [
        "",
        "## Interpretation",
        "",
        f"- H4 remains best among official H0-H4 policies under soft TCO: {all_h4_best}.",
        f"- BALANCED_RR_H4_PM beats H4 in at least one regime: {any_balanced_beats}. This is not a final policy result; it is evidence that route allocation can be improved beyond current H4.",
        "- H3 remains the value-oriented middle option when it approaches H4, but the soft-threshold comparison should be read by regime rather than as a universal replacement.",
        "- H1/H2 variants remain structurally exposed when C-route concentration creates high soft congestion and low effective fulfillment.",
        "- H0/H_TIME can retain high effective fulfillment but remain dominated in practice by failure, CM, and downtime.",
        "",
        "## Design Implication",
        "",
        "Soft thresholding changes the interpretation from pure capacity exceedance to near-capacity pressure. If the synthetic balanced comparator consistently beats H4, the next design step is a C5.54 route allocation experiment, not immediate H5 creation. H5 should only be justified after testing whether an official policy can combine H4's reliability/flow logic with a more effective route allocation rule.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyze C5.53 soft-threshold congestion outputs.")
    ap.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    ap.add_argument("--analysis-dir", default=str(DEFAULT_ANALYSIS_DIR))
    ap.add_argument("--report", default=str(DEFAULT_REPORT))
    args = ap.parse_args()

    rows = aggregate(read_csv(Path(args.summary)))
    analysis_dir = Path(args.analysis_dir)
    policy_csv = analysis_dir / "c5_53_soft_threshold_policy_comparison.csv"
    tradeoff_csv = analysis_dir / "c5_53_soft_threshold_tradeoff_summary.csv"
    write_csv(rows, policy_csv)
    tradeoff = make_tradeoff(rows)
    write_tradeoff(tradeoff, tradeoff_csv)
    write_report(rows, tradeoff, Path(args.report))
    print(f"Wrote {policy_csv}")
    print(f"Wrote {tradeoff_csv}")
    print(f"Wrote {Path(args.report)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
