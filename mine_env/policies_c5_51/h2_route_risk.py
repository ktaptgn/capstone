from __future__ import annotations

from typing import Any

from mine_env.policies_c5_51.base_route_facility_dispatch import (
    BaseRouteFacilityJointPolicy,
    RouteFacilityDispatchPolicy,
)


class H2RouteRiskDispatch(RouteFacilityDispatchPolicy):
    dispatch_id = "route_risk"

    def route_score(self, truck: dict[str, Any], route_id: str, state: dict[str, Any]) -> float:
        return self._route_value(route_id) - self._stress_cost(truck, route_id)


class H2RouteRiskPolicy(BaseRouteFacilityJointPolicy):
    policy_id = "H2"
    pm_family = "risk_priority"
    dispatch_cls = H2RouteRiskDispatch
