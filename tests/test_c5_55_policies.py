from __future__ import annotations

import pytest

from mine_env.config_c5_55 import CONFIG_PATH, load_config
from mine_env.policies_c5_55 import (
    GUARD_METRIC_KEYS,
    ROUTE_H5_POLICY_REGISTRY,
    H5AggressivePolicy,
    H5Policy,
    create_h5_policy,
)
from tests.c5_51_helpers import make_truck, route_state


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_c5_55_policy_registry(config):
    assert set(config["policies"]["enabled"]).issubset(set(ROUTE_H5_POLICY_REGISTRY))
    assert "H5" in ROUTE_H5_POLICY_REGISTRY
    assert "H5_AGGRESSIVE" in ROUTE_H5_POLICY_REGISTRY
    assert "BALANCED_RR_H4_PM" in ROUTE_H5_POLICY_REGISTRY


def test_h5_default_uses_freeze_settings(config):
    policy = create_h5_policy("H5", config)
    assert isinstance(policy, H5Policy)
    assert policy.soft_utilization_threshold == pytest.approx(0.90)
    assert policy.risk_guard_level == "base"
    assert policy.risk_guard_percentile == pytest.approx(0.90)


def test_h5_aggressive_uses_sensitivity_settings(config):
    policy = create_h5_policy("H5_AGGRESSIVE", config)
    assert isinstance(policy, H5AggressivePolicy)
    assert policy.soft_utilization_threshold == pytest.approx(0.85)
    assert policy.risk_guard_level == "strict"
    assert policy.risk_guard_percentile == pytest.approx(0.75)


def test_h5_returns_ranked_routes_and_guard_metrics(config):
    policy = create_h5_policy("H5", config)
    decision = policy.decide(route_state([make_truck("T01"), make_truck("T02")]))
    assert set(decision) == {"pm", "dispatch"}
    first = dict(decision["dispatch"])["T01"]
    assert set(first) == set(config["routes"])
    assert set(policy.guard_metrics()) == set(GUARD_METRIC_KEYS)
