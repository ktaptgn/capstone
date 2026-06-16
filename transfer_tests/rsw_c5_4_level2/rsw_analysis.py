"""Step 5 mechanism and sensitivity analysis for the RSW Level 2 mini-test."""

from __future__ import annotations

import argparse
import copy
import csv
import math
import statistics
from pathlib import Path
from typing import Any

import numpy as np

from rsw_c5_4_mini_sim import (
    ROOT,
    aggregate_policy_summaries,
    load_config,
    run_policy_episode,
    write_csv,
)


POLICIES = ("H0", "H_TIME", "H1", "H2", "H3", "H4")
STATE_AWARE = ("H1", "H2")
BLIND = ("H0", "H_TIME")


def mean(rows: list[dict[str, Any]], key: str) -> float:
    return statistics.mean(float(row[key]) for row in rows)


def safe_corr(left: list[float], right: list[float]) -> float | None:
    if len(left) < 3 or np.std(left) == 0 or np.std(right) == 0:
        return None
    return round(float(np.corrcoef(left, right)[0, 1]), 6)


def run_rows(
    config: dict[str, Any], policies: tuple[str, ...] | list[str], seeds: list[int], days: int
) -> list[dict[str, Any]]:
    return [
        run_policy_episode(config, policy, seed, days=days, record_events=False).summary
        for policy in policies
        for seed in seeds
    ]


