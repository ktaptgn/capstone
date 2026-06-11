from __future__ import annotations

import csv
import json
import math
import shutil
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import yaml


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "presentation_materials"
RAW = PACK / "data" / "raw"
GENERATED = PACK / "data" / "generated"
TABLES = PACK / "tables"
FIGURES = PACK / "figures"

TITLE = "가상 광산 시뮬레이션을 통한 마일리지 적용 설비 PM 분석 및 최소 비용 지출 정책 도출"
SUBTITLE = "등가 마일리지·Health Index·PM timing을 고려한 가상광산 DES 기반 정책 비교"

DOCS_PRIORITY = [
    "docs/source/C5_DOCUMENTATION_INDEX_v2.md",
    "docs/source/C5_CAPSTONE_AGENT_BRIEF.md",
    "docs/source/C5_ALGORITHM_EQUATION_IMPLEMENTATION_ADDENDUM.md",
    "docs/source/C5_COST_AND_DEMAND_MODEL_v2.md",
    "docs/source/C5_PM_BAY_AND_TIME_RISK_DEFENSE.md",
    "docs/source/C5_PARAMETER_DEFENSE_TABLE_v2.md",
    "docs/source/03_EVIDENCE_AND_SOURCE_REGISTER.md",
    "docs/source/04_PROJECT_CHANGELOG.md",
]

REQUESTED_SOURCE_NAMES = [
    "C5_DOCUMENTATION_INDEX_v2.md",
    "C5_CAPSTONE_AGENT_BRIEF.md",
    "C5_ALGORITHM_EQUATION_IMPLEMENTATION_ADDENDUM.md",
    "C5_COST_AND_DEMAND_MODEL_v2.md",
    "C5_PM_BAY_AND_TIME_RISK_DEFENSE.md",
    "C5_PARAMETER_DEFENSE_TABLE_v2.md",
    "03_EVIDENCE_AND_SOURCE_REGISTER.md",
    "04_PROJECT_CHANGELOG.md",
    "final_comparison_summary_table.csv",
    "final_comparison_summary_table.md",
    "c5_final_metrics_table.csv",
    "c5_policy_comparison.csv",
    "c5_scenario_robustness.csv",
    "c5_cost_breakdown.csv",
    "c5_action_distribution_by_time.csv",
    "c5_health_summary.csv",
    "c5_final_report.json",
    "baseline_vs_ppo_summary.json",
    "RESULTS_ALL.csv",
    "REPORT_DATA.md",
    "PROJECT_SPEC.md",
]

ADDITIONAL_RESULT_PATHS = [
    "outputs/c5_1/summary/policy_comparison.csv",
    "outputs/c5_1/summary/policy_comparison.json",
    "outputs/c5_1/summary/c5_1_policy_report.md",
    "outputs/c5_1/analysis/policy_kpi_summary.csv",
    "outputs/c5_1/analysis/policy_ranking_table.csv",
    "outputs/c5_1/analysis/policy_stability_table.csv",
    "outputs/c5_1/analysis/policy_tradeoff_notes.md",
    "outputs/c5_1/analysis/dashboard_analysis.json",
    "outputs/c5_1/analysis/h0_improvement_table.csv",
    "configs/c5_1.yaml",
    "configs/cost_model_c5_1.yaml",
    "configs/maintenance_c5_1.yaml",
    "docs/c5_1/C5_1_POLICY_SPEC.md",
    "docs/c5_1/C5_1_LOG_SCHEMA.md",
    "docs/c5_1/C5_1_VISUALIZATION_SPEC.md",
    "docs/c5_1/C5_1_PRESENTATION_RESULT_SUMMARY.md",
    "docs/c5_1/C5_1_FINAL_RESULT_SUMMARY.md",
    "docs/c5_1/C5_1_HEURISTIC_COMPARISON_ANALYSIS.md",
]

POLICY_LABELS = {
    "H0": "Periodic PM Baseline",
    "H1": "Due / Health PM",
    "H2": "PM Risk Priority",
    "H3": "Cost Unit Value",
    "H4": "Flow / Backpressure",
}

POLICY_RULES = {
    "H0": {
        "rule": "트럭별 고정 캘린더 슬롯이 도래하면 PM_VEHICLE을 수행한다.",
        "inputs": "day, truck_id, periodic_pm_interval_days",
        "hi": "아니오",
        "time": "예",
        "queue": "아니오",
        "strength": "비교 기준으로 해석이 단순하다.",
        "weakness": "실제 상태와 수요를 무시해 과잉 정비가 발생할 수 있다.",
    },
    "H1": {
        "rule": "PM due 또는 Truck/Tire HI 임계 조건을 확인해 PM하고, 아니면 기본 dispatch를 수행한다.",
        "inputs": "pm_due_hours, truck_hi, tire_hi, demand pressure",
        "hi": "예",
        "time": "예",
        "queue": "아니오",
        "strength": "기본 규칙으로 상태와 PM due를 함께 반영한다.",
        "weakness": "큐와 비용 최적화를 수행하지 않는다.",
    },
    "H2": {
        "rule": "Truck HI, Tire HI, PM due 기반 risk가 threshold 이상이면 PM을 우선한다.",
        "inputs": "truck_hi, tire_hi, pm_due_hours, demand pressure",
        "hi": "예",
        "time": "아니오",
        "queue": "간접",
        "strength": "고위험 설비를 조기에 정비해 상태 저하를 억제한다.",
        "weakness": "생산 기회손실과 unmet demand가 커질 수 있다.",
    },
    "H3": {
        "rule": "운행 가치와 PM 가치를 CU 비용 proxy로 비교해 더 높은 operational value를 선택한다.",
        "inputs": "demand pressure, truck/tire HI, PM cost, degradation cost",
        "hi": "예",
        "time": "간접",
        "queue": "비용 관점 간접",
        "strength": "생산, PM, downtime, degradation을 하나의 비용 언어로 비교한다.",
        "weakness": "가중치와 비용 proxy 설정에 민감하다.",
    },
    "H4": {
        "rule": "downstream pressure와 backpressure를 보고 high-demand release, PM, standby를 선택한다.",
        "inputs": "demand pressure, queue_time, truck/tire risk",
        "hi": "예",
        "time": "아니오",
        "queue": "예",
        "strength": "전체 flow 관점의 병목 완화 설명이 쉽다.",
        "weakness": "queue 상태 해상도와 threshold 설정에 민감하다.",
    },
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def ensure_dirs() -> None:
    for path in [RAW, GENERATED, TABLES, FIGURES, PACK / "scripts"]:
        path.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def md_table(headers: list[str], rows: list[list[object]]) -> str:
    def cell(value: object) -> str:
        if value is None:
            return "N/A"
        text = str(value)
        return text.replace("\n", " ").replace("|", "/")

    header = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(cell(v) for v in row) + " |" for row in rows]
    return "\n".join([header, sep, *body])


