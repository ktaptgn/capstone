from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "docs" / "c5_1" / "C5_1_HEURISTIC_COMPARISON_ANALYSIS.md"
DEFAULT_PRESENTATION = ROOT / "docs" / "c5_1" / "C5_1_PRESENTATION_RESULT_SUMMARY.md"
DEFAULT_DASHBOARD = ROOT / "docs" / "c5_1" / "C5_1_DASHBOARD_ANALYSIS_MAPPING.md"

PM_ACTIONS = {"PM_TIRE", "PM_VEHICLE", "PM_VEHICLE_BALANCED", "PM_VEHICLE_FAST_EXPENSIVE", "PM_VEHICLE_SLOW_CHEAP"}

POLICY_NAMES = {
    "H0": "Periodic PM Baseline",
    "H1": "Due / Health PM",
    "H2": "PM Risk Priority",
    "H3": "Cost Unit Value",
    "H4": "Flow / Backpressure",
}

KPI_DIRECTIONS = {
    "total_cost": "lower",
    "pm_cost": "lower",
    "unmet_demand": "lower",
    "demand_fulfillment_rate": "higher",
    "completed_loads": "higher",
    "average_available_trucks": "higher",
    "total_downtime": "lower",
    "pm_count": "lower",
    "failure_count": "lower",
    "average_tire_hi": "higher",
    "average_truck_hi": "higher",
    "queue_time": "lower",
}

REQUIRED_KPIS = [
    "total_cost",
    "pm_cost",
    "unmet_demand",
    "demand_fulfillment_rate",
    "completed_loads",
    "average_available_trucks",
    "total_downtime",
    "pm_count",
    "failure_count",
    "average_tire_hi",
    "average_truck_hi",
    "queue_time",
]

MEAN_TABLE_KPIS = REQUIRED_KPIS

RANKING_KPIS = [
    "total_cost",
    "demand_fulfillment_rate",
    "unmet_demand",
    "total_downtime",
    "queue_time",
    "average_available_trucks",
    "pm_cost",
]

COMPOSITE_WEIGHTS = {
    "total_cost": 0.30,
    "demand_fulfillment_rate": 0.25,
    "unmet_demand": 0.15,
    "total_downtime": 0.10,
    "queue_time": 0.10,
    "average_available_trucks": 0.10,
}

KPI_LABELS_KO = {
    "total_cost": "총 운영비용",
    "pm_cost": "PM 비용",
    "unmet_demand": "미충족 수요",
    "demand_fulfillment_rate": "수요 충족률",
    "completed_loads": "완료 운반량",
    "average_available_trucks": "가용 트럭 수",
    "total_downtime": "총 다운타임",
    "pm_count": "PM 횟수",
    "failure_count": "고장 횟수",
    "average_tire_hi": "Tire HI",
    "average_truck_hi": "Truck HI",
    "queue_time": "대기시간",
}

