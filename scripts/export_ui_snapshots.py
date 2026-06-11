from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_DIR = ROOT / "outputs" / "c5_1" / "summary"
LOG_DIR = ROOT / "outputs" / "c5_1" / "logs"
WORK_ORDER_DIR = ROOT / "outputs" / "c5_1" / "work_orders"
ANALYSIS_DIR = ROOT / "outputs" / "c5_1" / "analysis"
OPERATOR_SNAPSHOT_DIR = ROOT / "ui" / "operator_dashboard" / "public" / "c5_1"
OPERATOR_BUNDLED_DATA_DIR = ROOT / "ui" / "operator_dashboard" / "src" / "data"
PM_SNAPSHOT_DIR = ROOT / "ui" / "pm_worker_app" / "public" / "c5_1"


def _copy_if_exists(source: Path, target: Path) -> bool:
    if not source.exists():
        print(f"warning: missing source: {source}")
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    print(f"copied: {source} -> {target}")
    return True


def _sample_log() -> Path | None:
    preferred = LOG_DIR / "H3_seed_1.json"
    if preferred.exists():
        return preferred
    matches = sorted(LOG_DIR.glob("*.json"))
    return matches[0] if matches else None


def _work_orders() -> Path | None:
    preferred = WORK_ORDER_DIR / "work_orders_H3_seed1.json"
    if preferred.exists():
        return preferred
    matches = sorted(WORK_ORDER_DIR.glob("work_orders_*.json"))
    return matches[0] if matches else None


def _ensure_feedback_snapshot() -> None:
    source = WORK_ORDER_DIR / "pm_feedback_log.json"
    if not source.exists():
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("[]\n", encoding="utf-8")
        print(f"warning: created empty feedback log: {source}")
    _copy_if_exists(source, PM_SNAPSHOT_DIR / "pm_feedback_log.json")


def export_ui_snapshots() -> None:
    OPERATOR_SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    PM_SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    _copy_if_exists(
        SUMMARY_DIR / "policy_comparison.json",
        OPERATOR_SNAPSHOT_DIR / "policy_comparison.json",
    )

    analysis_json = ANALYSIS_DIR / "dashboard_analysis.json"
    if analysis_json.exists():
        _copy_if_exists(analysis_json, OPERATOR_SNAPSHOT_DIR / "dashboard_analysis.json")
        _copy_if_exists(
            analysis_json,
            OPERATOR_BUNDLED_DATA_DIR / "dashboardAnalysisSnapshot.json",
        )
    else:
        print(f"warning: dashboard analysis JSON missing, skipping operator snapshot: {analysis_json}")

    sample_log = _sample_log()
    if sample_log:
        _copy_if_exists(sample_log, OPERATOR_SNAPSHOT_DIR / "sample_log.json")
        _copy_if_exists(sample_log, PM_SNAPSHOT_DIR / "sample_log.json")
    else:
        print(f"warning: no log JSON files found in {LOG_DIR}")

    work_orders = _work_orders()
    if work_orders:
        _copy_if_exists(work_orders, OPERATOR_SNAPSHOT_DIR / "work_orders.json")
        _copy_if_exists(work_orders, PM_SNAPSHOT_DIR / "work_orders.json")
    else:
        print(f"warning: no work order JSON files found in {WORK_ORDER_DIR}")
        empty_work_orders = []
        for target_dir in (OPERATOR_SNAPSHOT_DIR, PM_SNAPSHOT_DIR):
            target = target_dir / "work_orders.json"
            target.write_text(json.dumps(empty_work_orders, indent=2), encoding="utf-8")
            print(f"warning: wrote empty work order snapshot: {target}")

    _ensure_feedback_snapshot()


if __name__ == "__main__":
    export_ui_snapshots()