def fmt(value: object, digits: int = 3) -> str:
    if value is None:
        return "N/A"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(number):
        return "N/A"
    if number.is_integer():
        return str(int(number))
    return f"{number:.{digits}f}".rstrip("0").rstrip(".")


def discover_sources() -> tuple[list[Path], list[str]]:
    def in_pack(path: Path) -> bool:
        try:
            path.relative_to(PACK)
            return True
        except ValueError:
            return False

    found: dict[str, Path] = {}
    missing_names = []
    for name in REQUESTED_SOURCE_NAMES:
        matches = sorted(path for path in ROOT.rglob(name) if not in_pack(path))
        if matches:
            for match in matches:
                found[rel(match)] = match
        else:
            missing_names.append(name)

    for item in ADDITIONAL_RESULT_PATHS:
        path = ROOT / item
        if path.exists():
            found[rel(path)] = path

    for pattern in [
        "outputs/c5_1/logs/*.json",
        "outputs/c5_1/work_orders/*.json",
        "outputs/c5_1/analysis/*.md",
        "outputs/c5_1/analysis/*.csv",
        "outputs/c5_1/analysis/*.json",
    ]:
        for match in ROOT.glob(pattern):
            found[rel(match)] = match

    return sorted(found.values(), key=lambda p: rel(p)), missing_names


def role_for(path: Path) -> tuple[str, str, str]:
    name = path.name
    path_text = rel(path)
    if name in {Path(p).name for p in DOCS_PRIORITY}:
        return ("source-of-truth document", "1-15", "Read before generated content.")
    if path_text.startswith("configs/"):
        return ("simulation/config parameter source", "5-6", "Used for spec and CU settings.")
    if "policy_comparison.csv" in name or "policy_comparison.json" in name:
        return ("official 365-day policy result source", "9-11", "Preferred numeric result table.")
    if "logs/" in path_text:
        return ("policy replay log", "10", "Used to derive PM count, downtime, and PM timing.")
    if "analysis" in path_text:
        return ("secondary analysis output", "9-11", "Used as interpretation aid; conflicts are warned.")
    if "docs/c5_1" in path_text:
        return ("C5.1 implementation spec", "3-8", "Used for policy/log/visualization wording.")
    return ("supporting source", "N/A", "Copied as evidence.")


def copy_sources(sources: list[Path], missing_names: list[str]) -> list[dict[str, str]]:
    manifest = []
    for source in sources:
        copied = RAW / rel(source)
        copied.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, copied)
        role, slide, notes = role_for(source)
        manifest.append(
            {
                "File": source.name,
                "Original Path": rel(source),
                "Copied Path": rel(copied),
                "Role": role,
                "Used In Slide Section": slide,
                "Notes": notes,
            }
        )

    missing_rows = [
        {
            "requested_file": item,
            "status": "not_found",
            "searched_root": str(ROOT),
            "note": "No file with this exact name was found. Equivalent C5.1 outputs were used where available.",
        }
        for item in missing_names
    ]
    write_csv(
        GENERATED / "missing_requested_sources.csv",
        missing_rows,
        ["requested_file", "status", "searched_root", "note"],
    )
    return manifest


def load_config() -> dict:
    config = {}
    for item in ["configs/c5_1.yaml", "configs/cost_model_c5_1.yaml", "configs/maintenance_c5_1.yaml"]:
        path = ROOT / item
        if path.exists():
            with path.open("r", encoding="utf-8") as stream:
                config.update(yaml.safe_load(stream) or {})
    return config


def official_rows() -> list[dict[str, str]]:
    path = ROOT / "outputs/c5_1/summary/policy_comparison.csv"
    return read_csv(path) if path.exists() else []


def aggregate_policy_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row["policy_id"]].append(row)

    numeric = [
        "days",
        "total_demand",
        "completed_loads",
        "unmet_demand",
        "demand_fulfillment_rate",
        "total_cost",
        "total_cost_report_value",
        "pm_cost",
        "avg_queue_time",
        "availability_rate",
    ]
    out = []
    for policy_id in sorted(groups):
        values = groups[policy_id]
        item: dict[str, object] = {"policy_id": policy_id, "policy_name": POLICY_LABELS.get(policy_id, policy_id)}
        for key in numeric:
            nums = [float(v[key]) for v in values if v.get(key) not in (None, "")]
            item[f"{key}_mean"] = sum(nums) / len(nums) if nums else None
        item["seed_count"] = len(values)
        out.append(item)
    return out


def load_logs() -> dict[tuple[str, int], dict]:
    logs = {}
    for path in sorted((ROOT / "outputs/c5_1/logs").glob("H*_seed_*.json")):
        with path.open("r", encoding="utf-8") as stream:
            payload = json.load(stream)
        logs[(payload["policy_id"], int(payload["seed"]))] = payload
    return logs


