from __future__ import annotations

from typing import Any

from mine_env.policies_c5_5.base_facility_dispatch import (
    BaseFacilityJointPolicy,
    FacilityDispatchPolicy,
)


class H2FacilityRiskDispatch(FacilityDispatchPolicy):
    dispatch_id = "facility_risk"

    def destination_score(
        self, truck: dict[str, Any], action: str, state: dict[str, Any]
    ) -> float:
        if action in ("SEND_TO_PM_BAY", "EMERGENCY_PM", "SAFE_STOP"):
            risk = max(self._component_risk(truck, c) for c in ("tire", "engine", "brake"))
            return 1.5 if risk >= 0.85 else -2.0
        if action == "STANDBY":
            return -0.5
        return self._facility_value(truck, action) - self._stress_cost(truck, action)


class H2FacilityRiskPolicy(BaseFacilityJointPolicy):
    policy_id = "H2"
    pm_family = "risk_priority"
    dispatch_cls = H2FacilityRiskDispatch
