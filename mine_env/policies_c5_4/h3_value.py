from __future__ import annotations

from mine_env.policies_c5_4.base_joint import BaseJointPolicy


class H3ValuePolicy(BaseJointPolicy):
    """H3 -- cost-value PM + value (grade) routing.

    The cost-unit-value philosophy on both axes: PM only when the expected corrective cost it
    avoids exceeds the PM cost, and chase ore grade per cycle on dispatch. A cost-rational
    operating point that tolerates wear longer than CBM and is condition-blind on routing.
    """

    policy_id = "H3"
    pm_family = "cost_value"
    dispatch_id = "H3"