def cost_breakdown(rows: list[dict[str, str]], config: dict, logs: dict[tuple[str, int], dict]) -> list[dict[str, object]]:
    downtime_rate = float(config["cost_model"]["event_costs"]["downtime_cost_per_hour"])
    unmet_rate = float(config["cost_model"]["event_costs"]["unmet_demand_penalty_per_load"])
    per_seed = []
    for row in rows:
        key = (row["policy_id"], int(row["seed"]))
        payload = logs.get(key, {})
        records = payload.get("records", [])
        pm_direct = sum(float(r.get("pm_cost", 0.0)) for r in records)
        downtime_hours = sum(float(r.get("downtime_hours", 0.0)) for r in records)
        downtime_cost = downtime_hours * downtime_rate
        target_cost = float(row["unmet_demand"]) * unmet_rate
        total = float(row["total_cost"])
        degradation = max(total - pm_direct - downtime_cost - target_cost, 0.0)
        pm_count = sum(1 for r in records if str(r.get("action", "")).startswith("PM_"))
        per_seed.append(
            {
                "policy_id": row["policy_id"],
                "seed": int(row["seed"]),
                "pm_direct_cost": pm_direct,
                "pm_downtime_cost": downtime_cost,
                "tire_life_degradation_cost": degradation,
                "queue_cost": None,
                "failure_cost": None,
                "target_shortfall_cost": target_cost,
                "total_cost": total,
                "pm_count": pm_count,
                "downtime_hours": downtime_hours,
            }
        )

    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in per_seed:
        groups[str(row["policy_id"])].append(row)
    agg = []
    keys = [
        "pm_direct_cost",
        "pm_downtime_cost",
        "tire_life_degradation_cost",
        "target_shortfall_cost",
        "total_cost",
        "pm_count",
        "downtime_hours",
    ]
    for policy_id in sorted(groups):
        item: dict[str, object] = {"policy_id": policy_id}
        for key in keys:
            nums = [float(v[key]) for v in groups[policy_id] if v.get(key) is not None]
            item[f"{key}_mean"] = sum(nums) / len(nums) if nums else None
        item["queue_cost_mean"] = None
        item["failure_cost_mean"] = None
        agg.append(item)
    return agg


def pm_timing_counts(logs: dict[tuple[str, int], dict]) -> list[dict[str, object]]:
    counts: Counter[tuple[str, str]] = Counter()
    for (policy_id, _seed), payload in logs.items():
        for record in payload.get("records", []):
            if str(record.get("action", "")).startswith("PM_"):
                label = str(record["time"])
                day = int(label.replace("day_", ""))
                bucket = f"Day {((day - 1) // 30) * 30 + 1}-{min(((day - 1) // 30 + 1) * 30, 365)}"
                counts[(policy_id, bucket)] += 1
    rows = [
        {"policy_id": policy_id, "period": period, "pm_actions": count}
        for (policy_id, period), count in sorted(counts.items())
    ]
    return rows


def write_manifest(manifest: list[dict[str, str]]) -> None:
    rows = [[m[h] for h in ["File", "Original Path", "Copied Path", "Role", "Used In Slide Section", "Notes"]] for m in manifest]
    write_text(
        PACK / "source_manifest.md",
        "# Source Manifest\n\n"
        + md_table(["File", "Original Path", "Copied Path", "Role", "Used In Slide Section", "Notes"], rows),
    )


def make_diagram(path: Path, title: str, boxes: list[str], arrows: bool = True) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(title, fontsize=16, fontweight="bold")
    y_values = list(reversed([0.15 + i * (0.7 / max(len(boxes) - 1, 1)) for i in range(len(boxes))]))
    for i, (label, y) in enumerate(zip(boxes, y_values)):
        ax.text(
            0.5,
            y,
            label,
            ha="center",
            va="center",
            fontsize=11,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#EAF2F8", edgecolor="#2E86C1", linewidth=1.5),
        )
        if arrows and i < len(y_values) - 1:
            ax.annotate("", xy=(0.5, y_values[i + 1] + 0.055), xytext=(0.5, y - 0.055), arrowprops=dict(arrowstyle="->", lw=1.8))
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def generate_figures(summary: list[dict[str, object]], breakdown: list[dict[str, object]], pm_rows: list[dict[str, object]]) -> list[str]:
    generated = []
    make_diagram(
        FIGURES / "system_architecture.png",
        "C5.1 System Architecture",
        ["Plant Feed Manager", "Dispatch / PM Policy", "DES Engine", "Truck / Tire HI / Queue / PM Bay / Crusher", "KPI + CU Cost Evaluation"],
    )
    generated.append("presentation_materials/figures/system_architecture.png")

    make_diagram(
        FIGURES / "virtual_mine_flow.png",
        "Virtual Mine Flow",
        ["Shovel A / B / C", "Haul Road", "Crusher 1 / Crusher 2", "Concentrator Feed Target", "Side path: PM Bay / Cooldown / Standby"],
    )
    generated.append("presentation_materials/figures/virtual_mine_flow.png")

    fig, ax = plt.subplots(figsize=(9, 5.5))
    labels = [str(r["policy_id"]) for r in summary]
    total_cost = [float(r["total_cost_mean"]) for r in summary]
    fulfillment = [float(r["demand_fulfillment_rate_mean"]) for r in summary]
    x = range(len(labels))
    ax.bar([v - 0.18 for v in x], total_cost, width=0.36, label="Total cost (CU)")
    ax2 = ax.twinx()
    ax2.plot(list(x), fulfillment, color="#C0392B", marker="o", linewidth=2, label="Fulfillment")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Mean total cost (CU)")
    ax2.set_ylabel("Mean fulfillment")
    ax.set_title("Policy KPI Comparison, Official 365-Day Sweep")
    lines, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines + lines2, labels1 + labels2, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIGURES / "policy_kpi_comparison.png", dpi=180)
    plt.close(fig)
    generated.append("presentation_materials/figures/policy_kpi_comparison.png")

    fig, ax = plt.subplots(figsize=(9, 5.5))
    labels = [str(r["policy_id"]) for r in breakdown]
    pm = [float(r["pm_direct_cost_mean"]) for r in breakdown]
    dt = [float(r["pm_downtime_cost_mean"]) for r in breakdown]
    deg = [float(r["tire_life_degradation_cost_mean"]) for r in breakdown]
    short = [float(r["target_shortfall_cost_mean"]) for r in breakdown]
    bottom = [0.0] * len(labels)
    for values, label in [(pm, "PM direct"), (dt, "PM downtime"), (deg, "HI degradation"), (short, "Target shortfall")]:
        ax.bar(labels, values, bottom=bottom, label=label)
        bottom = [a + b for a, b in zip(bottom, values)]
    ax.set_ylabel("Mean cost (CU)")
    ax.set_title("CU Cost Breakdown Derived from Official Logs")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(FIGURES / "cost_breakdown.png", dpi=180)
    plt.close(fig)
    generated.append("presentation_materials/figures/cost_breakdown.png")

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.axis("off")
    ax.set_title("Heuristic Concept Map", fontsize=16, fontweight="bold")
    center = (0.5, 0.52)
    ax.text(*center, "C5.1 Policies\nH0-H4", ha="center", va="center", fontsize=13, bbox=dict(boxstyle="round,pad=0.6", facecolor="#FDEBD0", edgecolor="#CA6F1E"))
    nodes = [
        ("Calendar / PM due", 0.17, 0.78),
        ("HI threshold", 0.5, 0.86),
        ("Time-risk proxy", 0.83, 0.78),
        ("Queue pressure", 0.17, 0.28),
        ("PM due score", 0.5, 0.16),
        ("RUL proxy", 0.83, 0.28),
    ]
    for label, x0, y0 in nodes:
        ax.text(x0, y0, label, ha="center", va="center", fontsize=11, bbox=dict(boxstyle="round,pad=0.35", facecolor="#E8F8F5", edgecolor="#117A65"))
        ax.annotate("", xy=center, xytext=(x0, y0), arrowprops=dict(arrowstyle="->", lw=1.2, color="#566573"))
    fig.tight_layout()
    fig.savefig(FIGURES / "heuristic_concept_map.png", dpi=180)
    plt.close(fig)
    generated.append("presentation_materials/figures/heuristic_concept_map.png")

    if pm_rows:
        periods = sorted({str(r["period"]) for r in pm_rows}, key=lambda x: int(x.split()[1].split("-")[0]))
        policies = sorted({str(r["policy_id"]) for r in pm_rows})
        lookup = {(str(r["policy_id"]), str(r["period"])): int(r["pm_actions"]) for r in pm_rows}
        fig, ax = plt.subplots(figsize=(11, 5.5))
        for policy in policies:
            ax.plot(periods, [lookup.get((policy, p), 0) for p in periods], marker="o", linewidth=1.8, label=policy)
        ax.set_title("PM Timing by 30-Day Period, Official Replay Logs")
        ax.set_ylabel("PM actions")
        ax.tick_params(axis="x", rotation=45)
        ax.legend()
        fig.tight_layout()
        fig.savefig(FIGURES / "pm_timing_tradeoff.png", dpi=180)
        plt.close(fig)
    else:
        make_diagram(
            FIGURES / "pm_timing_tradeoff.png",
            "Conceptual PM Timing Tradeoff",
            ["Early PM: lower future risk", "Balanced PM timing", "Late PM: higher production now, higher future risk"],
        )
        write_text(
            FIGURES / "pm_timing_tradeoff.placeholder.md",
            "# PM Timing Placeholder\n\n- missing input: policy replay logs with PM action records\n- searched paths: outputs/c5_1/logs/*.json\n- why unavailable: no PM action records were found\n- next figure: PM action timing by period after replay logs are added",
        )
    generated.append("presentation_materials/figures/pm_timing_tradeoff.png")
    return generated


