from __future__ import annotations

from typing import Any

from mine_env.policies_c5_5.base_facility_dispatch import (
    BaseFacilityJointPolicy,
    FacilityDispatchPolicy,
)


class H1FacilityHealthDispatch(FacilityDispatchPolicy):
    dispatch_id = "facility_health"

    def destination_score(
        self, truck: dict[str, Any], action: str, state: dict[str, Any]
    ) -> float:
        if action in ("SEND_TO_PM_BAY", "EMERGENCY_PM", "SAFE_STOP"):
            return 2.0 if min(self._obs(truck, c) for c in ("tire", "engine", "brake")) <= 0.18 else -2.0
        if action == "STANDBY":
            return 0.2 if min(self._obs(truck, c) for c in ("tire", "engine", "brake")) <= 0.30 else -1.5
        return -self._weakness_stress(truck, action)


class H1FacilityHealthPolicy(BaseFacilityJointPolicy):
    policy_id = "H1"
    pm_family = "condition"
    dispatch_cls = H1FacilityHealthDispatch
