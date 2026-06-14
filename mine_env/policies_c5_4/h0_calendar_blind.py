from __future__ import annotations

from mine_env.policies_c5_4.base_joint import BaseJointPolicy


class H0CalendarBlindPolicy(BaseJointPolicy):
    """H0 -- the fully blind baseline: calendar PM + route-blind round-robin dispatch.

    The state-blind reference both decisions are measured against. PM fires on a fixed calendar
    interval (full vehicle service, condition-blind) and trucks are assigned to routes
    round-robin, ignoring health entirely on both axes.
    """

    policy_id = "H0"
    pm_family = "calendar"
    dispatch_id = "H0"