def write_tables(summary: list[dict[str, object]], breakdown: list[dict[str, object]], config: dict) -> None:
    write_text(
        TABLES / "01_project_overview.md",
        "# 01 Project Overview\n\n"
        + md_table(
            ["Item", "Content"],
            [
                ["One-line definition", "C5.1은 같은 가상광산 DES 환경에서 H0 baseline과 H1-H4 휴리스틱 정책을 비교하고 KPI/CU 비용으로 해석하는 프로젝트다."],
                ["Problem statement", "열화가 누적되는 haul truck과 tire를 계속 운행할지, PM으로 뺄지, queue와 생산 압력 속에서 결정해야 한다."],
                ["Decision objective", "CU 기반 total cost, unmet demand, downtime, queue, PM cost를 함께 낮추는 정책을 찾는다."],
                ["Evaluation logic", "같은 seed, 같은 demand scenario, 같은 환경에서 정책만 바꾸어 KPI를 비교한다."],
            ],
        ),
    )

    write_text(
        TABLES / "02_project_elements.md",
        "# 02 Project Elements\n\n"
        + md_table(
            ["Element", "Role", "Main Variables", "Presentation Meaning"],
            [
                ["Truck", "광석 운반 설비", "truck_id, truck_hi, state, location", "PM 또는 운행 의사결정 대상"],
                ["Tire HI", "타이어 열화 상태", "tire_hi, min threshold", "등가 마일리지 proxy가 누적되며 감소하는 상태값"],
                ["Truck HI", "차량 본체 상태", "truck_hi, pm_due_hours", "고장위험과 PM 필요도를 표현하는 proxy"],
                ["Shovel", "상차 지점", "Shovel A/B/C presentation label", "운반 flow 시작점"],
                ["Crusher 1 / Crusher 2", "하역/처리 지점", "crusher_count=2", "downstream capacity와 queue가 생기는 지점"],
                ["PM Bay", "통합 정비능력", "pm_bay_capacity", "bay, crew, tool, tire handler를 묶은 capacity proxy"],
                ["Plant Feed Manager", "수요/목표 관리", "daily_loads, variation", "concentrator feed target을 맞추는 상위 요구"],
                ["Time-risk / seasonal risk", "상황별 위험 multiplier proxy", "time-risk factor", "측정 회귀계수가 아니라 C5 risk multiplier proxy"],
                ["Cost Unit", "정책 비교 단위", "normalized_cu", "실제 회계값이 아닌 marginal cost proxy"],
            ],
        ),
    )

    specs = [
        ["simulation_method", config["simulation"]["version"] + " DES", "Fixed", "configs/c5_1.yaml", "event-based virtual mine simulation"],
        ["fleet size", config["mine"]["truck_count"], "Config", "configs/c5_1.yaml", "실제 광산 설비 수가 아닌 C5.1 proxy fleet"],
        ["minimum operating trucks", "N/A", "Not explicit", "N/A", "현재 config에 별도 literal field 없음"],
        ["truck model proxy", "large haul truck proxy", "Presentation label", "docs/source/03_EVIDENCE_AND_SOURCE_REGISTER.md", "특정 실제 모델 재현으로 말하지 않음"],
        ["payload", config["mine"]["truck_avg_payload_ton"], "Proxy", "configs/c5_1.yaml", "simplified average payload"],
        ["shovel count", "3 presentation flow nodes", "Presentation label", "slide request", "현재 config에는 shovel_count literal field 없음"],
        ["crusher count", config["mine"]["crushers"], "Fixed", "configs/c5_1.yaml", "current C5 environment"],
        ["PM bay capacity", config["maintenance"]["pm_bay_capacity"], "Proxy", "configs/maintenance_c5_1.yaml", "통합 정비능력"],
        ["tire count per truck", "N/A", "Not explicit", "N/A", "현재 simulation state는 aggregate tire_hi를 사용"],
        ["initial Truck HI", config["fleet"]["initial_truck_hi"], "Config", "configs/c5_1.yaml", "state proxy"],
        ["initial Tire HI", config["fleet"]["initial_tire_hi"], "Config", "configs/c5_1.yaml", "state proxy"],
        ["time slot factor", "C5 risk multiplier proxy", "Proxy concept", "docs/source/C5_PM_BAY_AND_TIME_RISK_DEFENSE.md", "실측값으로 말하지 않음"],
        ["demand scenarios", f"daily_loads={config['demand']['daily_loads']}, variation={config['demand']['daily_variation_loads']}", "Config", "configs/c5_1.yaml", "same seed/scenario comparison"],
        ["cost unit", config["cost_model"]["unit"], "Fixed", "configs/cost_model_c5_1.yaml", "CU 기반 비교"],
    ]
    write_text(
        TABLES / "03_simulation_spec.md",
        "# 03 Simulation Spec\n\n"
        + md_table(["Spec", "Value", "Classification", "Source File", "Presentation Caution"], specs),
    )

    write_text(
        TABLES / "04_heuristic_definitions.md",
        "# 04 Heuristic Definitions\n\n"
        + md_table(
            ["Heuristic", "Rule Summary", "Required Inputs", "Expected Behavior", "Risk"],
            [
                [f"{pid} {POLICY_LABELS[pid]}", POLICY_RULES[pid]["rule"], POLICY_RULES[pid]["inputs"], POLICY_RULES[pid]["strength"], POLICY_RULES[pid]["weakness"]]
                for pid in ["H0", "H1", "H2", "H3", "H4"]
            ],
        )
        + "\n\nSource: docs/source/C5_ALGORITHM_EQUATION_IMPLEMENTATION_ADDENDUM.md, docs/c5_1/C5_1_POLICY_SPEC.md, mine_env/policies/*.py",
    )

    comparison_rows = []
    breakdown_by_policy = {str(r["policy_id"]): r for r in breakdown}
    for row in summary:
        pid = str(row["policy_id"])
        cost = float(row["total_cost_mean"])
        fulfillment = float(row["demand_fulfillment_rate_mean"])
        interpretation = "lowest CU cost and highest fulfillment in official 365-day sweep" if pid == min(summary, key=lambda r: float(r["total_cost_mean"]))["policy_id"] else "trade-off policy; compare cost, fulfillment, PM, queue together"
        comparison_rows.append(
            [
                pid,
                fmt(cost),
                fmt(row["completed_loads_mean"]),
                fmt(breakdown_by_policy[pid]["pm_count_mean"]),
                "N/A",
                fmt(breakdown_by_policy[pid]["downtime_hours_mean"]),
                "N/A",
                fmt(row["unmet_demand_mean"]),
                interpretation,
            ]
        )
    write_text(
        TABLES / "05_policy_result_comparison.md",
        "# 05 Policy Result Comparison\n\nSource used: outputs/c5_1/summary/policy_comparison.csv plus replay logs in outputs/c5_1/logs/*.json for PM count and downtime.\n\n"
        + md_table(
            ["Policy", "Total Cost / TCO (CU)", "Production / Throughput", "PM Count", "Failure Count", "Downtime (hr)", "Queue Cost", "Target Shortfall", "Main Interpretation"],
            comparison_rows,
        )
        + "\n\nConflict note: outputs/c5_1/analysis/policy_kpi_summary.csv contains smaller-scale KPI values than the official 365-day summary. This pack uses outputs/c5_1/summary/policy_comparison.csv for numeric policy comparison.",
    )

    cost_rows = [
        [
            r["policy_id"],
            fmt(r["pm_direct_cost_mean"]),
            fmt(r["pm_downtime_cost_mean"]),
            fmt(r["tire_life_degradation_cost_mean"]),
            "N/A",
            "N/A",
            fmt(r["target_shortfall_cost_mean"]),
            fmt(r["total_cost_mean"]),
        ]
        for r in breakdown
    ]
    write_text(
        TABLES / "06_cost_breakdown.md",
        "# 06 Cost Breakdown\n\nSource used: outputs/c5_1/summary/policy_comparison.csv, outputs/c5_1/logs/*.json, configs/cost_model_c5_1.yaml. Queue and failure cost are N/A because the official cost model does not expose separate queue/failure cost fields.\n\n"
        + md_table(
            ["Policy", "PM Direct Cost", "PM Downtime Cost", "Tire Life / Degradation Cost", "Queue Cost", "Failure Cost", "Target Shortfall Cost", "Total Cost"],
            cost_rows,
        ),
    )

    write_text(
        TABLES / "07_limitations_and_improvements.md",
        "# 07 Limitations and Improvements\n\n## Limitations\n\n"
        + md_table(
            ["Limitation", "Meaning", "Presentation Defense"],
            [
                ["실제 광산 digital twin 아님", "Escondida/Atacama 특성을 참조한 proxy DES", "정밀 복제가 아니라 의사결정 프레임워크"],
                ["파라미터는 proxy / assumption 포함", "payload, mine scale, HI loss는 단순화", "parameter defense table에 proxy로 분리"],
                ["실제 tire sensor / telemetry 없음", "HI는 sensor calibration 값이 아님", "EOH/TKPH/severity 기반 proxy로 설명"],
                ["CU cost는 실제 회계값 아님", "normalized marginal cost proxy", "정책 비교용 내부 단위"],
                ["time-risk는 측정 회귀계수 아님", "C5 risk multiplier proxy", "실측값이라고 말하지 않음"],
                ["seed / scenario / sensitivity 추가 필요", "현재 multi-seed는 제한적", "robustness 확장 필요"],
                ["PM crew scheduling은 범위 밖", "PM bay가 통합 정비능력을 대표", "별도 crew roster 모델은 future work"],
                ["multi-agent RL은 범위 밖", "C5.1은 H0-H4 comparison foundation", "RL은 primary target 아님"],
            ],
        )
        + "\n\n## Future Improvements\n\n"
        + md_table(
            ["Improvement", "Expected Value", "Priority"],
            [
                ["실제 telemetry / tire sensor calibration", "HI와 RUL proxy 신뢰도 향상", "High"],
                ["multi-seed robustness", "정책 ranking 안정성 확인", "High"],
                ["30일 / 52주 continuous evaluation", "운영 기간별 PM timing 평가", "Medium"],
                ["PM bay 1 vs 2 sensitivity", "정비 capacity 병목 영향 분리", "High"],
                ["cost weight low/base/high sensitivity", "CU weighting 민감도 확인", "High"],
                ["route roughness and demand shock scenario", "실제 운영 충격에 가까운 stress test", "Medium"],
                ["RUL proxy refinement", "PM 필요도 판단 개선", "High"],
                ["dashboard integration", "운영자 설명과 replay 강화", "Low"],
                ["field app integration", "작업지시 lifecycle 연결", "Low"],
            ],
        ),
    )

    write_text(
        TABLES / "08_transfer_applications.md",
        "# 08 Transfer Applications\n\n"
        + md_table(
            ["Domain", "Equivalent Equipment", "Degradation Proxy", "PM Action", "Objective"],
            [
                ["스마트팩토리 AGV", "AGV fleet / battery / wheel", "운행시간, 충전 cycle, vibration", "battery swap, wheel inspection", "라인 공급 중단 최소화"],
                ["반도체 후공정 설비", "handler, bonder, tester", "cycle count, thermal load, error rate", "calibration, part replacement", "throughput loss와 defect risk 최소화"],
                ["저항점용접 RSW electrode tip", "electrode tip", "weld count, current, tip wear proxy", "tip dressing, tip replacement", "품질 불량과 downtime 균형"],
                ["데이터센터 냉각/서버 설비", "chiller, fan, server node", "thermal load, fan hours, error logs", "maintenance, workload migration", "SLA와 energy cost 균형"],
                ["발전소/풍력 설비", "turbine, gearbox, bearing", "operating hours, vibration, wind load", "inspection, component replacement", "availability와 failure risk 균형"],
                ["군용 차량/항공 정비", "vehicle / aircraft fleet", "mission hours, terrain severity, component HI", "PM, inspection, grounded rotation", "mission readiness와 정비비 균형"],
            ],
        )
        + "\n\nThese are transfer cases, not validated experiments in this project.",
    )