def build_mechanism(
    seeds: list[int], days: int, regimes: list[str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return causal profiles and failure-timing rows at the Step 4 scale."""
    profiles: list[dict[str, Any]] = []
    timing: list[dict[str, Any]] = []
    third = max(days / 3.0, 1.0)
    for regime in regimes:
        config = load_config(regime=regime)
        rows = run_rows(config, POLICIES, seeds, days)
        for policy in POLICIES:
            group = [row for row in rows if row["policy"] == policy]
            pm_total = max(mean(group, "pm_components"), 1e-12)
            cm_total = max(mean(group, "failures"), 1e-12)
            route_total = max(mean(group, "completed_welds"), 1e-12)
            profiles.append(
                {
                    "regime": regime,
                    "policy": policy,
                    "TCO_mean": round(mean(group, "TCO"), 6),
                    "PMvisits_mean": round(mean(group, "pm_visits"), 6),
                    "CM_mean": round(mean(group, "cm_events"), 6),
                    "failure_mean": round(mean(group, "failures"), 6),
                    "defect_mean": round(mean(group, "defects"), 6),
                    "endHI_mean": round(mean(group, "endHI_mean"), 6),
                    "max_frailty_failure_corr": safe_corr(
                        [float(row["max_frailty"]) for row in group],
                        [float(row["failures"]) for row in group],
                    ),
                    **{
                        f"pm_{component}_share": round(
                            mean(group, f"pm_{component}") / pm_total, 6
                        )
                        for component in ("tip", "cooling", "actuator")
                    },
                    **{
                        f"cm_{component}_share": round(
                            mean(group, f"cm_{component}") / cm_total, 6
                        )
                        for component in ("tip", "cooling", "actuator")
                    },
                    **{
                        f"route_{family}_share": round(
                            mean(group, f"route_{family}") / route_total, 6
                        )
                        for family in ("A", "B", "C")
                    },
                }
            )

        failure_events = []
        for policy in POLICIES:
            for seed in seeds:
                result = run_policy_episode(config, policy, seed, days=days, record_events=False)
                failure_events.extend(result.failure_log)
        for policy in POLICIES:
            selected = [event for event in failure_events if event["policy"] == policy]
            timing.append(
                {
                    "regime": regime,
                    "policy": policy,
                    "early": sum(1 for event in selected if float(event["day"]) <= third),
                    "mid": sum(
                        1
                        for event in selected
                        if third < float(event["day"]) <= 2.0 * third
                    ),
                    "late": sum(1 for event in selected if float(event["day"]) > 2.0 * third),
                    "total": len(selected),
                }
            )
        print(f"mechanism {regime}: complete", flush=True)
    return profiles, timing


def run_frailty_sensitivity(seeds: list[int], days: int) -> list[dict[str, Any]]:
    output = []
    base = load_config(regime="heterogeneous_condition")
    for cv in base["sensitivity"]["frailty_cv"]:
        config = copy.deepcopy(base)
        config["reliability"]["frailty"]["cv"] = float(cv)
        rows = run_rows(config, POLICIES, seeds, days)
        for policy in POLICIES:
            group = [row for row in rows if row["policy"] == policy]
            output.append(
                {
                    "analysis": "frailty_cv",
                    "setting": float(cv),
                    "regime": config["active_regime"],
                    "policy": policy,
                    "seed_count": len(group),
                    "days": days,
                    "TCO_mean": round(mean(group, "TCO"), 6),
                    "PMvisits_mean": round(mean(group, "pm_visits"), 6),
                    "CM_mean": round(mean(group, "cm_events"), 6),
                    "failure_mean": round(mean(group, "failures"), 6),
                    "defect_mean": round(mean(group, "defects"), 6),
                    "fulfillment_mean": round(mean(group, "fulfillment"), 6),
                }
            )
        print(f"sensitivity frailty_cv={cv}: complete", flush=True)
    return output


def run_threshold_sensitivity(seeds: list[int], days: int) -> list[dict[str, Any]]:
    output = []
    for regime in ("heterogeneous_condition", "high_stress", "high_demand_high_stress"):
        base = load_config(regime=regime)
        frozen = copy.deepcopy(base["pm_scheduling"]["cbm_threshold"])
        for scale in base["sensitivity"]["cbm_threshold_scale"]:
            config = copy.deepcopy(base)
            for component, threshold in frozen.items():
                config["pm_scheduling"]["cbm_threshold"][component] = round(
                    float(threshold) * float(scale), 6
                )
            group = run_rows(config, ["H1"], seeds, days)
            output.append(
                {
                    "analysis": "cbm_threshold_scale",
                    "setting": float(scale),
                    "regime": regime,
                    "policy": "H1",
                    "seed_count": len(group),
                    "days": days,
                    "TCO_mean": round(mean(group, "TCO"), 6),
                    "PMvisits_mean": round(mean(group, "pm_visits"), 6),
                    "CM_mean": round(mean(group, "cm_events"), 6),
                    "failure_mean": round(mean(group, "failures"), 6),
                    "defect_mean": round(mean(group, "defects"), 6),
                    "fulfillment_mean": round(mean(group, "fulfillment"), 6),
                }
            )
        print(f"sensitivity cbm_threshold {regime}: complete", flush=True)
    return output


def run_slot_sensitivity(seeds: list[int], days: int) -> list[dict[str, Any]]:
    output = []
    base = load_config(regime="heterogeneous_condition")
    for slots in base["sensitivity"]["maintenance_slots"]:
        config = copy.deepcopy(base)
        config["simulation"]["maintenance_slots"] = int(slots)
        rows = run_rows(config, POLICIES, seeds, days)
        for policy in POLICIES:
            group = [row for row in rows if row["policy"] == policy]
            output.append(
                {
                    "analysis": "maintenance_slots",
                    "setting": int(slots),
                    "regime": config["active_regime"],
                    "policy": policy,
                    "seed_count": len(group),
                    "days": days,
                    "TCO_mean": round(mean(group, "TCO"), 6),
                    "PMvisits_mean": round(mean(group, "pm_visits"), 6),
                    "CM_mean": round(mean(group, "cm_events"), 6),
                    "failure_mean": round(mean(group, "failures"), 6),
                    "defect_mean": round(mean(group, "defects"), 6),
                    "fulfillment_mean": round(mean(group, "fulfillment"), 6),
                }
            )
        print(f"sensitivity maintenance_slots={slots}: complete", flush=True)
    return output


def write_mechanism_markdown(
    path: Path, profiles: list[dict[str, Any]], timing: list[dict[str, Any]], seeds: list[int], days: int
) -> None:
    lines = [
        "# RSW C5.4 Level 2 Mechanism Analysis",
        "",
        f"- Synthetic mini-test scale: {len(seeds)} seeds x {days} days.",
        "- Actual results are reported without forcing the expected C5.4 mining ranking.",
        "",
        "## Failure timing",
        "",
        "| regime | policy | early | mid | late | total |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in timing:
        lines.append(
            f"| {row['regime']} | {row['policy']} | {row['early']} | {row['mid']} | "
            f"{row['late']} | {row['total']} |"
        )
    lines += [
        "",
        "## Causal profile",
        "",
        "| regime | policy | TCO | PM visits | failures | defects | end HI | corr(max frailty, failure) | PM tip share | route A/B/C |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in profiles:
        corr = row["max_frailty_failure_corr"]
        lines.append(
            f"| {row['regime']} | {row['policy']} | {row['TCO_mean']:.2f} | "
            f"{row['PMvisits_mean']:.1f} | {row['failure_mean']:.2f} | "
            f"{row['defect_mean']:.2f} | {row['endHI_mean']:.3f} | {corr} | "
            f"{row['pm_tip_share']:.3f} | {row['route_A_share']:.3f}/"
            f"{row['route_B_share']:.3f}/{row['route_C_share']:.3f} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_sensitivity_markdown(path: Path, rows: list[dict[str, Any]], seeds: list[int], days: int) -> None:
    lines = [
        "# RSW C5.4 Level 2 Sensitivity Analysis",
        "",
        f"- Synthetic reduced-scale analysis: {len(seeds)} seeds x {days} days.",
        "- Lower TCO is better. Rankings below are actual mini-test outputs.",
        "",
    ]
    for analysis in ("frailty_cv", "cbm_threshold_scale", "maintenance_slots"):
        selected = [row for row in rows if row["analysis"] == analysis]
        lines += [
            f"## {analysis}",
            "",
            "| setting | regime | policy | TCO | PM visits | CM | failures | defects | fulfillment |",
            "|---:|---|---|---:|---:|---:|---:|---:|---:|",
        ]
        for row in selected:
            lines.append(
                f"| {row['setting']} | {row['regime']} | {row['policy']} | "
                f"{row['TCO_mean']:.2f} | {row['PMvisits_mean']:.1f} | {row['CM_mean']:.2f} | "
                f"{row['failure_mean']:.2f} | {row['defect_mean']:.2f} | "
                f"{row['fulfillment_mean']:.3f} |"
            )
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run RSW Level 2 mechanism and sensitivity analysis.")
    parser.add_argument("--days", type=int, default=None)
    parser.add_argument("--seeds", nargs="+", type=int, default=None)
    args = parser.parse_args()
    base = load_config()
    days = int(args.days or base["simulation"]["campaign_days"])
    seeds = args.seeds or [int(seed) for seed in base["simulation"]["seeds"]]
    regimes = list(base["regimes"])
    output_dir = ROOT / base["outputs"]["directory"]
    output_dir.mkdir(parents=True, exist_ok=True)

    profiles, timing = build_mechanism(seeds, days, regimes)
    mechanism_rows = [
        {"table": "profile", **row} for row in profiles
    ] + [{"table": "failure_timing", **row} for row in timing]
    write_csv(output_dir / "rsw_c5_4_mechanism.csv", mechanism_rows)
    write_mechanism_markdown(output_dir / "rsw_c5_4_mechanism.md", profiles, timing, seeds, days)

    sensitivity_rows = (
        run_frailty_sensitivity(seeds, days)
        + run_threshold_sensitivity(seeds, days)
        + run_slot_sensitivity(seeds, days)
    )
    write_csv(output_dir / base["outputs"]["sensitivity_csv"], sensitivity_rows)
    write_sensitivity_markdown(
        output_dir / base["outputs"]["sensitivity_markdown"], sensitivity_rows, seeds, days
    )
    print(f"Wrote Step 5 outputs to {output_dir}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
