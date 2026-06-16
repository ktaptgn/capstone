from __future__ import annotations

from typing import Any

from mine_env.policies_c5_51 import ROUTES
from mine_env.policies_c5_51.h0_route_blind import H0RouteBlindPolicy
from mine_env.policies_c5_51.h1_route_health import H1RouteHealthPolicy
from mine_env.policies_c5_51.h2_route_risk import H2RouteRiskPolicy
from mine_env.policies_c5_51.h3_route_value import H3RouteValuePolicy
from mine_env.policies_c5_51.h4_route_flow import H4RouteFlowPolicy
from mine_env.policies_c5_51.h_time_route_hours import HTimeRouteHoursPolicy
from mine_env.policies_c5_51.base_route_facility_dispatch import (
    BaseRouteFacilityJointPolicy,
    RouteFacilityDispatchPolicy,
)


class H1RouteHealthValueGuardDispatch(RouteFacilityDispatchPolicy):
    dispatch_id = "route_health_value_guard"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.value_weight = float(
            config["grade_aware_objective"]["value_guard"]["h1_route_value_weight"]
        )

    def route_score(self, truck: dict[str, Any], route_id: str, state: dict[str, Any]) -> float:
        return self.value_weight * self._route_value(route_id) - self._weakness_stress(
            truck, route_id
        )


class H2RouteRiskValueGuardDispatch(RouteFacilityDispatchPolicy):
    dispatch_id = "route_risk_value_guard"

    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.value_bonus = float(
            config["grade_aware_objective"]["value_guard"]["h2_route_value_bonus"]
        )

    def route_score(self, truck: dict[str, Any], route_id: str, state: dict[str, Any]) -> float:
        return (1.0 + self.value_bonus) * self._route_value(route_id) - self._stress_cost(
            truck, route_id
        )


class H1ValueGuardPolicy(BaseRouteFacilityJointPolicy):
    policy_id = "H1_value_guard"
    pm_family = "condition"
    dispatch_cls = H1RouteHealthValueGuardDispatch


class H2ValueGuardPolicy(BaseRouteFacilityJointPolicy):
    policy_id = "H2_value_guard"
    pm_family = "risk_priority"
    dispatch_cls = H2RouteRiskValueGuardDispatch


ROUTE_GRADE_AWARE_POLICY_REGISTRY = {
    "H0": H0RouteBlindPolicy,
    "H_TIME": HTimeRouteHoursPolicy,
    "H1": H1RouteHealthPolicy,
    "H2": H2RouteRiskPolicy,
    "H3": H3RouteValuePolicy,
    "H4": H4RouteFlowPolicy,
    "H1_original": H1RouteHealthPolicy,
    "H1_value_guard": H1ValueGuardPolicy,
    "H2_original": H2RouteRiskPolicy,
    "H2_value_guard": H2ValueGuardPolicy,
}


def create_grade_aware_policy(policy_id: str, config: dict[str, Any]):
    if policy_id not in ROUTE_GRADE_AWARE_POLICY_REGISTRY:
        raise ValueError(f"Unknown C5.52 grade-aware policy: {policy_id}")
    return ROUTE_GRADE_AWARE_POLICY_REGISTRY[policy_id](config)


__all__ = [
    "ROUTES",
    "ROUTE_GRADE_AWARE_POLICY_REGISTRY",
    "create_grade_aware_policy",
    "H1ValueGuardPolicy",
    "H2ValueGuardPolicy",
    "H1RouteHealthValueGuardDispatch",
    "H2RouteRiskValueGuardDispatch",
]
