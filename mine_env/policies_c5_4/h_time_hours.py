from __future__ import annotations

from mine_env.policies_c5_4.base_joint import BaseJointPolicy


class HTimeHoursPolicy(BaseJointPolicy):
    """H_TIME -- operating-hours PM + route-blind dispatch.

    The usage-based blind baseline (the C5.2 H_TIME analogue, which C5.3 had to drop because PM
    was fixed): PM when a truck's operating-hours-since-PM reach a usage budget, full service,
    blind to component condition; dispatch stays route-blind round-robin. Restored in C5.4
    because PM scheduling is a decision again, so an operating-hours timer is a genuine policy.
    """

    policy_id = "H_TIME"
    pm_family = "operating_hours"
    dispatch_id = "H0"
