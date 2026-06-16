from __future__ import annotations

from typing import Any

from mine_env.policies_c5_5.base_facility_dispatch import (
    BaseFacilityJointPolicy,
    FacilityDispatchPolicy,
)


class H4FacilityFlowDispatch(FacilityDispatchPolicy):
    dispatch_id = "facility_flow"

    def destination_score(
        self, truck: dict[str, Any], action: str, state: dict[str, Any]
    ) -> float:
        if action in ("SEND_TO_PM_BAY", "EMERGENCY_PM", "SAFE_STOP"):
            return -1.0
        if action == "STANDBY":
            return 0.5 if int(state.get("demand_remaining", 0)) <= 0 else -0.5
        return self._capacity_score(action, state)


class H4FacilityFlowPolicy(BaseFacilityJointPolicy):
    policy_id = "H4"
    pm_family = "flow_backpressure"
    dispatch_cls = H4FacilityFlowDispatch
