from __future__ import annotations

from pathlib import Path
from typing import Any

from mine_env.reliability_c5_3 import COMPONENTS

CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "c5_3.yaml"


def make_truck(truck_id: str, **observed_hi: float) -> dict[str, Any]:
    """A minimal dispatch-state truck: true + observed component HI (default healthy)."""
    truck: dict[str, Any] = {"truck_id": truck_id, "status": "AVAILABLE"}
    for component in COMPONENTS:
        value = float(observed_hi.get(component, 1.0))
        truck[f"{component}_hi"] = value
        truck[f"observed_{component}_hi"] = value
        truck[f"{component}_wear_multiplier"] = 1.0
    return truck


def dispatch_state(trucks: list[dict[str, Any]], capacities: dict[str, int] | None = None) -> dict[str, Any]:
    return {
        "dispatch_trucks": trucks,
        "route_capacity_remaining": capacities or {"A": 50, "B": 50, "C": 50},
        "demand_remaining": 100,
        "day": 1,
        "hour": 0,
    }
