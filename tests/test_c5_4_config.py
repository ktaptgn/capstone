from __future__ import annotations

import pytest

from mine_env.config_c5_3 import load_config as load_c5_3
from mine_env.config_c5_4 import load_config
from tests.c5_4_helpers import CONFIG_PATH

C5_3_CONFIG = CONFIG_PATH.resolve().parents[1] / "configs" / "c5_3.yaml"


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_config_loads_utf8_with_korean_comments(config):
    assert config["simulation"]["version"] == "C5.4"
    assert config["active_regime"] == "heterogeneous_condition"
    assert config["mine"]["truck_count"] == 25


def test_policy_roster_restores_h_time(config):
    assert config["policies"]["enabled"] == ["H0", "H_TIME", "H1", "H2", "H3", "H4"]


def test_pm_scheduling_block_present(config):
    pm = config["pm_scheduling"]
    assert pm["calendar"]["interval_days"] >= 1
    assert pm["operating_hours"]["due_hours"] > 0
    assert 0.0 < pm["risk_priority"]["risk_threshold"] <= 1.0
    assert pm["cost_value"]["lookahead_hauls"] >= 1
    assert 0.0 < pm["flow_backpressure"]["soft_threshold_hi"] < 1.0


def test_reliability_cost_routes_are_verbatim_from_c5_3():
    """Anti-overclaim: C5.4 must reuse the C5.3 surface unchanged -- only the decision differs."""
    c4 = load_config(CONFIG_PATH)
    c3 = load_c5_3(C5_3_CONFIG)
    for key in ("reliability", "cost", "routes", "regimes", "rule_based_pm"):
        assert c4[key] == c3[key], f"C5.4 {key} drifted from C5.3"
