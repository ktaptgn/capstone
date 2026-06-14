"""Build `version_results.json` consumed by the operator dashboard and PM worker app to
switch the displayed policy-comparison results between capstone versions C5.1 / C5.2 / C5.3 / C5.4.

- C5.4 (current official version) is read from the joint PM+dispatch sweep summary
  (`outputs/c5_4/summary/c5_4_policy_comparison.csv`, the `heterogeneous_condition` regime).
- C5.3 is read from the real sweep summary (`outputs/c5_3/summary/c5_3_policy_comparison.csv`,
  the `heterogeneous_condition` regime) so the UI always reflects the latest run.
- C5.2 is the frozen official KPI table from `docs/source/05_C5_2_SPECIFICATION.md` (levers on).
- C5.1 is the documented legacy-heuristic total cost from the project memory/changelog
  (reliability off; H1 and H4 collided bit-for-bit). Only totals are documented, so the other
  metrics are left null and the UI renders them as "—" rather than inventing numbers.

The same JSON is written into both app data folders so neither app needs a backend.
"""
from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "outputs" / "c5_3" / "summary" / "c5_3_policy_comparison.csv"
C5_4_CSV_PATH = ROOT / "outputs" / "c5_4" / "summary" / "c5_4_policy_comparison.csv"
TARGETS = [
    ROOT / "ui" / "operator_dashboard" / "src" / "data" / "version_results.json",
    ROOT / "ui" / "pm_worker_app" / "src" / "data" / "version_results.json",
]

COLORS = {
    "H0": "#64748B", "H_TIME": "#7C3AED", "H1": "#16A34A",
    "H2": "#0D9488", "H3": "#F59E0B", "H4": "#3B82F6",
}


def policy(pid, name, *, fulfill=None, pm=None, downtime=None, failures=None, total=None, use_case=""):
    return {
        "id": pid, "name": name, "color": COLORS.get(pid, "#64748B"),
        "demandFulfill": fulfill, "pmCost": pm, "downtime": downtime,
        "failures": failures, "totalCost": total, "useCase": use_case,
    }


def build_c5_1() -> dict:
    # Legacy heuristic totals (reliability off); H1 == H4 (bit-identical collision).
    return {
        "label": "C5.1",
        "title": "C5.1 — 휴리스틱 비교 기반",
        "subtitle": "레거시 H0–H4, 단일 환경. H1과 H4가 동일(충돌)했던 버전.",
        "costLabel": "총 운영비용", "costUnit": "normalized CU", "recommended": "H3",
        "headline": "H3가 최저 비용. 단 레거시 H1과 H4가 bit-identical로 충돌(사실상 4정책 비교) — C5.2에서 해소.",
        "source": "project memory / changelog (reliability off)",
        "policies": [
            policy("H0", "Baseline", total=1858.65, use_case="기준 비교"),
            policy("H1", "Bottleneck Dispatch", total=7062.53, use_case="처리량 우선 (H4와 충돌)"),
            policy("H2", "PM Risk Priority", total=3339.37, use_case="고장 위험 회피"),
            policy("H3", "Cost Unit Value", total=1724.75, use_case="비용 균형 (추천)"),
            policy("H4", "Flow / Backpressure", total=7062.53, use_case="흐름 압력 (H1과 충돌)"),
        ],
    }


def build_c5_2() -> dict:
    # Frozen official C5.2 table (levers on); see 05_C5_2_SPECIFICATION.md sections 4.1/4.2.
    return {
        "label": "C5.2",
        "title": "C5.2 — 보정 휴리스틱 + 신뢰성 레버",
        "subtitle": "H0 calendar / H_TIME / H1 due+health / H2·H3·H4. 건강도에 비용 결과 부여.",
        "costLabel": "총 운영비용", "costUnit": "normalized CU", "recommended": "H3",
        "headline": "상태인지 PM(H1/H2/H3, 고장 0)이 blind periodic PM(H0/H_TIME, 고장 발생)을 이김. H3 추천.",
        "source": "05_C5_2_SPECIFICATION.md (365d x 3 seeds, levers on)",
        "policies": [
            policy("H3", "Cost-value", fulfill=97.6, pm=613.3, downtime=724.3, failures=0, total=1675.67, use_case="비용 균형 (추천)"),
            policy("H1", "Due + health", fulfill=94.7, pm=520.8, downtime=625.0, failures=0, total=1858.65, use_case="상태 기반 PM"),
            policy("H_TIME", "Operating-hours", fulfill=98.5, pm=244.0, downtime=766.7, failures=110, total=1948.67, use_case="가동시간 기반 (blind)"),
            policy("H2", "Risk priority", fulfill=81.7, pm=402.7, downtime=483.0, failures=0, total=3312.74, use_case="위험 우선 PM"),
            policy("H0", "Calendar periodic", fulfill=83.2, pm=1095.0, downtime=1826.7, failures=92, total=5748.85, use_case="달력 주기 PM (blind)"),
            policy("H4", "Flow / backpressure", fulfill=49.8, pm=220.8, downtime=265.0, failures=0, total=7107.03, use_case="흐름 압력 (저충족)"),
        ],
    }


