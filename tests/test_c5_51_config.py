from __future__ import annotations

import pytest

from mine_env.config_c5_51 import load_config
from tests.c5_51_helpers import CONFIG_PATH

EXPECTED_ROUTES = {"R_A1", "R_A2", "R_B1", "R_B2", "R_C1", "R_C2"}


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_c5_51_config_loads(config):
    assert config["simulation"]["version"] == "C5.51"
    assert config["active_regime"] == "heterogeneous_condition"


def test_facility_layout_is_inherited_from_c5_5(config):
    mine = config["mine"]
    facilities = config["facilities"]
    assert mine["truck_count"] == 25
    assert mine["operating_truck_count"] == 20
    assert mine["standby_truck_count"] == 5
    assert len(facilities["shovels"]) == 3
    assert len(facilities["crushers"]) == 2
    assert mine["pm_bay_facility_count"] == 1
    assert mine["pm_service_capacity"] == 2


def test_route_table_has_exactly_six_facility_routes(config):
    assert set(config["routes"]) == EXPECTED_ROUTES


def test_every_route_maps_to_valid_shovel_and_crusher(config):
    shovels = set(config["facilities"]["shovels"])
    crushers = set(config["facilities"]["crushers"])
    for route in config["routes"].values():
        assert route["shovel_id"] in shovels
        assert route["crusher_id"] in crushers
        assert route["capacity_loads_per_day"] > 0
        assert route["cycle_time_factor"] > 0