DASHBOARD_BEST_KPIS = [
    "total_cost",
    "demand_fulfillment_rate",
    "unmet_demand",
    "queue_time",
    "average_available_trucks",
    "pm_cost",
    "total_downtime",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze C5.1 H0-H4 heuristic comparison results.")
    parser.add_argument("--summary", required=True, help="Path to outputs/c5_1/summary/policy_comparison.csv")
    parser.add_argument("--out-dir", default=str(ROOT / "outputs" / "c5_1" / "analysis"))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--presentation", default=str(DEFAULT_PRESENTATION))
    parser.add_argument("--dashboard", default=str(DEFAULT_DASHBOARD))
    return parser.parse_args()


def as_number(value: Any) -> Any:
    if value is None or value == "":
        return value
    try:
        number = float(value)
    except (TypeError, ValueError):
        return value
    if number.is_integer():
        return int(number)
    return number


def read_summary(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return [{key: as_number(value) for key, value in row.items()} for row in csv.DictReader(stream)]


def summary_json_note(summary_path: Path, csv_rows: list[dict[str, Any]]) -> str:
    json_path = summary_path.with_suffix(".json")
    if not json_path.exists():
        return f"Paired JSON summary not found at `{json_path.as_posix()}`; CSV was used as the analysis source."
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    json_policies = sorted({str(row.get("policy_id")) for row in payload if row.get("policy_id")})
    csv_policies = sorted({str(row.get("policy_id")) for row in csv_rows if row.get("policy_id")})
    row_status = "matches" if len(payload) == len(csv_rows) else f"differs ({len(payload)} JSON rows vs {len(csv_rows)} CSV rows)"
    policy_status = "matches" if json_policies == csv_policies else f"differs ({json_policies} JSON vs {csv_policies} CSV)"
    return (
        f"Paired JSON summary: `{json_path.as_posix()}`. "
        f"Row count {row_status}; policy set {policy_status}."
    )


def log_dir_from_summary(summary_path: Path) -> Path:
    return summary_path.resolve().parents[1] / "logs"


def read_log_metrics(log_dir: Path, policy_id: str, seed: int) -> dict[str, float]:
    path = log_dir / f"{policy_id}_seed_{seed}.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("records", [])
    if not records:
        return {}

    return {
        "average_available_trucks": mean([record.get("available_trucks", 0) for record in records]),
        "total_downtime": sum(float(record.get("downtime_hours", 0) or 0) for record in records),
        "pm_count": sum(1 for record in records if record.get("action") in PM_ACTIONS),
        "average_tire_hi": mean([record.get("tire_hi", 0) for record in records]),
        "average_truck_hi": mean([record.get("truck_hi", 0) for record in records]),
        "queue_time": mean([record.get("queue_time", 0) for record in records]),
    }


def mean(values: list[Any]) -> float:
    numeric = [float(value) for value in values if value not in (None, "")]
    return sum(numeric) / len(numeric) if numeric else float("nan")


def std(values: list[Any]) -> float:
    numeric = [float(value) for value in values if value not in (None, "")]
    return statistics.stdev(numeric) if len(numeric) > 1 else 0.0


def enrich_rows(rows: list[dict[str, Any]], log_dir: Path) -> list[dict[str, Any]]:
    enriched = []
    for row in rows:
        item = dict(row)
        if "avg_queue_time" in item and "queue_time" not in item:
            item["queue_time"] = item["avg_queue_time"]
        item.update(read_log_metrics(log_dir, str(item["policy_id"]), int(item["seed"])))
        enriched.append(item)
    return enriched


def group_by_policy(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["policy_id"])].append(row)
    return dict(sorted(grouped.items()))


def aggregate_policy_kpis(grouped: dict[str, list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, float]]]:
    long_rows: list[dict[str, Any]] = []
    means: dict[str, dict[str, float]] = {}
    for policy_id, rows in grouped.items():
        means[policy_id] = {}
        for kpi in MEAN_TABLE_KPIS:
            values = [row.get(kpi) for row in rows if row.get(kpi) not in (None, "")]
            if not values:
                continue
            kpi_mean = mean(values)
            kpi_std = std(values)
            kpi_min = min(float(value) for value in values)
            kpi_max = max(float(value) for value in values)
            cv = (kpi_std / abs(kpi_mean)) if not math.isnan(kpi_mean) and abs(kpi_mean) > 1e-12 else 0.0
            means[policy_id][kpi] = kpi_mean
            long_rows.append(
                {
                    "policy_id": policy_id,
                    "kpi": kpi,
                    "mean": round(kpi_mean, 6),
                    "std": round(kpi_std, 6),
                    "min": round(kpi_min, 6),
                    "max": round(kpi_max, 6),
                    "cv": round(cv, 6),
                }
            )
    return long_rows, means


