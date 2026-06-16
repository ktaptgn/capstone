from __future__ import annotations

import pytest

from mine_env.config_c5_53 import CONFIG_PATH, load_config
from mine_env.policies_c5_53 import ROUTES
from mine_env.simulator_c5_53 import route_cycle_time_components, run_policy_simulation


class SingleRoutePolicy:
    def reset(self):
        pass

    def decide(self, state):
        ranked = ["R_C2", "R_C1", "R_B2", "R_B1", "R_A2", "R_A1"]
        return {
            "pm": [],
            "dispatch": [(truck["truck_id"], ranked) for truck in state["dispatch_state"]["dispatch_trucks"]],
        }


class BalancedRoutePolicy:
    def __init__(self):
        self.index = 0

    def reset(self):
        self.index = 0

    def decide(self, state):
        dispatch = []
        for truck in state["dispatch_state"]["dispatch_trucks"]:
            head = self.index % len(ROUTES)
            ranked = list(ROUTES[head:]) + list(ROUTES[:head])
            dispatch.append((truck["truck_id"], ranked))
            self.index += 1
        return {"pm": [], "dispatch": dispatch}


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_single_route_saturation_creates_delay_and_congestion_cost(config):
    result = run_policy_simulation(
        config,
        "SINGLE_R_C2",
        seed=101,
        days=2,
        policy=SingleRoutePolicy(),
        congestion_alpha=1.0,
        congestion_beta=2.0,
        record_events=True,
    )
    summary = result.summary
    assert summary["route_r_c2_attempts"] > config["routes"]["R_C2"]["capacity_loads_per_day"]
    assert summary["congestion_delay_hours_total"] > 0
    assert summary["congestion_cost"] > 0
    assert summary["avg_realized_cycle_time_hours"] > summary["avg_base_cycle_time_hours"]
    assert any(float(event["route_utilization_after"]) > 1.0 for event in result.dispatch_events)


def test_balanced_assignment_reduces_route_concentration_and_delay(config):
    single = run_policy_simulation(
        config,
        "SINGLE_R_C2",
        seed=102,
        days=2,
        policy=SingleRoutePolicy(),
        congestion_alpha=1.0,
        congestion_beta=2.0,
    ).summary
    balanced = run_policy_simulation(
        config,
        "BALANCED",
        seed=102,
        days=2,
        policy=BalancedRoutePolicy(),
        congestion_alpha=1.0,
        congestion_beta=2.0,
    ).summary
    assert balanced["route_hhi"] < single["route_hhi"]
    assert balanced["max_route_share"] < single["max_route_share"]
    assert balanced["congestion_delay_hours_total"] < single["congestion_delay_hours_total"]


def test_h1_h2_c_route_concentration_is_logged(config):
    h2 = run_policy_simulation(
        config, "H2_original", seed=101, days=5, congestion_alpha=1.0, congestion_beta=2.0
    ).summary
    h4 = run_policy_simulation(
        config, "H4", seed=101, days=5, congestion_alpha=1.0, congestion_beta=2.0
    ).summary
    h2_c_attempts = h2["route_r_c1_attempts"] + h2["route_r_c2_attempts"]
    h4_c_attempts = h4["route_r_c1_attempts"] + h4["route_r_c2_attempts"]
    assert h2_c_attempts > 0
    assert h4_c_attempts > 0
    assert h2["route_hhi"] >= 0
    assert h4["route_hhi"] >= 0


def test_proxy_base_cycle_time_is_used_in_realized_cycle_time(config):
    result = run_policy_simulation(
        config,
        "SINGLE_R_C2",
        seed=103,
        days=1,
        policy=SingleRoutePolicy(),
        congestion_alpha=0.0,
        congestion_beta=2.0,
        record_events=True,
    )
    event = next(row for row in result.dispatch_events if row["assigned_route"] == "R_C2")
    expected = route_cycle_time_components(config, "R_C2")["base_cycle_time_min"]
    assert float(event["base_cycle_time_min"]) == pytest.approx(expected, rel=1e-6)
    assert float(event["realized_cycle_time_min"]) == pytest.approx(expected, rel=1e-6)
    assert result.summary["avg_base_cycle_time_min"] > 0


def test_soft_threshold_metrics_preserve_hard_tco_v3(config):
    summary = run_policy_simulation(
        config,
        "H4",
        seed=101,
        days=3,
        congestion_alpha=1.0,
        congestion_beta=2.0,
    ).summary
    assert summary["total_tco_v3_hard"] == summary["total_tco_v3"]
    assert summary["congestion_delay_hours_hard"] == summary["congestion_delay_hours_total"]
    assert summary["congestion_cost_hard"] == summary["congestion_cost"]
    assert summary["total_tco_v4_soft_congestion"] >= summary["total_tco_v2"]
    assert summary["congestion_delay_hours_soft"] >= summary["congestion_delay_hours_hard"]
    assert "max_route_utilization" in summary
    assert "max_shovel_utilization" in summary
    assert "max_crusher_utilization" in summary
