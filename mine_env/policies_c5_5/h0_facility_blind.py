from __future__ import annotations

from typing import Any

from mine_env.policies_c5_5.base_facility_dispatch import (
    CRUSHER_ACTION_TO_ID,
    EMPTY_ACTIONS,
    LOADED_ACTIONS,
    SHOVEL_ACTION_TO_ID,
    BaseFacilityJointPolicy,
    FacilityDispatchPolicy,
)


class H0FacilityBlindDispatch(FacilityDispatchPolicy):
    dispatch_id = "facility_blind"

    def decide_dispatch(self, state: dict[str, Any]) -> list[tuple[str, list[str]]]:
        empty_shovels = list(SHOVEL_ACTION_TO_ID)
        loaded_crushers = list(CRUSHER_ACTION_TO_ID)
        decisions: list[tuple[str, list[str]]] = []
        empty_index = 0
        loaded_index = 0
        for truck in state["dispatch_trucks"]:
            if truck["status"] == "AVAILABLE_EMPTY":
                first = [empty_shovels[(empty_index + i) % len(empty_shovels)] for i in range(len(empty_shovels))]
                decisions.append((truck["truck_id"], first + ["SEND_TO_PM_BAY", "STANDBY"]))
                empty_index += 1
            elif truck["status"] == "LOADED":
                first = [loaded_crushers[(loaded_index + i) % len(loaded_crushers)] for i in range(len(loaded_crushers))]
                decisions.append((truck["truck_id"], first + ["EMERGENCY_PM", "SAFE_STOP"]))
                loaded_index += 1
        return decisions

    def destination_score(
        self, truck: dict[str, Any], action: str, state: dict[str, Any]
    ) -> float:
        if action in EMPTY_ACTIONS or action in LOADED_ACTIONS:
            return 0.0
        return -1.0


class H0FacilityBlindPolicy(BaseFacilityJointPolicy):
    policy_id = "H0"
    pm_family = "calendar"
    dispatch_cls = H0FacilityBlindDispatch
