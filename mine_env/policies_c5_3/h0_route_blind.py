from __future__ import annotations

from typing import Any

from mine_env.policies_c5_3.base_dispatch import ROUTES, BaseDispatchPolicy


class H0RouteBlindPolicy(BaseDispatchPolicy):
    """H0 -- route-blind baseline (the C5.2 calendar/baseline philosophy, recast).

    Ignores condition entirely and assigns trucks to routes round-robin. It is the
    state-blind reference the state-aware route policies (H1-H4) are measured against.
    """

    policy_id = "H0"

    def decide_dispatch(self, state: dict[str, Any]) -> list[tuple[str, list[str]]]:
        n = len(ROUTES)
        return [
            (truck["truck_id"], [ROUTES[(index + offset) % n] for offset in range(n)])
            for index, truck in enumerate(state["dispatch_trucks"])
        ]

    def route_score(self, truck: dict[str, Any], route_id: str, state: dict[str, Any]) -> float:
        return 0.0
