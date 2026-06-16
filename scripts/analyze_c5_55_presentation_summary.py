"""Create presentation-focused C5.55 H5 summary tables and report."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRADEOFF_PATH = PROJECT_ROOT / "outputs" / "c5_55" / "analysis" / "c5_55_policy_tradeoff_summary.csv"
GUARD_PATH = PROJECT_ROOT / "outputs" / "c5_55" / "analysis" / "c5_55_guard_behavior_summary.csv"
BENCHMARK_REPORT = PROJECT_ROOT / "reports" / "c5_55_h5_policy_benchmark.md"
ANALYSIS_DIR = PROJECT_ROOT / "outputs" / "c5_55" / "analysis"
REPORT_PATH = PROJECT_ROOT / "reports" / "c5_55_personal_presentation_summary.md"

RANKING_PATH = ANALYSIS_DIR / "c5_55_presentation_ranking_table.csv"
COMPARISON_PATH = ANALYSIS_DIR / "c5_55_h4_h5_h5aggressive_comparison.csv"
CAVEAT_PATH = ANALYSIS_DIR / "c5_55_presentation_caveat_table.csv"

PRESENTATION_POLICIES = ["H5", "H5_AGGRESSIVE", "BALANCED_RR_H4_PM", "H4"]
REGIMES = ["heterogeneous_condition", "high_stress", "high_demand_high_stress"]
COMPARATORS = ["H4", "BALANCED_RR_H4_PM", "H5_AGGRESSIVE"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def f(row: dict[str, Any], key: str) -> float:
    return float(row.get(key, 0) or 0)


def get(rows: list[dict[str, str]], regime: str, policy: str) -> dict[str, str]:
    return next(row for row in rows if row["regime"] == regime and row["policy"] == policy)


def interpretation_for_ranking(row: dict[str, str]) -> str:
    policy = row["policy"]
    rank = int(float(row["rank_tco_v4_soft"]))
    if policy == "H5":
        return "Default official H5; best overall unless aggressive stress setting is isolated."
    if policy == "H5_AGGRESSIVE":
        return "Aggressive sensitivity comparator; useful under high-demand stress but higher fallback dependence."
    if policy == "BALANCED_RR_H4_PM":
        return "Audit-only comparator; not an official policy."
    if policy == "H4":
        return "Official H4 baseline; improved by H5 in C5.55."
    return f"Rank {rank} in soft TCO v4."


def build_ranking_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for regime in REGIMES:
        subset = [get(rows, regime, policy) for policy in PRESENTATION_POLICIES]
        for row in sorted(subset, key=lambda item: f(item, "total_tco_v4_soft_congestion")):
            out.append(
                {
                    "regime": regime,
                    "policy": row["policy"],
                    "soft_tco_v4": f(row, "total_tco_v4_soft_congestion"),
                    "rank": int(float(row["rank_tco_v4_soft"])),
                    "effective_fulfillment_rate": f(row, "effective_fulfillment_rate"),
                    "failure_count": f(row, "failure_count"),
                    "cm_count": f(row, "cm_count"),
                    "downtime_hours": f(row, "downtime_hours"),
                    "hard_congestion_hours": f(row, "congestion_delay_hours_hard"),
                    "soft_congestion_hours": f(row, "congestion_delay_hours_soft"),
                    "fallback_per_completed_load": f(row, "fallback_per_completed_load"),
                    "dominant_guard": row["dominant_guard"],
                    "interpretation": interpretation_for_ranking(row),
                }
            )
    return out


def comparison_interpretation(comparison: str, tco_margin: float, fallback_diff: float) -> str:
    if comparison == "H5 vs H4":
        return "H5 is lower TCO than H4; fallback behavior should still be disclosed."
    if comparison == "H5 vs BALANCED_RR_H4_PM":
        return "H5 converts the audit comparator signal into an official guarded policy."
    if tco_margin >= 0:
        return "H5 is lower TCO than the aggressive variant in this regime."
    return (
        "H5_AGGRESSIVE is lower TCO here, but it is not default because fallback dependence is higher."
        if fallback_diff < 0
        else "H5_AGGRESSIVE is lower TCO here."
    )


def build_comparison_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for regime in REGIMES:
        h5 = get(rows, regime, "H5")
        for comparator in COMPARATORS:
            comp = get(rows, regime, comparator)
            comparison = f"H5 vs {comparator}"
            tco_margin = f(comp, "total_tco_v4_soft_congestion") - f(h5, "total_tco_v4_soft_congestion")
            fallback_diff = f(h5, "fallback_per_completed_load") - f(comp, "fallback_per_completed_load")
            out.append(
                {
                    "regime": regime,
                    "comparison": comparison,
                    "tco_margin": tco_margin,
                    "effective_fulfillment_diff": f(h5, "effective_fulfillment_rate")
                    - f(comp, "effective_fulfillment_rate"),
                    "failure_diff": f(h5, "failure_count") - f(comp, "failure_count"),
                    "cm_diff": f(h5, "cm_count") - f(comp, "cm_count"),
                    "downtime_diff": f(h5, "downtime_hours") - f(comp, "downtime_hours"),
                    "soft_congestion_diff": f(h5, "congestion_delay_hours_soft")
                    - f(comp, "congestion_delay_hours_soft"),
                    "fallback_diff": fallback_diff,
                    "interpretation": comparison_interpretation(comparison, tco_margin, fallback_diff),
                }
            )
    return out


def caveat_rows() -> list[dict[str, str]]:
    return [
        {
            "issue": "C5.55 does not replace team C5.4.",
            "risk_if_overclaimed": "Audience may think the team result changed retroactively.",
            "safe_interpretation": "C5.55 is a personal follow-up benchmark with an expanded objective.",
            "presentation_sentence": "C5.55는 C5.4를 대체하지 않고, 목적함수 확장 시 정책 순위가 어떻게 달라지는지 보여주는 후속 실험입니다.",
        },
        {
            "issue": "C5.55 uses proxy cycle-time and soft congestion model.",
            "risk_if_overclaimed": "Could be mistaken for site-calibrated mine optimization.",
            "safe_interpretation": "The model is useful for structured comparison, not real dispatch calibration.",
            "presentation_sentence": "cycle time과 congestion은 proxy model이므로 실제 광산 실측 최적 정책이라고 주장하지 않습니다.",
        },
        {
            "issue": "H5_AGGRESSIVE wins in high_demand_high_stress.",
            "risk_if_overclaimed": "Could make the default H5 selection look inconsistent.",
            "safe_interpretation": "It is a stress-sensitive alternative with higher fallback dependence.",
            "presentation_sentence": "고수요 고스트레스에서는 aggressive variant가 더 낮은 TCO를 보였지만 fallback 의존도가 높아 default로 두지 않았습니다.",
        },
        {
            "issue": "H1/H2 can still be reliability-focused frontier.",
            "risk_if_overclaimed": "Could imply H1/H2 are simply bad policies.",
            "safe_interpretation": "They remain reliability-oriented policies under a narrower objective.",
            "presentation_sentence": "H1/H2는 reliability-cost 관점에서는 여전히 의미 있는 frontier이며, C5.55는 production-congestion objective를 추가한 비교입니다.",
        },
        {
            "issue": "H5 includes fallback-to-H4 behavior and guard logic.",
            "risk_if_overclaimed": "Could hide that H5 partly depends on H4 fallback.",
            "safe_interpretation": "Fallback is an explicit safety mechanism and must be disclosed.",
            "presentation_sentence": "H5는 balanced rotation만 쓰는 정책이 아니라 guard 위반 시 H4 score로 fallback하는 guarded policy입니다.",
        },
        {
            "issue": "Route guard is currently non-binding.",
            "risk_if_overclaimed": "Could overstate the role of route-capacity guard.",
            "safe_interpretation": "Most decisions are driven by shovel, crusher, risk guards and fallback.",
            "presentation_sentence": "현재 regime에서는 route guard violation이 0이라, 실제로는 shovel/risk/crusher guard가 의사결정을 주도했습니다.",
        },
    ]


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def md_table(rows: list[dict[str, Any]], fields: list[str], float_fields: set[str]) -> list[str]:
    lines = [
        "| " + " | ".join(fields) + " |",
        "|" + "|".join("---" for _ in fields) + "|",
    ]
    for row in rows:
        values = []
        for field in fields:
            value = row[field]
            if field in float_fields:
                value = f"{float(value):.3f}" if abs(float(value)) < 10 else f"{float(value):.1f}"
            values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def write_report(
    ranking: list[dict[str, Any]],
    comparisons: list[dict[str, Any]],
    caveats: list[dict[str, str]],
) -> None:
    h5_rows = [row for row in ranking if row["policy"] == "H5"]
    h5_min_eff = min(float(row["effective_fulfillment_rate"]) for row in h5_rows)
    h5_beats_h4 = all(row["tco_margin"] > 0 for row in comparisons if row["comparison"] == "H5 vs H4")
    h5_beats_rr = all(
        row["tco_margin"] > 0 for row in comparisons if row["comparison"] == "H5 vs BALANCED_RR_H4_PM"
    )
    aggressive_wins = [
        row["regime"]
        for row in comparisons
        if row["comparison"] == "H5 vs H5_AGGRESSIVE" and row["tco_margin"] < 0
    ]

    lines = [
        "# C5.55 Personal Presentation Summary",
        "",
        "## Executive Summary",
        "",
        f"C5.55 is a personal follow-up benchmark that freezes H5 as the guarded H4 route-allocation improvement from C5.54. In the 90-day benchmark, H5 beats both H4 and the audit-only `BALANCED_RR_H4_PM` comparator in all three regimes under soft TCO v4, with minimum effective fulfillment {h5_min_eff:.3f}. `H5_AGGRESSIVE` is better only under high-demand/high-stress, but its higher fallback dependence makes it an alternative rather than the default.",
        "",
        "## C5.4 vs C5.55 Difference",
        "",
        "C5.4에서는 reliability-cost 중심 목적함수에서 H1/H2가 우수했습니다. 반면 C5.55는 개인 후속 실험으로 grade-adjusted output과 route/facility congestion을 포함했기 때문에, 생산가치와 병목까지 균형화하는 H5가 우수하게 나타났습니다. 두 결과는 모순이 아니라 objective definition이 달라졌을 때 최적 정책이 달라진다는 후속 검증입니다.",
        "",
        "## H5 Policy Definition",
        "",
        "H5는 H4의 PM/flow logic을 기반으로 balanced route rotation, shovel/crusher/risk guard, fallback-to-H4 logic을 결합한 guarded route-allocation policy입니다.",
        "",
        "## Why H5 Was Selected as Default",
        "",
        "- H5 beats H4 in all regimes under soft TCO v4.",
        "- H5 beats the audit-only `BALANCED_RR_H4_PM` comparator in all regimes.",
        "- H5 keeps fallback/load lower than `H5_AGGRESSIVE` while retaining strong TCO performance.",
        "- H5 is easier to explain as a guarded official policy because it uses the C5.54 freeze setting `0.90/base`.",
        "",
        "## Why H5_AGGRESSIVE Was Not Selected as Default",
        "",
        "`H5_AGGRESSIVE` wins only in `high_demand_high_stress`; in lower-stress regimes it is slightly worse than H5 and roughly doubles fallback/load. It remains useful as a stress-sensitive alternative, but not as the presentation default.",
        "",
        "## H4 vs H5 vs H5_AGGRESSIVE Comparison",
        "",
    ]
    ranking_fields = [
        "regime",
        "policy",
        "soft_tco_v4",
        "rank",
        "effective_fulfillment_rate",
        "failure_count",
        "cm_count",
        "downtime_hours",
        "hard_congestion_hours",
        "soft_congestion_hours",
        "fallback_per_completed_load",
        "dominant_guard",
        "interpretation",
    ]
    lines += md_table(
        ranking,
        ranking_fields,
        {
            "soft_tco_v4",
            "effective_fulfillment_rate",
            "failure_count",
            "cm_count",
            "downtime_hours",
            "hard_congestion_hours",
            "soft_congestion_hours",
            "fallback_per_completed_load",
        },
    )
    lines += [
        "",
        "## H5 Pairwise Improvement",
        "",
    ]
    comparison_fields = [
        "regime",
        "comparison",
        "tco_margin",
        "effective_fulfillment_diff",
        "failure_diff",
        "cm_diff",
        "downtime_diff",
        "soft_congestion_diff",
        "fallback_diff",
        "interpretation",
    ]
    lines += md_table(
        comparisons,
        comparison_fields,
        {
            "tco_margin",
            "effective_fulfillment_diff",
            "failure_diff",
            "cm_diff",
            "downtime_diff",
            "soft_congestion_diff",
            "fallback_diff",
        },
    )
    lines += [
        "",
        "## H5 vs BALANCED_RR_H4_PM Comparison",
        "",
        f"H5 beats the audit-only comparator in all regimes: {'yes' if h5_beats_rr else 'no'}. The key interpretation is that C5.55 converts the synthetic balanced-route signal into an official guarded policy with explicit utilization/risk guards and fallback behavior.",
        "",
        "## H5 vs H1/H2 Reliability Caveat",
        "",
        "H1/H2 should not be dismissed as failed policies. They can still represent a reliability-focused frontier under a narrower reliability-cost objective. C5.55 changes the objective surface by adding grade-adjusted output and congestion, so the preferred policy changes.",
        "",
        "## Guard/Fallback Caveat",
        "",
        "H5는 C5.55의 proxy objective에서는 가장 균형적인 정책이지만, 실제 광산 실측 최적 정책을 의미하지는 않습니다. 또한 C5.55는 팀 발표 C5.4를 대체하는 것이 아니라, 개인 발표에서 objective 확장과 정책 개선 과정을 보여주기 위한 follow-up benchmark입니다.",
        "",
        "## Caveat / Defense Table",
        "",
    ]
    caveat_fields = ["issue", "risk_if_overclaimed", "safe_interpretation", "presentation_sentence"]
    lines += md_table(caveats, caveat_fields, set())
    lines += [
        "",
        "## Recommended Slide Structure",
        "",
        "1. Slide A — Why C5.4 and C5.55 differ",
        "2. Slide B — From H4 to H5: route allocation improvement",
        "3. Slide C — H5 benchmark result table",
        "4. Slide D — Guard/fallback caveat and limitations",
        "5. Slide E — Portfolio meaning: objective-sensitive operations optimization",
        "",
        "## Presentation-Ready Korean Explanation Paragraphs",
        "",
        "첫째, C5.4와 C5.55의 결과 차이는 정책 성능이 갑자기 뒤집힌 것이 아니라 목적함수 정의가 달라졌기 때문에 발생한 결과입니다. C5.4는 reliability-cost 관점에서 H1/H2의 장점을 보여주었고, C5.55는 grade-adjusted output과 congestion까지 포함했을 때 H5가 더 균형적인 선택이 될 수 있음을 보여줍니다.",
        "",
        "둘째, H5는 H4를 버린 새로운 정책이 아니라 H4의 flow/backpressure PM logic 위에 route allocation guard를 얹은 정책입니다. balanced route rotation으로 route 집중을 낮추고, shovel/crusher/risk guard로 병목과 위험을 제어하며, 모든 guard가 막힐 때는 H4 scoring으로 fallback합니다.",
        "",
        "셋째, H5_AGGRESSIVE는 high-demand/high-stress 조건에서 가장 낮은 TCO를 보였지만 fallback 의존도가 높기 때문에 default로 선택하지 않았습니다. 발표에서는 H5를 기본 정책으로, H5_AGGRESSIVE를 stress-sensitive alternative로 설명하는 것이 가장 방어 가능한 해석입니다.",
        "",
        "## Q&A Defense Bullets",
        "",
        f"- H5 beats H4 across all regimes: {'yes' if h5_beats_h4 else 'no'}.",
        f"- H5 beats the audit comparator across all regimes: {'yes' if h5_beats_rr else 'no'}.",
        f"- H5_AGGRESSIVE beats H5 only in: {', '.join(aggressive_wins) if aggressive_wins else 'no regimes'}.",
        "- C5.55 does not replace C5.4; it demonstrates objective-sensitive optimization.",
        "- The model is proxy-based and should not be presented as site-calibrated dispatch optimization.",
        "- Fallback-to-H4 is a designed safety mechanism and should be disclosed.",
        "- Route guard is non-binding in current regimes; shovel/risk/crusher guards explain most guard behavior.",
        "",
    ]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    tradeoff = read_csv(TRADEOFF_PATH)
    read_csv(GUARD_PATH)
    if not BENCHMARK_REPORT.exists():
        raise FileNotFoundError(BENCHMARK_REPORT)

    ranking = build_ranking_rows(tradeoff)
    comparisons = build_comparison_rows(tradeoff)
    caveats = caveat_rows()
    write_csv(RANKING_PATH, ranking, list(ranking[0]))
    write_csv(COMPARISON_PATH, comparisons, list(comparisons[0]))
    write_csv(CAVEAT_PATH, caveats, list(caveats[0]))
    write_report(ranking, comparisons, caveats)
    print(f"Wrote {RANKING_PATH}")
    print(f"Wrote {COMPARISON_PATH}")
    print(f"Wrote {CAVEAT_PATH}")
    print(f"Wrote {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
