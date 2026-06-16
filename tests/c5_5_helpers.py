from __future__ import annotations

from pathlib import Path
from typing import Any

from mine_env.reliability_c5_4 import COMPONENTS

CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "c5_5.yaml"


def make_truck(
    truck_id: str,
    status: str = "AVAILABLE_EMPTY",
    operating_hours_since_pm: float = 0.0,
    last_pm_day: int = 0,
    load_origin: str | None = None,
    **observed_hi: float,
) -> dict[str, Any]:
    truck: dict[str, Any] = {
        "truck_id": truck_id,
        "role": "OPERATING",
        "status": status,
        "downtime_remaining": 0,
        "load_origin": load_origin,
        "assigned_destination": None,
        "loads_completed": 0,
        "operating_hours_since_pm": float(operating_hours_since_pm),
        "last_pm_day": int(last_pm_day),
        "pm_event_count": 0,
    }
    for component in COMPONENTS:
        value = float(observed_hi.get(component, 1.0))
        truck[f"{component}_hi"] = value
        truck[f"observed_{component}_hi"] = value
        truck[f"{component}_wear_multiplier"] = 1.0
    truck["truck_hi"] = min(truck[f"{component}_hi"] for component in COMPONENTS)
    return truck


def facility_state(
    trucks: list[dict[str, Any]],
    free_bays: int = 2,
    day: int = 1,
    hour: int = 0,
    step: int = 1,
    demand_remaining: int = 100,
    slots_this_step: int = 9,
) -> dict[str, Any]:
    available_empty = [t for t in trucks if t["status"] == "AVAILABLE_EMPTY"]
    dispatchable = [t for t in trucks if t["status"] in {"AVAILABLE_EMPTY", "LOADED"}]
    available_ids = {t["truck_id"] for t in available_empty}
    return {
        "trucks": trucks,
        "available_ids": available_ids,
        "step": step,
        "free_bays": free_bays,
        "pm_context": {
            "day": day,
            "hour": hour,
            "step": step,
            "demand_remaining": demand_remaining,
            "slots_this_step": slots_this_step,
            "available_count": len(available_empty),
        },
        "dispatch_state": {
            "dispatch_trucks": dispatchable,
            "shovel_capacity_remaining": {"SHOVEL_A": 50, "SHOVEL_B": 50, "SHOVEL_C": 50},
            "crusher_capacity_remaining": {"CRUSHER_1": 50, "CRUSHER_2": 50},
            "demand_remaining": demand_remaining,
            "day": day,
            "hour": hour,
        },
    }
