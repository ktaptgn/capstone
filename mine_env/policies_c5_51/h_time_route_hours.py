from __future__ import annotations

from mine_env.policies_c5_51.base_route_facility_dispatch import BaseRouteFacilityJointPolicy
from mine_env.policies_c5_51.h0_route_blind import H0RouteBlindDispatch


class HTimeRouteHoursPolicy(BaseRouteFacilityJointPolicy):
    policy_id = "H_TIME"
    pm_family = "operating_hours"
    dispatch_cls = H0RouteBlindDispatch
