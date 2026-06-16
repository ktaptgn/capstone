from __future__ import annotations

import pytest

from mine_env.config_c5_52 import CONFIG_PATH, load_config
from mine_env.policies_c5_52 import ROUTES, ROUTE_GRADE_AWARE_POLICY_REGISTRY, create_grade_aware_policy
from tests.c5_51_helpers import make_truck, route_state


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_registry_contains_required_original_and_value_guard_policies(config):
    assert set(config["policies"]["enabled"]).issubset(set(ROUTE_GRADE_AWARE_POLICY_REGISTRY))
    for policy_id in ("H0", "H_TIME", "H1", "H2", "H3", "H4", "H1_original", "H1_value_guard", "H2_original", "H2_value_guard"):
        assert policy_id in ROUTE_GRADE_AWARE_POLICY_REGISTRY


@pytest.mark.parametrize("policy_id", ["H0", "H_TIME", "H1", "H2", "H3", "H4", "H1_original", "H1_value_guard", "H2_original", "H2_value_guard"])
def test_policies_return_ranked_routes(config, policy_id):
    policy = create_grade_aware_policy(policy_id, config)
    decision = policy.decide(route_state([make_truck("T01", tire=0.3), make_truck("T02")]))
    assert set(decision) == {"pm", "dispatch"}
    for _tid, ranked in decision["dispatch"]:
        assert set(ranked) == set(ROUTES)


def test_value_guard_changes_h1_route_ranking(config):
    worn = make_truck("T01", tire=0.25, brake=0.25)
    original = create_grade_aware_policy("H1_original", config)
    guarded = create_grade_aware_policy("H1_value_guard", config)
    assert dict(original.decide(route_state([worn]))["dispatch"])["T01"] != dict(
        guarded.decide(route_state([worn]))["dispatch"]
    )["T01"]
