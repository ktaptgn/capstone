from __future__ import annotations

import pytest

from mine_env.config_c5_53 import CONFIG_PATH, load_config
from mine_env.simulator_c5_53 import build_route_cycle_time_table


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_c5_53_config_loads(config):
    assert config["simulation"]["version"] == "C5.53"
    assert config["active_regime"] == "heterogeneous_condition"


def test_c5_53_inherits_c5_52_layout(config):
    assert config["mine"]["truck_count"] == 25
    assert config["mine"]["operating_truck_count"] == 20
    assert config["mine"]["standby_truck_count"] == 5
    assert len(config["facilities"]["shovels"]) == 3
    assert len(config["facilities"]["crushers"]) == 2
    assert config["mine"]["pm_bay_facility_count"] == 1
    assert config["mine"]["pm_service_capacity"] == 2
    assert set(config["routes"]) == {"R_A1", "R_A2", "R_B1", "R_B2", "R_C1", "R_C2"}


def test_congestion_block(config):
    congestion = config["congestion"]
    assert congestion["enabled"] is True
    assert congestion["base_cycle_time_hours"] > 0
    assert set(congestion["congestion_cost_per_hour"]) == {"low", "base", "high"}
    assert congestion["congestion_cost_per_hour"]["low"] < congestion["congestion_cost_per_hour"]["base"]
    assert congestion["congestion_cost_per_hour"]["base"] < congestion["congestion_cost_per_hour"]["high"]


def test_soft_congestion_block(config):
    soft = config["soft_congestion"]
    assert soft["enabled"] is True
    assert soft["soft_start"] == pytest.approx(0.85)
    assert soft["alpha_soft"]["low"] < soft["alpha_soft"]["base"]
    assert soft["alpha_soft"]["base"] < soft["alpha_soft"]["high"]
    assert soft["cost_per_hour"] > 0


def test_cycle_time_proxy_blocks_load(config):
    assert config["truck_motion"]["loaded_speed_kmh"]["base"] < config["truck_motion"]["empty_speed_kmh"]["base"]
    assert set(config["route_distances"]) == set(config["routes"])
    assert set(config["route_speed_factors"]) == {"A", "B", "C"}
    assert set(config["shovel_loading_proxy"]["shovels"]) == {"A", "B", "C"}
    assert set(config["crusher_service_proxy"]["crushers"]) == {"crusher_1", "crusher_2"}


def test_route_cycle_time_sanity_order(config):
    table = {row["route_id"]: row for row in build_route_cycle_time_table(config)}
    assert table["R_C1"]["base_cycle_time_min"] < table["R_C2"]["base_cycle_time_min"]
    assert table["R_C2"]["base_cycle_time_min"] < table["R_A1"]["base_cycle_time_min"]
    assert table["R_C2"]["base_cycle_time_min"] < table["R_A2"]["base_cycle_time_min"]
    assert table["R_A2"]["base_cycle_time_min"] > table["R_A1"]["base_cycle_time_min"]
    assert table["R_B2"]["base_cycle_time_min"] > table["R_B1"]["base_cycle_time_min"]
    assert table["R_A2"]["loaded_distance_km"] > table["R_A1"]["loaded_distance_km"]
    assert table["R_B2"]["loaded_distance_km"] > table["R_B1"]["loaded_distance_km"]
    assert table["R_A2"]["crusher_service_time_min"] < table["R_A1"]["crusher_service_time_min"]
