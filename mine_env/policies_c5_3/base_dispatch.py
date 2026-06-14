from __future__ import annotations

from typing import Any

from mine_env.reliability_c5_3 import COMPONENTS, C5_3ReliabilityModel


ROUTES = ("A", "B", "C")


class BaseDispatchPolicy:
    """C5.3 dispatch-only policy base.

    A policy assigns each currently-available truck to a route (A/B/C). Preventive
    maintenance is delegated to the shared fixed rule engine, so policies differ ONLY in
    route selection -- that is the entire C5.3 decision variable. Policies read the OBSERVED
    (noisy) component HI, never the latent truth.

    ``decide_dispatch`` returns ``(truck_id, ranked_routes)`` in truck-priority order: each
    truck carries its routes ranked best-first, and the simulator assigns the first route that
    still has daily capacity (so a truck whose preferred route is full falls back to its next
    choice rather than idling -- the C6 behaviour, where full routes are masked and the policy
    re-picks among the rest). The truck priority order also decides WHICH trucks haul when
    there are more available trucks than demand slots (e.g. a risk-aware policy lets healthy
    trucks haul and rests worn ones).
    """

    policy_id = "BASE"

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.routes = config["routes"]
        self.reliability = C5_3ReliabilityModel(config)

    # subclasses override this; higher score == more preferred (truck, route) pairing
    def route_score(self, truck: dict[str, Any], route_id: str, state: dict[str, Any]) -> float:
        raise NotImplementedError

    def decide_dispatch(self, state: dict[str, Any]) -> list[tuple[str, list[str]]]:
        ranked: list[tuple[float, str, list[str]]] = []
        for truck in state["dispatch_trucks"]:
            routes_by_pref = sorted(
                ROUTES, key=lambda route_id: self.route_score(truck, route_id, state), reverse=True
            )
            top_score = self.route_score(truck, routes_by_pref[0], state)
            ranked.append((top_score, truck["truck_id"], routes_by_pref))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [(truck_id, routes) for _, truck_id, routes in ranked]

    # --- shared scoring helpers (all on OBSERVED HI) ---
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
