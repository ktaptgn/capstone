from mine_env.policies_c5_5.base_facility_dispatch import (
    CRUSHER_ACTION_TO_ID,
    EMPTY_ACTIONS,
    LOADED_ACTIONS,
    SHOVEL_ACTION_TO_ID,
    BaseFacilityJointPolicy,
    FacilityDispatchPolicy,
)
from mine_env.policies_c5_5.h0_facility_blind import H0FacilityBlindPolicy
from mine_env.policies_c5_5.h1_facility_health import H1FacilityHealthPolicy
from mine_env.policies_c5_5.h2_facility_risk import H2FacilityRiskPolicy
from mine_env.policies_c5_5.h3_facility_value import H3FacilityValuePolicy
from mine_env.policies_c5_5.h4_facility_flow import H4FacilityFlowPolicy
from mine_env.policies_c5_5.h_time_facility_hours import HTimeFacilityHoursPolicy

FACILITY_POLICY_REGISTRY = {
    "H0": H0FacilityBlindPolicy,
    "H_TIME": HTimeFacilityHoursPolicy,
    "H1": H1FacilityHealthPolicy,
    "H2": H2FacilityRiskPolicy,
    "H3": H3FacilityValuePolicy,
    "H4": H4FacilityFlowPolicy,
}


def create_facility_policy(policy_id: str, config: dict):
    if policy_id not in FACILITY_POLICY_REGISTRY:
        raise ValueError(f"Unknown C5.5 facility policy: {policy_id}")
    return FACILITY_POLICY_REGISTRY[policy_id](config)


__all__ = [
    "BaseFacilityJointPolicy",
    "FacilityDispatchPolicy",
    "FACILITY_POLICY_REGISTRY",
    "create_facility_policy",
    "EMPTY_ACTIONS",
    "LOADED_ACTIONS",
    "SHOVEL_ACTION_TO_ID",
    "CRUSHER_ACTION_TO_ID",
    "H0FacilityBlindPolicy",
    "HTimeFacilityHoursPolicy",
    "H1FacilityHealthPolicy",
    "H2FacilityRiskPolicy",
    "H3FacilityValuePolicy",
    "H4FacilityFlowPolicy",
]
