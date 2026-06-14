from __future__ import annotations

from mine_env.policies_c5_4.base_joint import BaseJointPolicy


class H4FlowPolicy(BaseJointPolicy):
    """H4 -- flow/backpressure PM + capacity routing.

    The flow/backpressure philosophy on both axes: schedule PM only into spare fleet capacity
    (defer it while demand pressure is high), and send each truck to the route with the most
    remaining capacity. Throughput-first on both decisions -- maintenance and routing both yield
    to keeping the fleet hauling.
    """

    policy_id = "H4"
    pm_family = "flow_backpressure"
    dispatch_id = "H4"
