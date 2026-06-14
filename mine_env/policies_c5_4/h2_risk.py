from __future__ import annotations

from mine_env.policies_c5_4.base_joint import BaseJointPolicy


class H2RiskPolicy(BaseJointPolicy):
    """H2 -- risk-priority PM + risk-aware routing.

    The PM-risk-priority philosophy on both axes: PM the highest-risk components first, and steer
    worn trucks away from high-stress routes (``value - sum(component_risk x route_wear)``). The
    risk lens drives both maintenance and dispatch.
    """

    policy_id = "H2"
    pm_family = "risk_priority"
    dispatch_id = "H2"
