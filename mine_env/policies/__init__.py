from mine_env.policies.base_policy import BasePolicy
from mine_env.policies.h0_baseline import H0BaselinePolicy
from mine_env.policies.h1_due_health import H1DueHealthPolicy
from mine_env.policies.h2_pm_risk_priority import H2PmRiskPriorityPolicy
from mine_env.policies.h3_cost_unit_value import H3CostUnitValuePolicy
from mine_env.policies.h4_flow_backpressure import H4FlowBackpressurePolicy
from mine_env.policies.h_time_periodic_pm import HTimeDuePmPolicy


POLICY_REGISTRY = {
    "H_TIME": HTimeDuePmPolicy,
    "H0": H0BaselinePolicy,
    "H1": H1DueHealthPolicy,
    "H2": H2PmRiskPriorityPolicy,
    "H3": H3CostUnitValuePolicy,
    "H4": H4FlowBackpressurePolicy,
}


def create_policy(policy_id: str, config: dict):
    if policy_id not in POLICY_REGISTRY:
        raise ValueError(f"Unknown C5.1 policy: {policy_id}")
    return POLICY_REGISTRY[policy_id](config)


__all__ = [
    "BasePolicy",
    "POLICY_REGISTRY",
    "create_policy",
    "H0BaselinePolicy",
    "H1DueHealthPolicy",
    "H2PmRiskPriorityPolicy",
    "H3CostUnitValuePolicy",
    "H4FlowBackpressurePolicy",
    "HTimeDuePmPolicy",
]