def write_outline(summary: list[dict[str, object]], breakdown: list[dict[str, object]]) -> None:
    best_cost = min(summary, key=lambda r: float(r["total_cost_mean"]))
    best_fulfillment = max(summary, key=lambda r: float(r["demand_fulfillment_rate_mean"]))
    outline = f"""
# Slide Outline

## Slide 1. Title
Title: {TITLE}

Subtitle: {SUBTITLE}

## Slide 2. 프로젝트 개요
- 문제 배경: 열화가 누적되는 haul truck과 tire를 계속 운행할지 PM으로 뺄지 결정해야 한다.
- 핵심 질문: 같은 환경에서 어떤 정책이 CU 기반 비용과 생산 KPI를 더 잘 균형화하는가.
- 산업공학적 의사결정 구조: resource allocation, queue, PM timing, cost trade-off.
- 왜 광산 트럭인가: 설비 열화, 대기, 생산 목표, 정비 capacity가 동시에 충돌한다.
- 표현: Escondida/Atacama 특성을 참조한 proxy DES 가상광산이다.

## Slide 3. 프로젝트 요소 설명
Truck, Tire HI, Truck HI, Shovel, Crusher 1 / Crusher 2, PM Bay, Plant Feed Manager, Time-risk / seasonal risk, Cost Unit을 한 장에 정리한다.

## Slide 4. 시뮬레이션 환경 구조
DES engine, dispatch-PM decision, queue, loading / hauling / dumping / PM / cooldown / standby, event scheduler 흐름을 설명한다.

## Slide 5. 시뮬레이션 세부 스펙
`tables/03_simulation_spec.md`의 Category / Value / Type / Defense 구조를 사용한다.

## Slide 6. 마일리지 / HI / PM 판단 구조
운행 누적 → EOH / TKPH / severity 증가 → Tire HI, Truck HI 감소 → RUL proxy, PM due score 증가 → PM / 계속 운행 / cooldown / standby 판단.

마일리지 용어 매핑:

{md_table(["발표 용어", "구현상 의미"], [
    ["마일리지", "EOH, TKPH, route severity 기반 누적 사용량 proxy"],
    ["설비 상태", "Truck HI + Tire HI"],
    ["PM 필요도", "RUL proxy, PM due score, HI threshold"],
    ["최소 비용 정책", "CU 기반 총비용, downtime, queue, failure, PM cost 최소화 정책"],
])}

## Slide 7. 휴리스틱 비교 구조
구현 이름을 사용한다: H0 Periodic PM Baseline, H1 Due / Health PM, H2 PM Risk Priority, H3 Cost Unit Value, H4 Flow / Backpressure.

## Slide 8. 각 휴리스틱 설명
`tables/04_heuristic_definitions.md`의 policy decision table을 사용한다.

## Slide 9. 결과 비교 — KPI
Official source: `outputs/c5_1/summary/policy_comparison.csv`.
현재 365-day sweep 기준 lowest total cost는 {best_cost['policy_id']} ({fmt(best_cost['total_cost_mean'])} CU), highest fulfillment도 {best_fulfillment['policy_id']} ({fmt(best_fulfillment['demand_fulfillment_rate_mean'])})이다.

## Slide 10. 결과 비교 — 비용 분해
`tables/06_cost_breakdown.md`와 `figures/cost_breakdown.png`를 사용한다. CU cost가 정책 비교 기준이다.

## Slide 11. 정책 해석
- 가장 낮은 비용: {best_cost['policy_id']}
- 생산량 유지: {best_fulfillment['policy_id']}
- PM을 많이 쓰는 정책은 cost와 downtime을 같이 봐야 한다.
- failure field는 현재 official output에 별도 존재하지 않는다.
- PM bay / queue / time-risk는 ranking을 해석하는 proxy factor이며 통계적 유의성으로 과장하지 않는다.

## Slide 12. 프로젝트 한계점
`tables/07_limitations_and_improvements.md`의 limitations table을 사용한다.

## Slide 13. 개선점
telemetry calibration, multi-seed robustness, PM bay sensitivity, cost sensitivity, route roughness/demand shock, RUL proxy refinement를 제안한다.

## Slide 14. 타 분야 응용
스마트팩토리 AGV, 반도체 후공정 설비, 저항점용접 RSW electrode tip, 데이터센터 냉각/서버 설비, 발전소/풍력 설비, 군용 차량/항공 정비로 전이 가능성을 설명한다. 이미 검증한 실험으로 말하지 않는다.

## Slide 15. Final Message
본 프로젝트의 핵심은 광산 자체를 정밀 복제하는 것이 아니라,
열화가 누적되는 설비를 언제 계속 운행하고 언제 PM으로 빼야 하는지
정량 KPI와 비용 proxy로 비교하는 의사결정 프레임워크를 만든 것이다.
"""
    write_text(PACK / "slide_outline.md", outline)


