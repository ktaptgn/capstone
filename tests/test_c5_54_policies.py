from __future__ import annotations

import pytest

from mine_env.config_c5_54 import CONFIG_PATH, load_config
from mine_env.policies_c5_54 import (
    GUARD_METRIC_KEYS,
    ROUTE_ALLOCATION_POLICY_REGISTRY,
    create_route_allocation_policy,
)
from tests.c5_51_helpers import make_truck, route_state


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_c5_54_policy_registry(config):
    assert set(config["policies"]["enabled"]).issubset(set(ROUTE_ALLOCATION_POLICY_REGISTRY))
    assert set(ROUTE_ALLOCATION_POLICY_REGISTRY) == {
        "H4",
        "BALANCED_RR_H4_PM",
        "H4_BALANCED_RR_GUARD",
    }


def test_h4_balanced_rr_guard_returns_ranked_routes(config):
    policy = create_route_allocation_policy("H4_BALANCED_RR_GUARD", config)
    decision = policy.decide(route_state([make_truck("T01"), make_truck("T02")]))
    assert set(decision) == {"pm", "dispatch"}
    first = dict(decision["dispatch"])["T01"]
    assert set(first) == set(config["routes"])
    assert first[0] in config["h4_balanced_rr_guard"]["route_order"]
    assert set(policy.guard_metrics()) == set(GUARD_METRIC_KEYS)


def test_h4_balanced_rr_guard_fallback_when_all_routes_over_guard(config):
    policy = create_route_allocation_policy("H4_BALANCED_RR_GUARD", config)
    state = route_state([make_truck("T01")])
    state["dispatch_state"]["route_capacity_remaining"] = {route_id: 0 for route_id in config["routes"]}
    decision = policy.decide(state)
    assert dict(decision["dispatch"])["T01"]
    assert policy.guard_metrics()["fallback_to_h4_count"] == 1
    assert policy.guard_metrics()["guard_skip_count"] >= len(config["routes"])
