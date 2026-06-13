import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts.export_ui_snapshots import export_ui_snapshots
from scripts.export_work_orders import export_work_orders


ROOT = Path(__file__).resolve().parents[1]


def _read_optional(path: Path) -> bytes | None:
    return path.read_bytes() if path.exists() else None


def _restore_optional(path: Path, content: bytes | None) -> None:
    if content is None:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def test_work_order_export_and_schema_validation():
    work_order_path = export_work_orders(ROOT / "configs" / "c5_1.yaml", "H3", 1)
    schema = json.loads((ROOT / "schemas" / "work_order.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    work_orders = json.loads(work_order_path.read_text(encoding="utf-8"))

    assert work_order_path.name == "work_orders_H3_seed1.json"
    assert isinstance(work_orders, list)
    assert work_orders
    validator.validate(work_orders[0])
    assert (ROOT / "outputs" / "c5_1" / "work_orders" / "pm_feedback_log.json").exists()


def test_ui_snapshot_export_creates_app_public_snapshots():
    analysis_source = ROOT / "outputs" / "c5_1" / "analysis" / "dashboard_analysis.json"
    analysis_snapshot = ROOT / "ui" / "operator_dashboard" / "public" / "c5_1" / "dashboard_analysis.json"
    backups = {
        analysis_source: _read_optional(analysis_source),
        analysis_snapshot: _read_optional(analysis_snapshot),
    }

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "analyze_c5_1_heuristics.py"),
                "--summary",
                str(ROOT / "tests" / "fixtures" / "policy_comparison_missing_failure_sample.csv"),
                "--out-dir",
                str(ROOT / "outputs" / "c5_1" / "analysis"),
                "--report",
                str(ROOT / "outputs" / "c5_1" / "analysis" / "pytest_report.md"),
                "--presentation",
                str(ROOT / "outputs" / "c5_1" / "analysis" / "pytest_presentation.md"),
                "--dashboard",
                str(ROOT / "outputs" / "c5_1" / "analysis" / "pytest_dashboard.md"),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr

        export_ui_snapshots()

        expected = [
            ROOT / "ui" / "operator_dashboard" / "public" / "c5_1" / "policy_comparison.json",
            analysis_snapshot,
            ROOT / "ui" / "operator_dashboard" / "public" / "c5_1" / "sample_log.json",
            ROOT / "ui" / "operator_dashboard" / "public" / "c5_1" / "work_orders.json",
            ROOT / "ui" / "pm_worker_app" / "public" / "c5_1" / "work_orders.json",
            ROOT / "ui" / "pm_worker_app" / "public" / "c5_1" / "pm_feedback_log.json",
            ROOT / "ui" / "pm_worker_app" / "public" / "c5_1" / "sample_log.json",
        ]

        for path in expected:
            assert path.exists()

        copied_analysis = json.loads(analysis_snapshot.read_text(encoding="utf-8"))
        assert copied_analysis["recommended_policy"]
    finally:
        for path, content in backups.items():
            _restore_optional(path, content)