def improvement_table(means: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
    baseline = means.get("H0", {})
    rows: list[dict[str, Any]] = []
    for policy_id in sorted(policy for policy in means if policy != "H0"):
        row: dict[str, Any] = {"policy_id": policy_id}
        for kpi in MEAN_TABLE_KPIS:
            if kpi not in baseline or kpi not in means[policy_id]:
                continue
            base_value = baseline[kpi]
            value = means[policy_id][kpi]
            direction = KPI_DIRECTIONS[kpi]
            if kpi == "demand_fulfillment_rate":
                row["demand_fulfillment_delta"] = round(value - base_value, 6)
                continue
            if kpi == "completed_loads":
                row["completed_loads_delta"] = round(value - base_value, 6)
                continue
            if kpi == "average_available_trucks":
                row["available_trucks_delta"] = round(value - base_value, 6)
                continue
            if abs(base_value) < 1e-12:
                row[f"{kpi}_improvement_pct"] = ""
                continue
            if direction == "lower":
                improvement = (base_value - value) / abs(base_value) * 100.0
            else:
                improvement = (value - base_value) / abs(base_value) * 100.0
            row[f"{kpi}_improvement_pct"] = round(improvement, 6)
        rows.append(row)
    return rows


def rank_values(means: dict[str, dict[str, float]], kpi: str) -> dict[str, int]:
    available = [(policy, values[kpi]) for policy, values in means.items() if kpi in values]
    reverse = KPI_DIRECTIONS[kpi] == "higher"
    ordered = sorted(available, key=lambda item: item[1], reverse=reverse)
    ranks: dict[str, int] = {}
    last_value: float | None = None
    current_rank = 0
    for index, (policy, value) in enumerate(ordered, start=1):
        rounded_value = round(float(value), 9)
        if last_value is None or rounded_value != last_value:
            current_rank = index
            last_value = rounded_value
        ranks[policy] = current_rank
    return ranks


def rank_score(rank: int | str, policy_count: int) -> float:
    if rank == "" or policy_count <= 1:
        return 1.0 if rank != "" else 0.0
    return (policy_count - int(rank)) / (policy_count - 1)


def ranking_table(means: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
    ranks = {kpi: rank_values(means, kpi) for kpi in RANKING_KPIS}
    policy_count = len(means)
    rows: list[dict[str, Any]] = []
    for policy_id in sorted(means):
        composite = sum(
            COMPOSITE_WEIGHTS[kpi] * rank_score(ranks.get(kpi, {}).get(policy_id, ""), policy_count)
            for kpi in COMPOSITE_WEIGHTS
        )
        row: dict[str, Any] = {"policy_id": policy_id, "composite_score": round(composite, 6)}
        for kpi in RANKING_KPIS:
            row[f"{kpi}_rank"] = ranks.get(kpi, {}).get(policy_id, "")
            if kpi in means[policy_id]:
                row[kpi] = round(means[policy_id][kpi], 6)
        rows.append(row)
    return sorted(rows, key=lambda item: item["composite_score"], reverse=True)


def missing_kpis(means: dict[str, dict[str, float]]) -> list[str]:
    available = {kpi for metrics in means.values() for kpi in metrics}
    return [kpi for kpi in REQUIRED_KPIS if kpi not in available]


def stability_table(grouped: dict[str, list[dict[str, Any]]], means: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
    total_cost_stds = {policy: std([row.get("total_cost") for row in rows]) for policy, rows in grouped.items()}
    median_cost = statistics.median([metrics.get("total_cost", 0) for metrics in means.values()])
    median_std = statistics.median(total_cost_stds.values())
    rows: list[dict[str, Any]] = []
    for policy_id, policy_rows in grouped.items():
        cost_mean = means[policy_id].get("total_cost", 0)
        cost_std = total_cost_stds[policy_id]
        if cost_mean <= median_cost and cost_std <= median_std:
            label = "strong_and_stable"
        elif cost_mean <= median_cost:
            label = "strong_but_variable"
        elif cost_std <= median_std:
            label = "consistently_weak"
        else:
            label = "weak_and_variable"
        rows.append(
            {
                "policy_id": policy_id,
                "total_cost_mean": round(cost_mean, 6),
                "total_cost_std": round(cost_std, 6),
                "demand_fulfillment_rate_std": round(std([row.get("demand_fulfillment_rate") for row in policy_rows]), 6),
                "unmet_demand_std": round(std([row.get("unmet_demand") for row in policy_rows]), 6),
                "total_downtime_std": round(std([row.get("total_downtime") for row in policy_rows]), 6),
                "queue_time_std": round(std([row.get("queue_time") for row in policy_rows]), 6),
                "stability_label": label,
            }
        )
    return sorted(rows, key=lambda row: (row["total_cost_std"], row["total_cost_mean"]))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def md_table(rows: list[dict[str, Any]], columns: list[str], max_rows: int | None = None) -> str:
    selected = rows[:max_rows] if max_rows else rows
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in selected:
        values = [format_value(row.get(column, "")) for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def format_value(value: Any) -> str:
    if isinstance(value, float):
        if abs(value) >= 100:
            return f"{value:,.2f}"
        return f"{value:.4f}"
    return str(value)


def best_policy(means: dict[str, dict[str, float]], kpi: str) -> str:
    return best_policies(means, kpi)[0]


def best_policies(means: dict[str, dict[str, float]], kpi: str) -> list[str]:
    direction = KPI_DIRECTIONS[kpi]
    available = [(policy, metrics[kpi]) for policy, metrics in means.items() if kpi in metrics]
    if not available:
        return []
    if direction == "higher":
        target = max(value for _, value in available)
    else:
        target = min(value for _, value in available)
    return sorted(policy for policy, value in available if abs(value - target) < 1e-9)


def policy_set_label(policy_ids: list[str]) -> str:
    return " / ".join(policy_ids)


def direction_label(kpi: str) -> str:
    return "higher_is_better" if KPI_DIRECTIONS[kpi] == "higher" else "lower_is_better"


def best_value(means: dict[str, dict[str, float]], kpi: str) -> float | None:
    values = [metrics[kpi] for metrics in means.values() if kpi in metrics]
    if not values:
        return None
    return max(values) if KPI_DIRECTIONS[kpi] == "higher" else min(values)


def dashboard_stability_label(policy_id: str, stability_rows: list[dict[str, Any]]) -> str:
    if stability_rows and policy_id == stability_rows[0]["policy_id"]:
        return "총 운영비용 기준 가장 안정적"
    row = next((item for item in stability_rows if item["policy_id"] == policy_id), {})
    labels = {
        "strong_and_stable": "강하고 안정적",
        "strong_but_variable": "성과는 좋지만 변동성 있음",
        "consistently_weak": "일관되지만 성과 약함",
        "weak_and_variable": "성과 약하고 변동성 있음",
    }
    return labels.get(row.get("stability_label"), "해석 필요")


def create_dashboard_analysis(
    rows: list[dict[str, Any]],
    means: dict[str, dict[str, float]],
    improvement_rows: list[dict[str, Any]],
    ranking_rows: list[dict[str, Any]],
    stability_rows: list[dict[str, Any]],
    missing: list[str],
) -> dict[str, Any]:
    recommended = ranking_rows[0]
    best_by_kpi = []
    for kpi in DASHBOARD_BEST_KPIS:
        policies = best_policies(means, kpi)
        if not policies:
            continue
        best_by_kpi.append(
            {
                "kpi": kpi,
                "label_ko": KPI_LABELS_KO[kpi],
                "best_policy": policy_set_label(policies),
                "best_policies": policies,
                "is_tie": len(policies) > 1,
                "value": round(float(best_value(means, kpi)), 6),
                "direction": direction_label(kpi),
            }
        )

    h0_improvement = []
    for row in improvement_rows:
        h0_improvement.append(
            {
                "policy_id": row["policy_id"],
                "total_cost_improvement_pct": row.get("total_cost_improvement_pct", ""),
                "demand_fulfillment_delta": row.get("demand_fulfillment_delta", ""),
                "queue_time_reduction_pct": row.get("queue_time_improvement_pct", ""),
                "downtime_reduction_pct": row.get("total_downtime_improvement_pct", ""),
            }
        )

    stability = []
    for row in stability_rows:
        policy_id = row["policy_id"]
        stability.append(
            {
                "policy_id": policy_id,
                "total_cost_mean": row.get("total_cost_mean", ""),
                "total_cost_std": row.get("total_cost_std", ""),
                "demand_fulfillment_rate_mean": round(means.get(policy_id, {}).get("demand_fulfillment_rate", float("nan")), 6),
                "demand_fulfillment_rate_std": row.get("demand_fulfillment_rate_std", ""),
                "stability_label": row.get("stability_label", ""),
                "stability_label_ko": dashboard_stability_label(policy_id, stability_rows),
            }
        )

    queue_best = next((item for item in best_by_kpi if item["kpi"] == "queue_time"), {})
    stable_policy = stability_rows[0]["policy_id"] if stability_rows else ""
    return {
        "generated_at": datetime.now().replace(microsecond=0).isoformat(),
        "baseline_policy": "H0",
        "seed_count": len({row.get("seed") for row in rows if row.get("seed") not in (None, "")}),
        "recommended_policy": {
            "policy_id": recommended["policy_id"],
            "weighted_rank_score": recommended["composite_score"],
            "basis": "current weighted KPI rank score",
            "basis_ko": "현재 KPI 가중 순위 점수",
            "warning": "This is not a global optimum.",
            "warning_ko": "수학적으로 모든 경우의 최선임을 보장하지 않습니다.",
        },
        "best_by_kpi": best_by_kpi,
        "h0_improvement": h0_improvement,
        "stability": stability,
        "tradeoff_notes_ko": [
            f"현재 C5.1 KPI 가중치 기준 추천 정책은 {recommended['policy_id']}입니다.",
            f"{queue_best.get('best_policy', '데이터 없음')}는 대기시간 기준에서 가장 우수하거나 공동 1위입니다.",
            f"{stable_policy}는 총 운영비용 표준편차 기준으로 가장 안정적입니다." if stable_policy else "Seed 안정성 데이터가 없습니다.",
            "추천 정책은 현재 C5.1 가정과 가중치 기준의 표시용 판단이며 모든 상황의 최선임을 보장하지 않습니다.",
        ],
        "missing_kpis": [
            {
                "kpi": kpi,
                "label_ko": KPI_LABELS_KO.get(kpi, kpi),
                "reason_ko": "현재 생성된 C5.1 결과 데이터에 포함되지 않았습니다.",
            }
            for kpi in missing
        ],
        "limitations_ko": [
            "현재 비교는 3개 seed 기준의 1차 비교입니다.",
            "비용 값은 정규화된 값입니다.",
            "현재 C5.1 가정과 설정에 의존합니다.",
            "강화학습 비교는 별도 RL Lab에서 후속 진행됩니다.",
            "Drop Zone은 H0~H4 비교에 포함되지 않습니다.",
        ],
    }


def policy_interpretation(policy_id: str, means: dict[str, dict[str, float]], ranking_rows: list[dict[str, Any]]) -> dict[str, str]:
    row = next(item for item in ranking_rows if item["policy_id"] == policy_id)
    rank_pairs = [(kpi, row.get(f"{kpi}_rank")) for kpi in RANKING_KPIS if row.get(f"{kpi}_rank") != ""]
    strong = [kpi for kpi, rank in rank_pairs if rank == 1]
    weak = [kpi for kpi, rank in rank_pairs if rank and int(rank) >= 4]
    if not strong:
        strong = [min(rank_pairs, key=lambda item: int(item[1]))[0]]
    if not weak:
        weak = [max(rank_pairs, key=lambda item: int(item[1]))[0]]

    use_cases = {
        "H0": "Pure periodic PM baseline for judging improvement and fairness.",
        "H1": "Use when a simple PM due/HI-aware rule is sufficient without queue or cost optimization.",
        "H2": "Use when PM risk control is preferred but production shortfall must remain visible.",
        "H3": "Use for the current balanced recommendation because it minimizes total cost while keeping demand fulfillment high.",
        "H4": "Use when flow/backpressure behavior is the focus.",
    }
    risks = {
        "H0": "Ignores actual truck condition and demand; useful as a control, not a recommendation.",
        "H1": "Does not optimize PM timing against queue pressure or operating cost.",
        "H2": "Middle performance can be hard to justify unless risk control is the presentation focus.",
        "H3": "Higher PM cost and queue time than some alternatives; recommendation should not be framed as global optimum.",
        "H4": "Backpressure thresholds remain sensitive to the queue-state resolution.",
    }
    return {
        "strong": ", ".join(strong),
        "weak": ", ".join(weak),
        "interpretation": f"{policy_id} ranks best on {', '.join(strong)} and is weakest on {', '.join(weak)} under the current C5.1 assumptions.",
        "use_case": use_cases[policy_id],
        "risk": risks[policy_id],
    }


def create_tradeoff_notes(means: dict[str, dict[str, float]], ranking_rows: list[dict[str, Any]]) -> str:
    best_cost = best_policies(means, "total_cost")
    best_fulfillment = best_policies(means, "demand_fulfillment_rate")
    best_pm_cost = best_policies(means, "pm_cost")
    best_queue = best_policies(means, "queue_time")
    best_availability = best_policies(means, "average_available_trucks")
    best_hi = best_policies(means, "average_tire_hi")
    composite = ranking_rows[0]["policy_id"]
    return "\n".join(
        [
            "# C5.1 Policy Trade-off Notes",
            "",
            f"- Cost vs demand fulfillment: lowest total cost = `{policy_set_label(best_cost)}`; highest demand fulfillment = `{policy_set_label(best_fulfillment)}`. In the current run these are {'the same policy' if best_cost == best_fulfillment else 'different policies'}, so present both KPIs together.",
            f"- PM cost vs downtime/risk: lowest PM cost = `{policy_set_label(best_pm_cost)}`. That does not automatically produce the lowest total cost or unmet demand.",
            f"- Queue time vs completed loads: lowest average queue time = `{policy_set_label(best_queue)}`; highest completed demand = `{policy_set_label(best_fulfillment)}`. This shows queue reduction alone is not the final objective.",
            f"- Available trucks vs PM count: highest average available truck count = `{policy_set_label(best_availability)}`. Policies with more PM can still perform better on total cost if they prevent unmet-demand penalty.",
            f"- Tire/truck HI preservation vs production: best average tire HI = `{policy_set_label(best_hi)}`. The presentation recommendation should still use production and cost KPIs together.",
            f"- Composite helper: `{composite}` has the highest weighted presentation helper score. This is a display aid, not a mathematical proof of global optimality.",
            "",
        ]
    )


def create_report(
    report_path: Path,
    summary_path: Path,
    json_note: str,
    mean_rows: list[dict[str, Any]],
    means: dict[str, dict[str, float]],
    improvement_rows: list[dict[str, Any]],
    ranking_rows: list[dict[str, Any]],
    stability_rows: list[dict[str, Any]],
    tradeoff_notes: str,
    missing: list[str],
) -> None:
    mean_wide = []
    for policy_id in sorted(means):
        mean_wide.append({"policy_id": policy_id, **{kpi: round(means[policy_id].get(kpi, float("nan")), 6) for kpi in MEAN_TABLE_KPIS if kpi in means[policy_id]}})

    lines = [
        "# C5.1 Heuristic Comparison Analysis",
        "",
        "## 1. Analysis Purpose",
        "",
        "C5.1 compares H0 baseline and H1-H4 heuristics under the same virtual mine environment, seed set, demand scenario generation, and KPI definitions. This report analyzes the current generated outputs without changing simulation or policy logic.",
        "",
        "## 2. Input Data",
        "",
        f"- Summary CSV: `{summary_path.as_posix()}`",
        f"- {json_note}",
        "- Policy logs: `outputs/c5_1/logs/*.json`",
        "- Execution command: `python scripts/run_c5_1_policy_sweep.py --config configs/c5_1.yaml --policies H0 H1 H2 H3 H4 --seeds 1 2 3`",
        "",
        "## 3. KPI Summary",
        "",
        "Policy-level mean values are shown below. Full mean/std/min/max/CV values are exported in `outputs/c5_1/analysis/policy_kpi_summary.csv`.",
        "",
        "Missing required KPI columns: " + (", ".join(f"`{kpi}`" for kpi in missing) if missing else "none") + ".",
        "",
        md_table(mean_wide, ["policy_id", "total_cost", "pm_cost", "unmet_demand", "demand_fulfillment_rate", "completed_loads", "average_available_trucks", "total_downtime", "pm_count", "failure_count", "average_tire_hi", "average_truck_hi", "queue_time"]),
        "",
        "## 4. H0 Baseline Improvement",
        "",
        md_table(improvement_rows, list(improvement_rows[0].keys()) if improvement_rows else ["policy_id"]),
        "",
        "## 5. Policy Ranking",
        "",
        "Composite score is a presentation helper only. It is not a global optimum proof.",
        "",
        md_table(ranking_rows, ["policy_id", "composite_score", "total_cost_rank", "demand_fulfillment_rate_rank", "unmet_demand_rank", "total_downtime_rank", "queue_time_rank", "average_available_trucks_rank", "pm_cost_rank"]),
        "",
        "## 6. Seed Stability",
        "",
        md_table(stability_rows, ["policy_id", "total_cost_mean", "total_cost_std", "demand_fulfillment_rate_std", "unmet_demand_std", "total_downtime_std", "queue_time_std", "stability_label"]),
        "",
        "## 7. Trade-off Analysis",
        "",
        tradeoff_notes.replace("# C5.1 Policy Trade-off Notes\n\n", ""),
        "## 8. Policy-by-Policy Interpretation",
        "",
    ]
    for policy_id in ["H0", "H1", "H2", "H3", "H4"]:
        interp = policy_interpretation(policy_id, means, ranking_rows)
        lines.extend(
            [
                f"## {policy_id}. {POLICY_NAMES[policy_id]}",
                "",
                "### Strong KPI",
                f"- {interp['strong']}",
                "",
                "### Weak KPI",
                f"- {interp['weak']}",
                "",
                "### Interpretation",
                f"- {interp['interpretation']}",
                "",
                "### Best Use Case",
                f"- {interp['use_case']}",
                "",
                "### Risk",
                f"- {interp['risk']}",
                "",
            ]
        )
    recommended = ranking_rows[0]["policy_id"]
    lines.extend(
        [
            "## 9. Recommended Presentation Message",
            "",
            f"Use `{recommended}` as the recommended policy for the current C5.1 presentation because it has the strongest weighted rank-score helper and should be discussed alongside KPI-specific winners. Avoid saying it is globally optimal.",
            "",
            "## 10. Limitations",
            "",
            "- Three seeds are enough for a first comparison, not full statistical proof.",
            "- Cost values are normalized internal C5.1 values.",
            "- Results depend on the current C5.1 assumptions and simplified environment.",
            "- RL comparison is deferred to a separate RL Lab.",
            "- Drop Zone is not part of the H0-H4 heuristic comparison.",
            "",
        ]
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def create_presentation_summary(path: Path, means: dict[str, dict[str, float]], ranking_rows: list[dict[str, Any]]) -> None:
    best_rows = []
    labels = {
        "total_cost": "Total cost",
        "demand_fulfillment_rate": "Demand fulfillment",
        "unmet_demand": "Unmet demand",
        "queue_time": "Queue time",
        "pm_cost": "PM cost",
        "average_available_trucks": "Available trucks",
    }
    for kpi, label in labels.items():
        policies = best_policies(means, kpi)
        policy = policy_set_label(policies)
        best_rows.append({"KPI": label, "Best Policy": policy, "Reason": f"{KPI_DIRECTIONS[kpi]} is better; leading/tied policy set: {policy}."})
    recommended = ranking_rows[0]["policy_id"]
    lines = [
        "# C5.1 Presentation Result Summary",
        "",
        "## One-line Result",
        "",
        f"`{recommended}` is the recommended current presentation policy using the weighted rank-score helper, while KPI-specific winners should be shown to explain trade-offs.",
        "",
        "## Best Policy by KPI",
        "",
        md_table(best_rows, ["KPI", "Best Policy", "Reason"]),
        "",
        "## Recommended Policy for Presentation",
        "",
        f"- Recommended by current KPI helper: `{recommended}`",
        "- Phrase carefully: recommended under current C5.1 assumptions, not globally optimal.",
        "",
        "## Trade-off Message",
        "",
        "- Show total cost, demand fulfillment, unmet demand, queue time, PM cost, and availability together.",
        "- Explain why a policy can be strong on one KPI and weak on another.",
        "",
        "## Slide Candidate Tables",
        "",
        "- Policy KPI summary table",
        "- H0 improvement table",
        "- Ranking and composite helper table",
        "- Trade-off notes for the recommended policy",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def create_dashboard_mapping(path: Path) -> None:
    lines = [
        "# C5.1 Dashboard Analysis Mapping",
        "",
        "## Overview Cards",
        "",
        "- `total_cost` -> Total Cost / 총 운영비용",
        "- `demand_fulfillment_rate` -> Demand Fulfillment / 수요 충족률",
        "- `average_available_trucks` -> Available Trucks / 가용 트럭",
        "- `pm_cost` -> PM Cost / PM 비용",
        "- `unmet_demand` -> Unmet Demand / 미충족 수요",
        "- `queue_time` -> Queue Time / 대기시간",
        "",
        "## Policy Comparison Page",
        "",
        "- Source snapshot: `ui/operator_dashboard/public/c5_1/policy_comparison.json`",
        "- Analysis source: `outputs/c5_1/analysis/policy_kpi_summary.csv`",
        "- Purpose: show H0-H4 KPI table and policy-level comparison.",
        "- Presentation interpretation: use this page to show that policies are compared under the same C5.1 environment and KPI definitions.",
        "",
        "## Heuristic Analysis Page",
        "",
        "- Source snapshot: `ui/operator_dashboard/public/c5_1/dashboard_analysis.json`",
        "- `recommended_policy` -> 추천 정책 card",
        "- `best_by_kpi` -> KPI별 우수 정책 cards",
        "- `h0_improvement` -> H0 대비 개선율 table",
        "- `stability` -> Seed 안정성 table",
        "- `tradeoff_notes_ko` -> Trade-off 해석 panel",
        "- `missing_kpis` -> 누락 KPI warning",
        "- `limitations_ko` -> 분석 한계 section",
        "",
        "## PM Worker App Link",
        "",
        "- Source snapshot: `ui/pm_worker_app/public/c5_1/work_orders.json`",
        "- Purpose: show that selected policy results can be converted into PM Work Order data.",
        "- Presentation interpretation: this is an execution mock, not a native Android production build.",
        "",
        "## Warning",
        "",
        "Composite score is a presentation helper. Do not label it as a mathematical optimum.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def create_charts(out_dir: Path, means: dict[str, dict[str, float]]) -> list[str]:
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover - optional dependency path
        return [f"matplotlib unavailable, skipped charts: {exc}"]

    figure_dir = out_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    policies = sorted(means)

    def bar_chart(kpi: str, filename: str, title: str) -> None:
        values = [means[policy].get(kpi, 0) for policy in policies]
        plt.figure(figsize=(7, 4))
        plt.bar(policies, values)
        plt.title(title)
        plt.xlabel("Policy")
        plt.ylabel(kpi)
        plt.tight_layout()
        plt.savefig(figure_dir / filename)
        plt.close()

    bar_chart("total_cost", "fig_policy_total_cost.png", "Policy Total Cost")
    bar_chart("demand_fulfillment_rate", "fig_policy_demand_fulfillment.png", "Policy Demand Fulfillment")
    bar_chart("unmet_demand", "fig_policy_unmet_demand.png", "Policy Unmet Demand")
    bar_chart("queue_time", "fig_policy_queue_time.png", "Policy Queue Time")

    plt.figure(figsize=(6, 4))
    for policy in policies:
        plt.scatter(means[policy].get("total_cost", 0), means[policy].get("demand_fulfillment_rate", 0), label=policy)
    plt.title("Cost vs Demand Fulfillment")
    plt.xlabel("total_cost")
    plt.ylabel("demand_fulfillment_rate")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figure_dir / "fig_policy_tradeoff_cost_vs_fulfillment.png")
    plt.close()
    return [f"charts written to {figure_dir}"]


def main() -> None:
    args = parse_args()
    summary_path = Path(args.summary).resolve()
    out_dir = Path(args.out_dir).resolve()
    summary_rows = read_summary(summary_path)
    json_note = summary_json_note(summary_path, summary_rows)
    rows = enrich_rows(summary_rows, log_dir_from_summary(summary_path))
    grouped = group_by_policy(rows)
    kpi_rows, means = aggregate_policy_kpis(grouped)
    improvement_rows = improvement_table(means)
    ranking_rows = ranking_table(means)
    stability_rows = stability_table(grouped, means)
    tradeoff_notes = create_tradeoff_notes(means, ranking_rows)
    missing = missing_kpis(means)
    dashboard_analysis = create_dashboard_analysis(rows, means, improvement_rows, ranking_rows, stability_rows, missing)

    write_csv(out_dir / "policy_kpi_summary.csv", kpi_rows)
    write_csv(out_dir / "h0_improvement_table.csv", improvement_rows)
    write_csv(out_dir / "policy_ranking_table.csv", ranking_rows)
    write_csv(out_dir / "policy_stability_table.csv", stability_rows)
    (out_dir / "policy_tradeoff_notes.md").write_text(tradeoff_notes, encoding="utf-8")
    write_json(out_dir / "dashboard_analysis.json", dashboard_analysis)

    create_report(Path(args.report), summary_path, json_note, kpi_rows, means, improvement_rows, ranking_rows, stability_rows, tradeoff_notes, missing)
    create_presentation_summary(Path(args.presentation), means, ranking_rows)
    create_dashboard_mapping(Path(args.dashboard))
    for message in create_charts(out_dir, means):
        print(message)

    print(f"Analysis outputs: {out_dir}")
    print(f"Report: {Path(args.report).resolve()}")


if __name__ == "__main__":
    main()
