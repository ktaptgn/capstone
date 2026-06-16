from __future__ import annotations

from typing import Any

from mine_env.pm_scheduler_c5_4 import Referral, create_pm_rule
from mine_env.reliability_c5_4 import COMPONENTS, C5_4ReliabilityModel

ROUTES = ("R_A1", "R_A2", "R_B1", "R_B2", "R_C1", "R_C2")


class RouteFacilityDispatchPolicy:
    """C5.51 route-ranker over Shovel x Crusher route pairs."""

    dispatch_id = "route_base"

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.routes = config["routes"]
        self.reliability = C5_4ReliabilityModel(config)

    def reset(self) -> None:
        pass

    def route_score(self, truck: dict[str, Any], route_id: str, state: dict[str, Any]) -> float:
        raise NotImplementedError

    def decide_dispatch(self, state: dict[str, Any]) -> list[tuple[str, list[str]]]:
        ranked: list[tuple[float, str, list[str]]] = []
        for truck in state["dispatch_trucks"]:
            routes_by_pref = sorted(
                ROUTES,
                key=lambda route_id: self.route_score(truck, route_id, state),
                reverse=True,
            )
            ranked.append(
                (
                    self.route_score(truck, routes_by_pref[0], state),
                    truck["truck_id"],
                    routes_by_pref,
                )
            )
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [(truck_id, routes) for _, truck_id, routes in ranked]

    def score_components(
        self, truck: dict[str, Any], route_id: str, state: dict[str, Any]
    ) -> dict[str, float]:
        return {
            "route_value": self._route_value(route_id),
            "risk_penalty": self._stress_cost(truck, route_id),
            "capacity_score": self._capacity_score(route_id, state),
            "queue_penalty": self._queue_penalty(route_id, state),
        }

    def _obs(self, truck: dict[str, Any], component: str) -> float:
        return float(truck[f"observed_{component}_hi"])

    def _route_value(self, route_id: str) -> float:
        route = self.routes[route_id]
        return float(route["grade"]) / max(float(route.get("cycle_time_factor", 1.0)), 0.1)

    def _stress_cost(self, truck: dict[str, Any], route_id: str) -> float:
        route = self.routes[route_id]
        return sum(
            self.reliability.component_risk_score(component, self._obs(truck, component))
            * float(route.get(f"{component}_wear_multiplier", 1.0) or 1.0)
            for component in COMPONENTS
        )

    def _weakness_stress(self, truck: dict[str, Any], route_id: str) -> float:
        route = self.routes[route_id]
        return sum(
            (1.0 - self._obs(truck, component))
            * float(route.get(f"{component}_wear_multiplier", 1.0) or 1.0)
            for component in COMPONENTS
        )

    def _capacity_score(self, route_id: str, state: dict[str, Any]) -> float:
        return float(state.get("route_capacity_remaining", {}).get(route_id, 0))

    def _queue_penalty(self, route_id: str, state: dict[str, Any]) -> float:
        route = self.routes[route_id]
        used = float(route.get("capacity_loads_per_day", 0)) - self._capacity_score(route_id, state)
        pressure = used / max(float(route.get("capacity_loads_per_day", 1)), 1.0)
        return pressure * float(route.get("queue_sensitivity", 1.0))


class BaseRouteFacilityJointPolicy:
    policy_id = "BASE"
    pm_family = ""
    dispatch_cls: type[RouteFacilityDispatchPolicy] = RouteFacilityDispatchPolicy

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
