from __future__ import annotations

from typing import Any

from mine_env.pm_scheduler_c5_4 import Referral, create_pm_rule
from mine_env.policies_c5_3 import create_dispatch_policy


class BaseJointPolicy:
    """C5.4 joint (PM-scheduling + dispatch) policy base.

    A C5.4 policy makes TWO decisions each step: which trucks to refer to the PM bay (and which
    components to service), and which route to send the rest on. It composes two reusable parts:

    * a PM-scheduling rule (``mine_env.pm_scheduler_c5_4``) -- the family that decides PM, and
    * a C5.3 dispatch policy (``mine_env.policies_c5_3``), reused verbatim -- the route ranker.

    ``decide(state)`` returns ``{"pm": [...], "dispatch": [...]}``:
      * ``pm``: shop-visit referrals ``(truck_id, components, risk)`` over the AVAILABLE trucks,
        priority-ordered and already capped to the free bays by the PM rule.
      * ``dispatch``: ``(truck_id, ranked_routes)`` over ALL available trucks (the C5.3 contract).
        The simulator applies the accepted PM referrals first, then dispatches the remaining
        available trucks by this ranking (skipping any that took a bay) -- so the dispatch list may
        name trucks that end up in PM; the simulator filters them. This keeps PM and dispatch
        decided in one call while respecting bay capacity.

    Both halves read only the OBSERVED (noisy) component HI -- never the latent truth (POMDP).
    The same ``decide`` signature is the contract a PPO agent targets (see
    ``mine_env.rl_interface_c5_4``), so heuristics and a learned policy are swappable.
    """

    policy_id = "BASE"
    pm_family: str = ""
    dispatch_id: str = ""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.pm_rule = create_pm_rule(self.pm_family, config)
        self.dispatch = create_dispatch_policy(self.dispatch_id, config)

    def reset(self) -> None:
        self.pm_rule.reset()

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
