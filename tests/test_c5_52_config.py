from __future__ import annotations

import pytest

from mine_env.config_c5_52 import CONFIG_PATH, load_config


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_c5_52_config_loads(config):
    assert config["simulation"]["version"] == "C5.52"
    assert config["active_regime"] == "heterogeneous_condition"


def test_c5_52_inherits_c5_51_layout(config):
    assert config["mine"]["truck_count"] == 25
    assert config["mine"]["operating_truck_count"] == 20
    assert config["mine"]["standby_truck_count"] == 5
    assert len(config["facilities"]["shovels"]) == 3
    assert len(config["facilities"]["crushers"]) == 2
    assert config["mine"]["pm_bay_facility_count"] == 1
    assert config["mine"]["pm_service_capacity"] == 2
    assert set(config["routes"]) == {"R_A1", "R_A2", "R_B1", "R_B2", "R_C1", "R_C2"}


def test_grade_aware_objective_block(config):
    obj = config["grade_aware_objective"]
    assert obj["target_effective_grade_index"] == pytest.approx(0.80)
    assert set(obj["shortfall_cost_sensitivity"]) == {"low", "base", "high"}
    assert obj["shortfall_cost_sensitivity"]["low"] < obj["shortfall_cost_sensitivity"]["base"]
    assert obj["shortfall_cost_sensitivity"]["base"] < obj["shortfall_cost_sensitivity"]["high"]
