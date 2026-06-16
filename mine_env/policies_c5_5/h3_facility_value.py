from __future__ import annotations

from typing import Any

from mine_env.policies_c5_5.base_facility_dispatch import (
    BaseFacilityJointPolicy,
    FacilityDispatchPolicy,
)


class H3FacilityValueDispatch(FacilityDispatchPolicy):
    dispatch_id = "facility_value"

    def destination_score(
        self, truck: dict[str, Any], action: str, state: dict[str, Any]
    ) -> float:
        if action in ("SEND_TO_PM_BAY", "EMERGENCY_PM", "SAFE_STOP", "STANDBY"):
            return -2.0
        if action.startswith("SEND_TO_SHOVEL_"):
            return float(self._shovel(action)["grade_index"])
        return self._facility_value(truck, action)


class H3FacilityValuePolicy(BaseFacilityJointPolicy):
    policy_id = "H3"
    pm_family = "cost_value"
    dispatch_cls = H3FacilityValueDispatch
