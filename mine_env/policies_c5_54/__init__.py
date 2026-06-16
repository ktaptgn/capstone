from __future__ import annotations

from typing import Any

import numpy as np

from mine_env.pm_scheduler_c5_4 import create_pm_rule
from mine_env.policies_c5_51.h4_route_flow import H4RouteFlowDispatch
from mine_env.policies_c5_53 import BalancedRoundRobinH4PmPolicy, ROUTES, create_congestion_policy

GUARD_METRIC_KEYS = (
    "guard_skip_count",
    "fallback_to_h4_count",
    "route_guard_violation_count",
    "shovel_guard_violation_count",
    "crusher_guard_violation_count",
    "risk_guard_violation_count",
)


class H4BalancedRoundRobinGuardPolicy:
    """Official C5.54 candidate: H4 PM plus guarded balanced route allocation."""

    policy_id = "H4_BALANCED_RR_GUARD"
    official_candidate = True

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.pm_rule = create_pm_rule("flow_backpressure", config)
        self.h4_dispatch = H4RouteFlowDispatch(config)
        guard_cfg = config["h4_balanced_rr_guard"]
        self.route_order = tuple(guard_cfg.get("route_order", ROUTES))
        self.soft_utilization_threshold = float(guard_cfg.get("soft_utilization_threshold", 0.90))
        self.risk_guard_mode = str(guard_cfg.get("risk_guard_mode", "h4_baseline_percentile"))
        self.risk_guard_level = str(guard_cfg.get("risk_guard_level", "base"))
        risk_guard_levels = guard_cfg.get("risk_guard_levels", {})
        if self.risk_guard_level in risk_guard_levels:
            self.risk_guard_percentile = float(risk_guard_levels[self.risk_guard_level])
        else:
            self.risk_guard_percentile = float(guard_cfg.get("risk_guard_percentile", 0.90))
        self.fallback_policy = str(guard_cfg.get("fallback_policy", "h4_route_score"))
        self.index = 0
        self.metrics = {key: 0 for key in GUARD_METRIC_KEYS}

    def reset(self) -> None:
        self.pm_rule.reset()
        self.h4_dispatch.reset()
        self.index = 0
        self.metrics = {key: 0 for key in GUARD_METRIC_KEYS}

    def decide(self, state: dict[str, Any]) -> dict[str, Any]:
        pm = self.pm_rule.select_referrals(
            state["trucks"],
            state["available_ids"],
            state["step"],
            state["free_bays"],
            state["pm_context"],
        )
        dispatch = self.decide_dispatch(state["dispatch_state"])
        return {"pm": pm, "dispatch": dispatch}

    def decide_dispatch(self, state: dict[str, Any]) -> list[tuple[str, list[str]]]:
        dispatch: list[tuple[str, list[str]]] = []
        trucks = list(state["dispatch_trucks"])
        for truck in trucks:
            ordered = self._rotating_order()
            accepted: list[str] = []
            rejected: list[str] = []
            risk_guard = self._risk_guard(truck, ordered, state)
            for route_id in ordered:
                violations = self._guard_violations(truck, route_id, state, risk_guard)
                if violations:
                    self.metrics["guard_skip_count"] += 1
                    for key in violations:
                        self.metrics[key] += 1
                    rejected.append(route_id)
                else:
                    accepted.append(route_id)
            if accepted:
                ranked = accepted + rejected
            else:
                self.metrics["fallback_to_h4_count"] += 1
                ranked = self._h4_ranked_routes(truck, state)
            dispatch.append((truck["truck_id"], ranked))
            self.index += 1
        dispatch.sort(key=lambda item: self._route_head_score(item[1], state), reverse=True)
        return dispatch

    def guard_metrics(self) -> dict[str, int]:
        return dict(self.metrics)

    def _rotating_order(self) -> list[str]:
        head = self.index % len(self.route_order)
        return list(self.route_order[head:]) + list(self.route_order[:head])

    def _h4_ranked_routes(self, truck: dict[str, Any], state: dict[str, Any]) -> list[str]:
        return sorted(
            ROUTES,
            key=lambda route_id: self.h4_dispatch.route_score(truck, route_id, state),
            reverse=True,
        )

    def _route_head_score(self, ranked: list[str], state: dict[str, Any]) -> float:
        if not ranked:
            return 0.0
        return float(state.get("route_capacity_remaining", {}).get(ranked[0], 0))

    def _risk_guard(self, truck: dict[str, Any], route_order: list[str], state: dict[str, Any]) -> float:
        risks = [self._route_risk(truck, route_id) for route_id in route_order]
        if not risks:
            return float("inf")
        if self.risk_guard_mode == "h4_baseline_percentile":
            return float(np.quantile(risks, self.risk_guard_percentile))
        return float(self.config["h4_balanced_rr_guard"].get("risk_guard_value", max(risks)))

    def _route_risk(self, truck: dict[str, Any], route_id: str) -> float:
        return float(self.h4_dispatch._stress_cost(truck, route_id))

    def _guard_violations(
        self,
        truck: dict[str, Any],
        route_id: str,
        state: dict[str, Any],
        risk_guard: float,
    ) -> list[str]:
        violations: list[str] = []
        route = self.config["routes"][route_id]
        if self._route_utilization(route_id, state) > self.soft_utilization_threshold:
            violations.append("route_guard_violation_count")
        if self._shovel_utilization(route["shovel_id"], state) > self.soft_utilization_threshold:
            violations.append("shovel_guard_violation_count")
        if self._crusher_utilization(route["crusher_id"], state) > self.soft_utilization_threshold:
            violations.append("crusher_guard_violation_count")
        if self._route_risk(truck, route_id) > risk_guard:
            violations.append("risk_guard_violation_count")
        return violations

    def _route_utilization(self, route_id: str, state: dict[str, Any]) -> float:
        route = self.config["routes"][route_id]
        capacity = max(float(route["capacity_loads_per_day"]), 1.0)
        remaining = float(state.get("route_capacity_remaining", {}).get(route_id, capacity))
        return (capacity - remaining) / capacity

    def _shovel_utilization(self, shovel_id: str, state: dict[str, Any]) -> float:
        capacity = max(float(self.config["facilities"]["shovels"][shovel_id]["capacity_loads_per_day"]), 1.0)
        used = 0.0
        for route_id, route in self.config["routes"].items():
            if route["shovel_id"] == shovel_id:
                route_capacity = float(route["capacity_loads_per_day"])
                remaining = float(state.get("route_capacity_remaining", {}).get(route_id, route_capacity))
                used += route_capacity - remaining
        return used / capacity

    def _crusher_utilization(self, crusher_id: str, state: dict[str, Any]) -> float:
        capacity = max(float(self.config["facilities"]["crushers"][crusher_id]["capacity_loads_per_day"]), 1.0)
        used = 0.0
        for route_id, route in self.config["routes"].items():
            if route["crusher_id"] == crusher_id:
                route_capacity = float(route["capacity_loads_per_day"])
                remaining = float(state.get("route_capacity_remaining", {}).get(route_id, route_capacity))
                used += route_capacity - remaining
        return used / capacity


ROUTE_ALLOCATION_POLICY_REGISTRY = {
    "H4": lambda config: create_congestion_policy("H4", config),
    "BALANCED_RR_H4_PM": BalancedRoundRobinH4PmPolicy,
    "H4_BALANCED_RR_GUARD": H4BalancedRoundRobinGuardPolicy,
}


def create_route_allocation_policy(policy_id: str, config: dict[str, Any]):
    if policy_id not in ROUTE_ALLOCATION_POLICY_REGISTRY:
        raise ValueError(f"Unknown C5.54 route-allocation policy: {policy_id}")
    return ROUTE_ALLOCATION_POLICY_REGISTRY[policy_id](config)


__all__ = [
    "GUARD_METRIC_KEYS",
    "ROUTES",
    "ROUTE_ALLOCATION_POLICY_REGISTRY",
    "BalancedRoundRobinH4PmPolicy",
    "H4BalancedRoundRobinGuardPolicy",
    "create_route_allocation_policy",
]
