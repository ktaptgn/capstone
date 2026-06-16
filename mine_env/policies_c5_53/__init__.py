from __future__ import annotations

from mine_env.policies_c5_52 import (
    ROUTES,
    ROUTE_GRADE_AWARE_POLICY_REGISTRY,
    create_grade_aware_policy,
)

ROUTE_CONGESTION_POLICY_REGISTRY = ROUTE_GRADE_AWARE_POLICY_REGISTRY


def create_congestion_policy(policy_id: str, config: dict):
    return create_grade_aware_policy(policy_id, config)


__all__ = [
    "ROUTES",
    "ROUTE_CONGESTION_POLICY_REGISTRY",
    "create_congestion_policy",
]