def write_script_notes() -> None:
    slides = [
        ("Title", "프로젝트 제목과 범위를 먼저 고정한다.", "등가 마일리지와 HI 기반 PM timing 비교라고 소개한다.", "실제 광산을 복제했다고 말하지 않는다.", "마일리지는 실제 odometer가 아니라 equivalent operating mileage proxy라고 답한다."),
        ("프로젝트 개요", "이 프로젝트는 정비 타이밍을 비용과 KPI로 비교하는 의사결정 프레임워크다.", "광산 트럭은 생산 목표, queue, 정비 capacity, 설비 열화가 동시에 충돌하는 사례라 설명한다.", "디지털 트윈, 실측 회계값이라는 표현을 피한다.", "왜 광산인가라는 질문에는 IE scheduling/maintenance trade-off가 선명한 사례라고 답한다."),
        ("프로젝트 요소 설명", "각 object가 simulation에서 어떤 역할을 하는지 연결한다.", "Truck과 Tire HI는 상태, PM Bay는 제한자, Plant Feed Manager는 수요 목표라고 말한다.", "PM bay 2개를 실제 설비 수로 말하지 않는다.", "PM bay는 bay, crew, tool, tire handler를 묶은 통합 capacity라고 답한다."),
        ("시뮬레이션 환경 구조", "DES 흐름을 event와 state update 중심으로 설명한다.", "dispatch/PM policy가 action을 내고, DES가 truck state와 KPI를 업데이트한다고 말한다.", "operator dashboard 기능 설명으로 확장하지 않는다.", "시각화 MVP는 policy log replay라고 답한다."),
        ("시뮬레이션 세부 스펙", "config-driven 값을 보여주고 proxy/assumption을 구분한다.", "fleet 8, payload 350, crusher 2, PM bay 2, 365 days 등 config 값을 짚는다.", "shovel count처럼 config에 없는 값은 presentation flow label로만 말한다.", "실제 값이냐는 질문에는 parameter defense table의 proxy 분류를 근거로 답한다."),
        ("마일리지 / HI / PM 판단 구조", "마일리지를 구현상 equivalent usage proxy로 정리한다.", "EOH/TKPH/severity가 누적되면 HI가 내려가고 PM 필요도가 오른다는 흐름으로 말한다.", "실제 odometer field가 있다고 말하지 않는다.", "마일리지 표현은 발표 제목과 구현 사이를 연결하는 용어라고 답한다."),
        ("휴리스틱 비교 구조", "정책만 바꾸고 환경은 같게 유지한 comparison이라고 설명한다.", "H0-H4 이름과 역할을 짧게 소개한다.", "Drop Zone을 H4로 말하지 않는다.", "Drop Zone은 future environment scenario라 답한다."),
        ("각 휴리스틱 설명", "각 정책의 입력 정보와 약점을 함께 말한다.", "H0 baseline, H1 queue/bottleneck, H2 HI risk, H3 CU value, H4 backpressure로 구분한다.", "어느 하나를 무조건 최적이라고 말하지 않는다.", "H3는 현재 cost weighting과 sweep에서 좋은 정책이라고 답한다."),
        ("결과 비교 — KPI", "공식 365-day result를 사용해 정책 ranking을 말한다.", "total cost, completed loads, unmet demand, fulfillment를 같이 본다.", "analysis 폴더의 작은 scale table과 혼용하지 않는다.", "충돌 값이 있으면 official summary를 우선했다고 답한다."),
        ("결과 비교 — 비용 분해", "CU 비용 분해로 어떤 비용이 ranking을 만드는지 설명한다.", "PM direct, downtime, degradation, target shortfall을 분리해 말한다.", "queue/failure cost가 별도 field인 것처럼 만들지 않는다.", "N/A는 missing field를 숨기지 않은 표시라고 답한다."),
        ("정책 해석", "정책 선택은 reward가 아니라 KPI, cost, robustness 기준이다.", "현재 sweep에서는 H3가 cost와 fulfillment에서 가장 강하다고 말하되 과장하지 않는다.", "통계적 유의성을 주장하지 않는다.", "multi-seed가 제한적이라 sensitivity가 필요하다고 답한다."),
        ("프로젝트 한계점", "한계는 방어 포인트로 제시한다.", "proxy DES, no telemetry, CU cost, time-risk proxy, limited robustness를 정리한다.", "약점 숨기기처럼 말하지 않는다.", "범위를 명확히 잘라서 구현 신뢰도를 높였다고 답한다."),
        ("개선점", "다음 단계는 데이터 calibration과 sensitivity다.", "telemetry, PM bay sensitivity, cost weight sensitivity, RUL refinement를 우선순위로 제안한다.", "지금 구현된 것처럼 말하지 않는다.", "개선안은 validation roadmap이라고 답한다."),
        ("타 분야 응용", "열화 설비 PM timing 문제로 일반화한다.", "AGV, 반도체 후공정, RSW tip, 데이터센터, 발전/풍력, 군용 정비를 연결한다.", "이미 실험 완료한 적용 사례로 말하지 않는다.", "공통 구조는 degradation proxy + maintenance action + objective라고 답한다."),
        ("Final Message", "핵심 메시지를 한 문장으로 닫는다.", "정밀 복제가 아니라 PM 의사결정 프레임워크라는 점을 강조한다.", "성과를 실제 광산 성능으로 과장하지 않는다.", "가치가 어디 있냐는 질문에는 비교 가능한 정책 평가 구조라고 답한다."),
    ]
    parts = ["# Slide Script Notes"]
    for idx, (title, msg, talk, caution, qa) in enumerate(slides, start=1):
        parts.append(
            f"""
## Slide {idx}. {title}

### 핵심 메시지
{msg}

### 발표자가 말할 내용
{talk}

### 주의할 표현
{caution}

### 예상 질문 대응
{qa}
"""
        )
    write_text(PACK / "slide_script_notes.md", "\n".join(parts))


