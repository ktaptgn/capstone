from __future__ import annotations

import pytest

from mine_env.config_c5_5 import load_config
from mine_env.simulator_c5_5 import run_policy_simulation
from tests.c5_5_helpers import CONFIG_PATH

DAYS = 10


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_one_seed_smoke_completes(config):
    summary = run_policy_simulation(config, "H2", seed=101, days=DAYS).summary
    assert summary["policy_id"] == "H2"
    assert summary["days"] == DAYS
    assert 0.0 <= summary["demand_fulfillment_rate"] <= 1.0
    assert summary["completed_loads"] >= 0
    assert summary["shovel_a_loads"] + summary["shovel_b_loads"] + summary["shovel_c_loads"] >= summary["completed_loads"]
    assert summary["crusher_1_loads"] + summary["crusher_2_loads"] == summary["completed_loads"]


def test_pm_service_capacity_never_exceeds_two(config):
    summary = run_policy_simulation(config, "H0", seed=101, days=20).summary
    assert summary["max_simultaneous_pm"] <= 2
    assert 0.0 <= summary["pm_bay_utilization"] <= 1.0


def test_cost_decomposition_sums_to_total_tco(config):
    summary = run_policy_simulation(config, "H1", seed=102, days=DAYS).summary
    parts = (
        summary["pm_cost"]
        + summary["cm_cost"]
        + summary["downtime_cost"]
        + summary["degradation_cost"]
        + summary["unmet_demand_cost"]
    )
    assert parts == pytest.approx(summary["total_tco"], abs=1e-2)


@pytest.mark.parametrize("policy_id", ["H0", "H_TIME", "H1", "H2", "H3", "H4"])
def test_all_c5_5_policies_smoke(config, policy_id):
    summary = run_policy_simulation(config, policy_id, seed=101, days=5).summary
    assert summary["policy_id"] == policy_id
    assert summary["max_simultaneous_pm"] <= 2
