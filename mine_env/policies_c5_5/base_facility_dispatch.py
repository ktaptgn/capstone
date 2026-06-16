from __future__ import annotations

from typing import Any

from mine_env.pm_scheduler_c5_4 import Referral, create_pm_rule
from mine_env.reliability_c5_4 import COMPONENTS, C5_4ReliabilityModel

EMPTY_ACTIONS = (
    "SEND_TO_SHOVEL_A",
    "SEND_TO_SHOVEL_B",
    "SEND_TO_SHOVEL_C",
    "SEND_TO_PM_BAY",
    "STANDBY",
)
LOADED_ACTIONS = ("SEND_TO_CRUSHER_1", "SEND_TO_CRUSHER_2", "EMERGENCY_PM", "SAFE_STOP")
SHOVEL_ACTION_TO_ID = {
    "SEND_TO_SHOVEL_A": "SHOVEL_A",
    "SEND_TO_SHOVEL_B": "SHOVEL_B",
    "SEND_TO_SHOVEL_C": "SHOVEL_C",
}
CRUSHER_ACTION_TO_ID = {
    "SEND_TO_CRUSHER_1": "CRUSHER_1",
    "SEND_TO_CRUSHER_2": "CRUSHER_2",
}


class FacilityDispatchPolicy:
    """C5.5 facility-destination dispatch base.

    The policy ranks valid destinations for each dispatchable truck. Empty trucks can rank shovels,
    PM bay, or standby. Loaded trucks can rank crushers or safety actions. The simulator enforces
    state validity and capacity after PM referrals are applied.
    """

    dispatch_id = "facility_base"

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.facilities = config["facilities"]
        self.reliability = C5_4ReliabilityModel(config)

    def reset(self) -> None:
        pass

    def decide_dispatch(self, state: dict[str, Any]) -> list[tuple[str, list[str]]]:
        ranked: list[tuple[float, str, list[str]]] = []
        for truck in state["dispatch_trucks"]:
            actions = EMPTY_ACTIONS if truck["status"] == "AVAILABLE_EMPTY" else LOADED_ACTIONS
            ranked_actions = sorted(
                actions,
                key=lambda action: self.destination_score(truck, action, state),
                reverse=True,
            )
            ranked.append(
                (
                    self.destination_score(truck, ranked_actions[0], state),
                    truck["truck_id"],
                    list(ranked_actions),
                )
            )
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [(truck_id, actions) for _, truck_id, actions in ranked]

    def destination_score(
        self, truck: dict[str, Any], action: str, state: dict[str, Any]
    ) -> float:
        raise NotImplementedError

    def _obs(self, truck: dict[str, Any], component: str) -> float:
        return float(truck[f"observed_{component}_hi"])

    def _component_risk(self, truck: dict[str, Any], component: str) -> float:
        return self.reliability.component_risk_score(component, self._obs(truck, component))

    def _shovel(self, action: str) -> dict[str, Any]:
        return self.facilities["shovels"][SHOVEL_ACTION_TO_ID[action]]

    def _crusher(self, action: str) -> dict[str, Any]:
        return self.facilities["crushers"][CRUSHER_ACTION_TO_ID[action]]

    def _stress_cost(self, truck: dict[str, Any], action: str) -> float:
        if action in SHOVEL_ACTION_TO_ID:
            profile = self._shovel(action)
        elif action in CRUSHER_ACTION_TO_ID:
            profile = self._crusher(action)
        else:
            return 0.0
        return sum(
            self._component_risk(truck, component)
            * float(profile.get(f"{component}_wear_multiplier", 1.0) or 1.0)
            for component in COMPONENTS
        )

    def _weakness_stress(self, truck: dict[str, Any], action: str) -> float:
        if action in SHOVEL_ACTION_TO_ID:
            profile = self._shovel(action)
        elif action in CRUSHER_ACTION_TO_ID:
            profile = self._crusher(action)
        else:
            return 0.0
        return sum(
            (1.0 - self._obs(truck, component))
            * float(profile.get(f"{component}_wear_multiplier", 1.0) or 1.0)
            for component in COMPONENTS
        )

    def _facility_value(self, truck: dict[str, Any], action: str) -> float:
        if action in SHOVEL_ACTION_TO_ID:
            shovel = self._shovel(action)
            return float(shovel["grade_index"]) / max(float(shovel["cycle_time_factor"]), 0.1)
        if action in CRUSHER_ACTION_TO_ID:
            crusher = self._crusher(action)
            origin = truck.get("load_origin")
            hardness = 1.0
            if origin:
                hardness = float(self.facilities["shovels"][origin].get("hardness_factor", 1.0))
            service_time = hardness * float(crusher.get("travel_time_factor", 1.0))
            return 1.0 / max(service_time, 0.1)
        return -1.0

    def _capacity_score(self, action: str, state: dict[str, Any]) -> float:
        if action in SHOVEL_ACTION_TO_ID:
            return float(state.get("shovel_capacity_remaining", {}).get(SHOVEL_ACTION_TO_ID[action], 0))
        if action in CRUSHER_ACTION_TO_ID:
            return float(state.get("crusher_capacity_remaining", {}).get(CRUSHER_ACTION_TO_ID[action], 0))
        return 0.0


class BaseFacilityJointPolicy:
    policy_id = "BASE"
    pm_family = ""
    dispatch_cls: type[FacilityDispatchPolicy] = FacilityDispatchPolicy

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.pm_rule = create_pm_rule(self.pm_family, config)
        self.dispatch = self.dispatch_cls(config)

    def reset(self) -> None:
        self.pm_rule.reset()
        self.dispatch.reset()

    def decide(self, state: dict[str, Any]) -> dict[str, Any]:
        pm: list[Referral] = self.pm_rule.select_referrals(
            state["trucks"],
            state["available_ids"],
            state["step"],
            state["free_bays"],
            state["pm_context"],
        )
        dispatch = self.dispatch.decide_dispatch(state["dispatch_state"])
        return {"pm": pm, "dispatch": dispatch}
