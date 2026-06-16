from __future__ import annotations

from typing import Any

from mine_env.policies_c5_51.base_route_facility_dispatch import (
    ROUTES,
    BaseRouteFacilityJointPolicy,
    RouteFacilityDispatchPolicy,
)


class H0RouteBlindDispatch(RouteFacilityDispatchPolicy):
    dispatch_id = "route_blind"

    def decide_dispatch(self, state: dict[str, Any]) -> list[tuple[str, list[str]]]:
        return [
            (truck["truck_id"], [ROUTES[(index + offset) % len(ROUTES)] for offset in range(len(ROUTES))])
            for index, truck in enumerate(state["dispatch_trucks"])
        ]

    def route_score(self, truck: dict[str, Any], route_id: str, state: dict[str, Any]) -> float:
        return 0.0


class H0RouteBlindPolicy(BaseRouteFacilityJointPolicy):
    policy_id = "H0"
    pm_family = "calendar"
    dispatch_cls = H0RouteBlindDispatch