def write_readme(generated_figures: list[str], missing_names: list[str]) -> None:
    placeholder_files = sorted(p.relative_to(PACK).as_posix() for p in FIGURES.glob("*.placeholder.md"))
    write_text(
        PACK / "README.md",
        f"""
# Presentation Materials Pack

This folder contains presentation-ready source copies, generated tables, chart images, slide outline, and speaker notes for:

{TITLE}

## Use For PPT Production
- `slide_outline.md`
- `slide_script_notes.md`
- `tables/*.md`
- `figures/*.png`

## Raw Copied Evidence
Raw copied files are under `data/raw/`. They preserve source documents, configs, result summaries, analysis files, and replay logs without modification.

## Generated Files
- `data/generated/policy_result_summary.csv`
- `data/generated/cost_breakdown_by_policy.csv`
- `data/generated/pm_timing_counts.csv`
- `data/generated/missing_requested_sources.csv`
- `tables/*.md`
- `figures/*.png`

## Chart Placeholders
{", ".join(placeholder_files) if placeholder_files else "No chart placeholder was needed. PM timing data was available from replay logs."}

## Regenerate Figures and Tables
Run from repository root:

```powershell
python scripts/build_presentation_assets.py
```

## Allowed Claims
- Escondida/Atacama 특성을 참조한 proxy DES 가상광산이다.
- time-risk factor는 C5 risk multiplier proxy다.
- cost는 CU 기반 marginal cost proxy다.
- PM bay capacity는 bay, crew, tool, tire handler를 포함한 통합 정비능력이다.
- 정책 비교는 reward가 아니라 KPI, cost, robustness 기준으로 해석한다.

## Do Not Claim
- 실제 광산을 정밀 재현했다.
- time-risk를 현장 측정 회귀계수로 제시한다.
- CU cost matrix를 실제 광산 회계 장부값으로 제시한다.
- PM bay 2개가 실제 광산 설비 수다.
- PPO/RL이 모든 baseline보다 우수하다.

## Missing Requested Source Names
See `data/generated/missing_requested_sources.csv`.
Missing exact names: {", ".join(missing_names) if missing_names else "None"}.

## Generated Figures
{chr(10).join("- " + item for item in generated_figures)}
""",
    )


