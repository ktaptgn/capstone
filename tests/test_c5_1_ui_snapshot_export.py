import json
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts.export_ui_snapshots import export_ui_snapshots
from scripts.export_work_orders import export_work_orders


ROOT = Path(__file__).resolve().parents[1]


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
    export_ui_snapshots()

    expected = [
        ROOT / "ui" / "operator_dashboard" / "public" / "c5_1" / "policy_comparison.json",
        ROOT / "ui" / "operator_dashboard" / "public" / "c5_1" / "sample_log.json",
        ROOT / "ui" / "operator_dashboard" / "public" / "c5_1" / "work_orders.json",
        ROOT / "ui" / "pm_worker_app" / "public" / "c5_1" / "work_orders.json",
        ROOT / "ui" / "pm_worker_app" / "public" / "c5_1" / "pm_feedback_log.json",
        ROOT / "ui" / "pm_worker_app" / "public" / "c5_1" / "sample_log.json",
    ]

    for path in expected:
        assert path.exists()
