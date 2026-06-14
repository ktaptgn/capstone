from __future__ import annotations

from mine_env.policies_c5_4.base_joint import BaseJointPolicy


class H1ConditionHealthPolicy(BaseJointPolicy):
    """H1 -- condition-based (CBM) PM + health routing.

    The state-aware due+health philosophy on both axes: PM a component when its observed HI
    crosses the CBM threshold (the C5.3 frozen rule, now chosen rather than imposed), and route
    each truck to the gentlest route for its weak components.
    """

    policy_id = "H1"
    pm_family = "condition"
    dispatch_id = "H1"
