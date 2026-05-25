from mine_env.policies.base_policy import BasePolicy
from mine_env.policies.h0_baseline import H0BaselinePolicy
from mine_env.policies.h1_bottleneck_dispatch import H1BottleneckDispatchPolicy
from mine_env.policies.h2_pm_risk_priority import H2PmRiskPriorityPolicy
from mine_env.policies.h3_cost_unit_value import H3CostUnitValuePolicy
from mine_env.policies.h4_flow_backpressure import H4FlowBackpressurePolicy


POLICY_REGISTRY = {
    "H0": H0BaselinePolicy,
    "H1": H1BottleneckDispatchPolicy,
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
    "H1BottleneckDispatchPolicy",
    "H2PmRiskPriorityPolicy",
    "H3CostUnitValuePolicy",
    "H4FlowBackpressurePolicy",
]
