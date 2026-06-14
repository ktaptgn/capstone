from __future__ import annotations

from pathlib import Path
from typing import Any

from mine_env.reliability_c5_4 import COMPONENTS

CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "c5_4.yaml"


def make_truck(
    truck_id: str,
    operating_hours_since_pm: float = 0.0,
    last_pm_day: int = 0,
    status: str = "AVAILABLE",
    **observed_hi: float,
) -> dict[str, Any]:
    """A minimal C5.4 truck for unit tests: true + observed component HI plus PM bookkeeping."""
    truck: dict[str, Any] = {
        "truck_id": truck_id,
        "status": status,
        "downtime_remaining": 0,
        "operating_hours_since_pm": float(operating_hours_since_pm),
        "last_pm_day": int(last_pm_day),
        "pm_event_count": 0,
    }
    for component in COMPONENTS:
        value = float(observed_hi.get(component, 1.0))
        truck[f"{component}_hi"] = value
        truck[f"observed_{component}_hi"] = value
        truck[f"{component}_wear_multiplier"] = 1.0
    return truck


def joint_state(
    trucks: list[dict[str, Any]],
    free_bays: int = 2,
    day: int = 1,
    hour: int = 0,
    step: int = 1,
    demand_remaining: int = 100,
    slots_this_step: int = 9,
    capacities: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Build the full state dict that a C5.4 joint policy's ``decide`` expects."""
    available = [t for t in trucks if t["status"] == "AVAILABLE"]
    available_ids = {t["truck_id"] for t in available}
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
            "available_count": len(available),
        },
        "dispatch_state": {
            "dispatch_trucks": available,
            "route_capacity_remaining": capacities or {"A": 50, "B": 50, "C": 50},
            "demand_remaining": demand_remaining,
            "day": day,
            "hour": hour,
        },
    }
