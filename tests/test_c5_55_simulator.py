from __future__ import annotations

import pytest

from mine_env.config_c5_55 import CONFIG_PATH, load_config
from mine_env.policies_c5_55 import GUARD_METRIC_KEYS
from mine_env.simulator_c5_55 import run_policy_simulation


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


@pytest.mark.parametrize(
    "policy_id",
    ["H0", "H_TIME", "H1", "H2", "H3", "H4", "H5", "BALANCED_RR_H4_PM", "H5_AGGRESSIVE"],
)
def test_c5_55_benchmark_policies_run(config, policy_id):
    summary = run_policy_simulation(config, policy_id, seed=101, days=3).summary
    assert summary["policy_id"] == policy_id
    assert summary["total_tco_v3_hard"] == summary["total_tco_v3"]
    assert summary["total_tco_v4_soft_congestion"] >= summary["total_tco_v2"]
    for key in GUARD_METRIC_KEYS:
        assert key in summary


def test_c5_55_h5_records_guard_metrics(config):
    summary = run_policy_simulation(config, "H5", seed=101, days=5).summary
    assert summary["guard_skip_count"] >= 0
    assert summary["fallback_to_h4_count"] >= 0
    assert summary["route_guard_violation_count"] >= 0
    assert summary["shovel_guard_violation_count"] >= 0
    assert summary["crusher_guard_violation_count"] >= 0
    assert summary["risk_guard_violation_count"] >= 0
