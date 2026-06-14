from __future__ import annotations

from typing import Any

from mine_env.policies_c5_3.base_dispatch import BaseDispatchPolicy


class H3ValueRoutePolicy(BaseDispatchPolicy):
    """H3 -- cost-unit-value philosophy recast as value routing.

    The C6 ``value`` strategy: chase ore grade per unit cycle time
    (``grade / cycle_time_factor``), condition-blind. Because the C5.3 objective is pure TCO
    (production value excluded), grade-chasing earns no cost credit while exposing trucks to
    whatever wear the high-grade route carries -- so H3 is a deliberately condition-blind
    baseline that tests whether chasing production hurts on a TCO objective.
    """

    policy_id = "H3"

    def route_score(self, truck: dict[str, Any], route_id: str, state: dict[str, Any]) -> float:
        return self._route_value(route_id)