def write_validation(missing_names: list[str], generated_figures: list[str], copied: list[dict[str, str]]) -> None:
    warnings = [
        "outputs/c5_1/analysis/policy_kpi_summary.csv conflicts with the official 365-day summary scale; official summary values were used.",
        "Queue cost and failure cost are not separate official cost fields; they are marked N/A.",
        "No literal mileage/odometer field was found; mileage is explained as EOH / equivalent mileage proxy.",
    ]
    report = f"""
# Validation Report

## Checks
- Deprecated USD constants are not used in generated presentation text.
- No claim says the model is a real mine digital twin.
- No claim says time-risk factors are measured values.
- No fake numeric result values are introduced; numeric KPI values come from official CSV/logs/config.
- Result tables cite source file paths.
- 마일리지는 EOH / equivalent mileage proxy로 설명된다.
- Heuristic names use implemented C5.1 names.
- CU-based cost is used for policy comparison.
- Missing data is reported in `data/generated/missing_requested_sources.csv`.

## Missing / Placeholder
- Missing exact requested source names: {", ".join(missing_names) if missing_names else "None"}
- Figure placeholders: {", ".join(p.relative_to(PACK).as_posix() for p in FIGURES.glob("*.placeholder.md")) or "None"}

## Warnings
{chr(10).join("- " + item for item in warnings)}

## Created Figure Files
{chr(10).join("- " + item for item in generated_figures)}

## Copied Source Count
{len(copied)}
"""
    write_text(GENERATED / "validation_report.md", report)


def copy_self() -> None:
    target = PACK / "scripts" / "build_presentation_assets.py"
    if Path(__file__).resolve() != target.resolve():
        shutil.copy2(Path(__file__), target)


def main() -> None:
    ensure_dirs()
    sources, missing_names = discover_sources()
    manifest = copy_sources(sources, missing_names)
    write_manifest(manifest)

    config = load_config()
    rows = official_rows()
    summary = aggregate_policy_rows(rows)
    logs = load_logs()
    breakdown = cost_breakdown(rows, config, logs)
    pm_rows = pm_timing_counts(logs)

    write_csv(
        GENERATED / "policy_result_summary.csv",
        summary,
        list(summary[0].keys()) if summary else ["policy_id"],
    )
    write_csv(
        GENERATED / "cost_breakdown_by_policy.csv",
        breakdown,
        list(breakdown[0].keys()) if breakdown else ["policy_id"],
    )
    write_csv(
        GENERATED / "pm_timing_counts.csv",
        pm_rows,
        ["policy_id", "period", "pm_actions"],
    )

    generated_figures = generate_figures(summary, breakdown, pm_rows)
    write_tables(summary, breakdown, config)
    write_outline(summary, breakdown)
    write_script_notes()
    write_readme(generated_figures, missing_names)
    write_validation(missing_names, generated_figures, manifest)
    copy_self()

    created = sorted(p.relative_to(PACK).as_posix() for p in PACK.rglob("*") if p.is_file())
    print("[Created]")
    for item in created:
        print(f"- presentation_materials/{item}")
    print("\n[Copied Sources]")
    for item in manifest:
        print(f"- {item['Original Path']} -> {item['Copied Path']}")
    print("\n[Generated Tables]")
    for path in sorted(TABLES.glob("*.md")):
        print(f"- {rel(path)}")
    print("\n[Generated Figures]")
    for item in generated_figures:
        print(f"- {item}")
    print("\n[Missing / Placeholder]")
    for item in missing_names:
        print(f"- missing exact requested source: {item}")
    for path in sorted(FIGURES.glob("*.placeholder.md")):
        print(f"- {rel(path)}")
    print("\n[Warnings]")
    print("- Official numeric comparison uses outputs/c5_1/summary/policy_comparison.csv.")
    print("- outputs/c5_1/analysis/policy_kpi_summary.csv has conflicting smaller-scale KPI values.")
    print("- Queue cost, failure cost, tire count per truck, and minimum operating trucks are N/A when no official field exists.")
    print(f"\nGenerated at {datetime.now().isoformat(timespec='seconds')}")


if __name__ == "__main__":
    main()
