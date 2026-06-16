from __future__ import annotations

import copy
from typing import Any

from mine_env.policies_c5_53 import ROUTE_CONGESTION_POLICY_REGISTRY, create_congestion_policy
from mine_env.policies_c5_54 import (
    GUARD_METRIC_KEYS,
    ROUTES,
    H4BalancedRoundRobinGuardPolicy,
)


def _guarded_config(
    config: dict[str, Any],
    threshold: float,
    risk_level: str,
    risk_percentile: float,
) -> dict[str, Any]:
    cfg = copy.deepcopy(config)
    guard = cfg["h4_balanced_rr_guard"]
    guard["soft_utilization_threshold"] = float(threshold)
    guard["risk_guard_level"] = str(risk_level)
    guard["risk_guard_percentile"] = float(risk_percentile)
    return cfg


class H5Policy(H4BalancedRoundRobinGuardPolicy):
    """Official C5.55 H5: guarded H4 route allocation frozen at 0.90/base."""

    policy_id = "H5"
    official_policy = True

    def __init__(self, config: dict[str, Any]):
        h5 = config["h5_policy"]
        super().__init__(
            _guarded_config(
                config,
                h5["soft_utilization_threshold"],
                h5["risk_guard_level"],
                h5["risk_guard_percentile"],
            )
        )


class H5AggressivePolicy(H4BalancedRoundRobinGuardPolicy):
    """Sensitivity comparator: guarded H4 route allocation frozen at 0.85/strict."""

    policy_id = "H5_AGGRESSIVE"
    sensitivity_comparator = True

    def __init__(self, config: dict[str, Any]):
        h5 = config["h5_policy"]
        super().__init__(
            _guarded_config(
                config,
                h5["aggressive_soft_utilization_threshold"],
                h5["aggressive_risk_guard_level"],
                h5["aggressive_risk_guard_percentile"],
            )
        )


ROUTE_H5_POLICY_REGISTRY = {
    **ROUTE_CONGESTION_POLICY_REGISTRY,
    "H5": H5Policy,
    "H5_AGGRESSIVE": H5AggressivePolicy,
}


def create_h5_policy(policy_id: str, config: dict[str, Any]):
    if policy_id == "H5":
        return H5Policy(config)
    if policy_id == "H5_AGGRESSIVE":
        return H5AggressivePolicy(config)
    if policy_id in ROUTE_CONGESTION_POLICY_REGISTRY:
        return create_congestion_policy(policy_id, config)
    raise ValueError(f"Unknown C5.55 H5 benchmark policy: {policy_id}")


__all__ = [
    "GUARD_METRIC_KEYS",
    "ROUTES",
    "ROUTE_H5_POLICY_REGISTRY",
    "H5Policy",
    "H5AggressivePolicy",
    "create_h5_policy",
]
