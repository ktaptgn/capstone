from __future__ import annotations

import pytest

from mine_env.config_c5_52 import CONFIG_PATH, load_config
from mine_env.simulator_c5_52 import run_policy_simulation


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_grade_aware_summary_fields(config):
    summary = run_policy_simulation(
        config, "H2_original", seed=101, days=5, shortfall_sensitivity="base"
    ).summary
    assert summary["total_tco_v1"] == summary["total_tco"]
    assert summary["target_effective_output"] > 0
    assert 0 <= summary["effective_fulfillment_rate"]
    assert 0 <= summary["avg_grade_per_load"] <= 1
    assert summary["total_tco_v2"] >= summary["total_tco_v1"]


def test_shortfall_sensitivity_changes_tco_v2(config):
    low = run_policy_simulation(config, "H2_original", seed=101, days=5, shortfall_sensitivity="low").summary
    high = run_policy_simulation(config, "H2_original", seed=101, days=5, shortfall_sensitivity="high").summary
    assert high["effective_output_shortfall_cost"] >= low["effective_output_shortfall_cost"]
    assert high["total_tco_v2"] >= low["total_tco_v2"]


def test_value_guard_can_run(config):
    summary = run_policy_simulation(
        config, "H2_value_guard", seed=101, days=5, shortfall_sensitivity="base"
    ).summary
    assert summary["policy_id"] == "H2_value_guard"
    assert summary["max_simultaneous_pm"] <= 2
