from __future__ import annotations

import pytest

from mine_env.config_c5_5 import load_config
from tests.c5_5_helpers import CONFIG_PATH


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_c5_5_config_loads(config):
    assert config["simulation"]["version"] == "C5.5"
    assert config["active_regime"] == "heterogeneous_condition"


def test_facility_layout_is_correct(config):
    mine = config["mine"]
    facilities = config["facilities"]
    assert mine["truck_count"] == 25
    assert mine["operating_truck_count"] == 20
    assert mine["standby_truck_count"] == 5
    assert len(facilities["shovels"]) == 3
    assert len(facilities["crushers"]) == 2
    assert mine["pm_bay_facility_count"] == 1
    assert mine["pm_service_capacity"] == 2


def test_policy_roster_matches_c5_4_family(config):
    assert config["policies"]["enabled"] == ["H0", "H_TIME", "H1", "H2", "H3", "H4"]
