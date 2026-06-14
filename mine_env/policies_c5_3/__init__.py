from mine_env.policies_c5_3.base_dispatch import BaseDispatchPolicy
from mine_env.policies_c5_3.h0_route_blind import H0RouteBlindPolicy
from mine_env.policies_c5_3.h1_health_route import H1HealthRoutePolicy
from mine_env.policies_c5_3.h2_risk_route import H2RiskRoutePolicy
from mine_env.policies_c5_3.h3_value_route import H3ValueRoutePolicy
from mine_env.policies_c5_3.h4_flow_route import H4FlowRoutePolicy


# H_TIME is intentionally absent: an operating-hours PM-timing policy has no dispatch
# analogue once PM is delegated to the fixed rule engine (it would equal H0's dispatch).
DISPATCH_POLICY_REGISTRY = {
    "H0": H0RouteBlindPolicy,
    "H1": H1HealthRoutePolicy,
    "H2": H2RiskRoutePolicy,
    "H3": H3ValueRoutePolicy,
    "H4": H4FlowRoutePolicy,
}


def create_dispatch_policy(policy_id: str, config: dict):
    if policy_id not in DISPATCH_POLICY_REGISTRY:
        raise ValueError(f"Unknown C5.3 dispatch policy: {policy_id}")
    return DISPATCH_POLICY_REGISTRY[policy_id](config)


__all__ = [
    "BaseDispatchPolicy",
    "DISPATCH_POLICY_REGISTRY",
    "create_dispatch_policy",
    "H0RouteBlindPolicy",
    "H1HealthRoutePolicy",
    "H2RiskRoutePolicy",
    "H3ValueRoutePolicy",
    "H4FlowRoutePolicy",
]
