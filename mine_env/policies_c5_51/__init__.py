from mine_env.policies_c5_51.base_route_facility_dispatch import (
    ROUTES,
    BaseRouteFacilityJointPolicy,
    RouteFacilityDispatchPolicy,
)
from mine_env.policies_c5_51.h0_route_blind import H0RouteBlindPolicy
from mine_env.policies_c5_51.h1_route_health import H1RouteHealthPolicy
from mine_env.policies_c5_51.h2_route_risk import H2RouteRiskPolicy
from mine_env.policies_c5_51.h3_route_value import H3RouteValuePolicy
from mine_env.policies_c5_51.h4_route_flow import H4RouteFlowPolicy
from mine_env.policies_c5_51.h_time_route_hours import HTimeRouteHoursPolicy

ROUTE_FACILITY_POLICY_REGISTRY = {
    "H0": H0RouteBlindPolicy,
    "H_TIME": HTimeRouteHoursPolicy,
    "H1": H1RouteHealthPolicy,
    "H2": H2RouteRiskPolicy,
    "H3": H3RouteValuePolicy,
    "H4": H4RouteFlowPolicy,
}


def create_route_facility_policy(policy_id: str, config: dict):
    if policy_id not in ROUTE_FACILITY_POLICY_REGISTRY:
        raise ValueError(f"Unknown C5.51 route-facility policy: {policy_id}")
    return ROUTE_FACILITY_POLICY_REGISTRY[policy_id](config)


__all__ = [
    "ROUTES",
    "BaseRouteFacilityJointPolicy",
    "RouteFacilityDispatchPolicy",
    "ROUTE_FACILITY_POLICY_REGISTRY",
    "create_route_facility_policy",
    "H0RouteBlindPolicy",
    "HTimeRouteHoursPolicy",
    "H1RouteHealthPolicy",
    "H2RouteRiskPolicy",
    "H3RouteValuePolicy",
    "H4RouteFlowPolicy",
]
