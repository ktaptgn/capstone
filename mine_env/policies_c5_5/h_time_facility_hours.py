from __future__ import annotations

from mine_env.policies_c5_5.h0_facility_blind import H0FacilityBlindDispatch
from mine_env.policies_c5_5.base_facility_dispatch import BaseFacilityJointPolicy


class HTimeFacilityHoursPolicy(BaseFacilityJointPolicy):
    policy_id = "H_TIME"
    pm_family = "operating_hours"
    dispatch_cls = H0FacilityBlindDispatch
