from mine_env.policies_c5_4.base_joint import BaseJointPolicy
from mine_env.policies_c5_4.h0_calendar_blind import H0CalendarBlindPolicy
from mine_env.policies_c5_4.h1_condition_health import H1ConditionHealthPolicy
from mine_env.policies_c5_4.h2_risk import H2RiskPolicy
from mine_env.policies_c5_4.h3_value import H3ValuePolicy
from mine_env.policies_c5_4.h4_flow import H4FlowPolicy
from mine_env.policies_c5_4.h_time_hours import HTimeHoursPolicy


# Each policy pairs a PM-scheduling family with the matching C5.3 dispatch rule (reused verbatim).
# H_TIME is BACK (vs C5.3): once PM scheduling is a decision, an operating-hours PM timer has a
# real meaning again, so the full C5.2 PM-trigger backbone (calendar / operating-hours /
# state-aware) is represented on both the PM and the dispatch axis.
JOINT_POLICY_REGISTRY = {
    "H0": H0CalendarBlindPolicy,
    "H_TIME": HTimeHoursPolicy,
    "H1": H1ConditionHealthPolicy,
    "H2": H2RiskPolicy,
    "H3": H3ValuePolicy,
    "H4": H4FlowPolicy,
}


def create_joint_policy(policy_id: str, config: dict):
    if policy_id not in JOINT_POLICY_REGISTRY:
        raise ValueError(f"Unknown C5.4 joint policy: {policy_id}")
    return JOINT_POLICY_REGISTRY[policy_id](config)


__all__ = [
    "BaseJointPolicy",
    "JOINT_POLICY_REGISTRY",
    "create_joint_policy",
    "H0CalendarBlindPolicy",
    "HTimeHoursPolicy",
    "H1ConditionHealthPolicy",
    "H2RiskPolicy",
    "H3ValuePolicy",
    "H4FlowPolicy",
]