def build_c5_3() -> dict:
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    hetero = [r for r in rows if r["regime"] == "heterogeneous_condition"]
    names = {
        "H0": "Route-blind", "H1": "Health routing", "H2": "Risk-aware routing",
        "H3": "Value routing", "H4": "Capacity routing",
    }
    use_case = {
        "H0": "경로 무시 baseline", "H1": "약한 컴포넌트 보호 (추천)", "H2": "마모 트럭 완만경로",
        "H3": "등급 추종 (blind)", "H4": "용량 분산 (blind)",
    }

    def mean(pid, key):
        vals = [float(r[key]) for r in hetero if r["policy_id"] == pid]
        return statistics.mean(vals) if vals else 0.0

    pids = ["H0", "H1", "H2", "H3", "H4"]
    policies = [
        policy(
            pid, names[pid],
            fulfill=round(mean(pid, "demand_fulfillment_rate") * 100, 1),
            pm=round(mean(pid, "pm_cost"), 1),
            downtime=round(mean(pid, "downtime_cost"), 1),
            failures=round(mean(pid, "cm_count"), 1),
            total=round(mean(pid, "total_tco"), 1),
            use_case=use_case[pid],
        )
        for pid in pids
    ]
    policies.sort(key=lambda p: p["totalCost"])
    return {
        "label": "C5.3",
        "title": "C5.3 — 3-컴포넌트 신뢰성 + dispatch-only",
        "subtitle": "25대 + 경로 A/B/C, frailty + 센서노이즈. PM 고정(rule), 경로선택만 비교.",
        "costLabel": "총 TCO", "costUnit": "normalized CU", "recommended": policies[0]["id"],
        "headline": "상태인지 라우팅(H1/H2)이 blind(H0/H3/H4)를 TCO로 이김. 고스트레스에선 고장 ~6× 적게 발생.",
        "source": "outputs/c5_3/summary (30 seeds x 365d, heterogeneous_condition)",
        "policies": policies,
    }


def build_c5_4() -> dict:
    # Joint PM-scheduling + dispatch; read live from the heterogeneous_condition sweep (mean/seed).
    rows = list(csv.DictReader(C5_4_CSV_PATH.open(encoding="utf-8")))
    hetero = [r for r in rows if r["regime"] == "heterogeneous_condition"]
    names = {
        "H0": "Calendar + blind", "H_TIME": "Operating-hours + blind",
        "H1": "CBM + health", "H2": "Risk priority + risk-aware",
        "H3": "Cost-value", "H4": "Flow / backpressure",
    }
    use_case = {
        "H0": "달력 주기 PM (blind)", "H_TIME": "가동시간 PM (blind)",
        "H1": "상태기반 PM+경로 (추천)", "H2": "위험 우선 PM+완만경로",
        "H3": "비용가치 PM", "H4": "흐름 압력 PM",
    }

    def mean(pid, key):
        vals = [float(r[key]) for r in hetero if r["policy_id"] == pid]
        return statistics.mean(vals) if vals else 0.0

    pids = ["H0", "H_TIME", "H1", "H2", "H3", "H4"]
    policies = [
        policy(
            pid, names[pid],
            fulfill=round(mean(pid, "demand_fulfillment_rate") * 100, 1),
            pm=round(mean(pid, "pm_cost"), 1),
            downtime=round(mean(pid, "downtime_cost"), 1),
            failures=round(mean(pid, "cm_count"), 1),
            total=round(mean(pid, "total_tco"), 1),
            use_case=use_case[pid],
        )
        for pid in pids
    ]
    policies.sort(key=lambda p: p["totalCost"])
    return {
        "label": "C5.4",
        "title": "C5.4 — joint PM 스케줄링 + dispatch",
        "subtitle": "PM 시점이 정책 결정. 6개 PM×dispatch 가족. C5.3 신뢰성/비용 표면 그대로.",
        "costLabel": "총 TCO", "costUnit": "normalized CU", "recommended": policies[0]["id"],
        "headline": "상태인지 joint PM+dispatch(H1/H2)가 blind periodic(H0/H_TIME)을 +40% TCO로 이김(30/30 seed). blind는 과정비+bay포화 고장꼬리로 2중 손해.",
        "source": "outputs/c5_4/summary (30 seeds x 365d, heterogeneous_condition)",
        "policies": policies,
    }


def main() -> int:
    payload = {
        "versions": ["C5.1", "C5.2", "C5.3", "C5.4"],
        "default": "C5.4",
        "data": {
            "C5.1": build_c5_1(), "C5.2": build_c5_2(),
            "C5.3": build_c5_3(), "C5.4": build_c5_4(),
        },
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    for target in TARGETS:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
