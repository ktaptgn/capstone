from __future__ import annotations

import pytest

from mine_env.config_c5_53 import CONFIG_PATH, load_config
from mine_env.policies_c5_53 import ROUTE_CONGESTION_POLICY_REGISTRY, ROUTES, create_congestion_policy
from tests.c5_51_helpers import make_truck, route_state


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_registry_contains_c5_52_policy_family(config):
    assert set(config["policies"]["enabled"]).issubset(set(ROUTE_CONGESTION_POLICY_REGISTRY))
    for policy_id in (
        "H0",
        "H_TIME",
        "H1",
        "H2",
        "H3",
        "H4",
        "H1_original",
        "H1_value_guard",
        "H2_original",
        "H2_value_guard",
    ):
        assert policy_id in ROUTE_CONGESTION_POLICY_REGISTRY
    assert "BALANCED_RR_H4_PM" in ROUTE_CONGESTION_POLICY_REGISTRY


@pytest.mark.parametrize("policy_id", ["H0", "H_TIME", "H1", "H2", "H3", "H4"])
def test_congestion_policies_return_ranked_routes(config, policy_id):
    policy = create_congestion_policy(policy_id, config)
    decision = policy.decide(route_state([make_truck("T01", tire=0.3), make_truck("T02")]))
    assert set(decision) == {"pm", "dispatch"}
    for _truck_id, ranked in decision["dispatch"]:
        assert set(ranked) == set(ROUTES)


def test_balanced_rr_h4_pm_policy_runs_as_synthetic_comparator(config):
    policy = create_congestion_policy("BALANCED_RR_H4_PM", config)
    assert getattr(policy, "synthetic_comparator", False) is True
    decision = policy.decide(route_state([make_truck("T01"), make_truck("T02")]))
    ranked_routes = [ranked for _truck_id, ranked in decision["dispatch"]]
    assert ranked_routes[0][0] == "R_A1"
    assert ranked_routes[1][0] == "R_A2"
