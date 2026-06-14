from __future__ import annotations

import pytest

from mine_env.config_c5_3 import load_config
from mine_env.simulator_c5_3 import run_policy_simulation
from tests.c5_3_helpers import CONFIG_PATH

DAYS = 15


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_simulation_runs_and_reports_expected_fields(config):
    summary = run_policy_simulation(config, "H2", seed=101, days=DAYS).summary
    assert summary["policy_id"] == "H2"
    assert summary["regime"] == "heterogeneous_condition"
    assert summary["days"] == DAYS
    assert 0.0 <= summary["demand_fulfillment_rate"] <= 1.0
    assert summary["pm_count"] >= 0
    assert summary["failure_count"] >= 0
    for component in ("tire", "engine", "brake"):
        assert 0.0 <= summary[f"avg_{component}_hi"] <= 1.0


def test_cost_decomposition_sums_to_total_tco(config):
    s = run_policy_simulation(config, "H4", seed=102, days=DAYS).summary
    parts = (
        s["pm_cost"] + s["cm_cost"] + s["downtime_cost"]
        + s["degradation_cost"] + s["unmet_demand_cost"]
    )
    assert parts == pytest.approx(s["total_tco"], abs=1e-2)


def test_results_are_reproducible_per_seed(config):
    first = run_policy_simulation(config, "H1", seed=101, days=DAYS).summary
    second = run_policy_simulation(config, "H1", seed=101, days=DAYS).summary
    assert first == second


def test_route_loads_account_for_completed_loads(config):
    s = run_policy_simulation(config, "H0", seed=101, days=DAYS).summary
    assert s["route_a_loads"] + s["route_b_loads"] + s["route_c_loads"] == s["completed_loads"]


def test_policies_produce_distinct_outcomes(config):
    # the recast H0-H4 must NOT collapse to identical behaviour (the whole point of the
    # route decision surface); compare on a longer horizon where PM cycling has begun
    tcos = {
        pid: run_policy_simulation(config, pid, seed=101, days=40).summary["total_tco"]
        for pid in ("H0", "H2", "H3")
    }
    assert len({round(v, 1) for v in tcos.values()}) == 3


def test_high_stress_regime_is_not_cheaper_than_baseline_regime(config):
    base = run_policy_simulation(config, "H2", seed=101, days=DAYS).summary["total_tco"]
    stressed = run_policy_simulation(
        load_config(CONFIG_PATH, regime="high_stress"), "H2", seed=101, days=DAYS
    ).summary["total_tco"]
    assert stressed >= base
