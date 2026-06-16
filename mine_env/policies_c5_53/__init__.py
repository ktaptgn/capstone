from __future__ import annotations

from mine_env.policies_c5_52 import (
    ROUTES,
    ROUTE_GRADE_AWARE_POLICY_REGISTRY,
    create_grade_aware_policy,
)
from mine_env.pm_scheduler_c5_4 import create_pm_rule


class BalancedRoundRobinH4PmPolicy:
    """Audit-only synthetic comparator: H4 PM rule plus round-robin route ranking."""

    policy_id = "BALANCED_RR_H4_PM"
    synthetic_comparator = True

    def __init__(self, config: dict):
        self.pm_rule = create_pm_rule("flow_backpressure", config)
        self.index = 0

    def reset(self) -> None:
        self.pm_rule.reset()
        self.index = 0

    def decide(self, state: dict) -> dict:
        pm = self.pm_rule.select_referrals(
            state["trucks"],
            state["available_ids"],
            state["step"],
            state["free_bays"],
            state["pm_context"],
        )
        dispatch = []
        for truck in state["dispatch_state"]["dispatch_trucks"]:
            head = self.index % len(ROUTES)
            ranked = list(ROUTES[head:]) + list(ROUTES[:head])
            dispatch.append((truck["truck_id"], ranked))
            self.index += 1
        return {"pm": pm, "dispatch": dispatch}


ROUTE_CONGESTION_POLICY_REGISTRY = {
    **ROUTE_GRADE_AWARE_POLICY_REGISTRY,
    "BALANCED_RR_H4_PM": BalancedRoundRobinH4PmPolicy,
}


def create_congestion_policy(policy_id: str, config: dict):
    if policy_id == "BALANCED_RR_H4_PM":
        return BalancedRoundRobinH4PmPolicy(config)
    return create_grade_aware_policy(policy_id, config)


__all__ = [
    "ROUTES",
    "ROUTE_CONGESTION_POLICY_REGISTRY",
    "BalancedRoundRobinH4PmPolicy",
    "create_congestion_policy",
]
