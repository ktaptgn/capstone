from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mine_env.config_c5_1 import load_c5_1_config
from mine_env.maintenance_c5_1 import C5_1MaintenanceModel


PM_ACTIONS = {"PM_TIRE", "PM_VEHICLE", "PM_VEHICLE_BALANCED"}
STATUS_VALUES = {
    "PENDING",
    "ACCEPTED",
    "IN_PROGRESS",
    "COMPLETED",
    "REJECTED",
    "REVIEW_REQUIRED",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export C5.1 PM work orders.")
    parser.add_argument("--policy", default="H3", help="Policy id, default H3")
    parser.add_argument("--seed", type=int, default=1, help="Seed value, default 1")
    parser.add_argument("--config", default="configs/c5_1.yaml")
    return parser.parse_args()


def _priority(record: dict[str, Any]) -> str:
    pm_due = float(record.get("pm_due_hours", 999))
    truck_hi = float(record.get("truck_hi", 1.0))
    tire_hi = float(record.get("tire_hi", 1.0))
    if pm_due <= 6 or truck_hi <= 0.45 or tire_hi <= 0.4:
        return "HIGH"
    if pm_due <= 12 or truck_hi <= 0.55 or tire_hi <= 0.5:
        return "MEDIUM"
    return "LOW"


def _source_log(log_dir: Path, policy: str, seed: int) -> Path:
    preferred = log_dir / f"{policy}_seed_{seed}.json"
    if preferred.exists():
        return preferred
    h3_seed1 = log_dir / "H3_seed_1.json"
    if h3_seed1.exists():
        return h3_seed1
    matches = sorted(log_dir.glob("*.json"))
    if not matches:
        raise FileNotFoundError(f"No C5.1 log JSON files found in {log_dir}")
    return matches[0]


def export_work_orders(config_path: str | Path, policy: str, seed: int) -> Path:
    config = load_c5_1_config(config_path)
    maintenance = C5_1MaintenanceModel(config)
    log_dir = ROOT / config["outputs"]["log_dir"]
    output_dir = ROOT / "outputs" / "c5_1" / "work_orders"
    output_dir.mkdir(parents=True, exist_ok=True)

    source_log = _source_log(log_dir, policy, seed)
    payload = json.loads(source_log.read_text(encoding="utf-8"))
    records = payload.get("records", payload if isinstance(payload, list) else [])
    effective_policy = payload.get("policy_id", policy)
    effective_seed = int(payload.get("seed", seed))

    work_orders = []
    for idx, record in enumerate(records):
        action = record.get("action")
        if action not in PM_ACTIONS:
            continue
        maintenance_action = maintenance.resolve_action(action)
        work_orders.append(
            {
                "work_order_id": f"WO-{effective_policy}-{effective_seed}-{len(work_orders) + 1:04d}",
                "source_policy": effective_policy,
                "seed": effective_seed,
                "step_idx": idx,
                "truck_id": record["truck_id"],
                "action": action,
                "priority": _priority(record),
                "reason": record.get("reason_code", "PM_ACTION_FROM_C5_1_LOG"),
                "estimated_duration_hours": maintenance_action.duration_hours,
                "status": "PENDING",
                "created_at": datetime.now().replace(microsecond=0).isoformat(),
                "source_log": source_log.name,
            }
        )

    work_order_path = output_dir / f"work_orders_{effective_policy}_seed{effective_seed}.json"
    work_order_path.write_text(json.dumps(work_orders, indent=2), encoding="utf-8")

    feedback_path = output_dir / "pm_feedback_log.json"
    if not feedback_path.exists():
        feedback_path.write_text("[]\n", encoding="utf-8")

    print(f"Work orders: {work_order_path}")
    print(f"Feedback log: {feedback_path}")
    return work_order_path


def main() -> None:
    args = parse_args()
    export_work_orders(args.config, args.policy, args.seed)


if __name__ == "__main__":
    main()
