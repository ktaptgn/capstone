from __future__ import annotations

import pytest

from mine_env.config_c5_55 import CONFIG_PATH, load_config


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_c5_55_config_loads(config):
    assert config["simulation"]["version"] == "C5.55"
    assert config["active_regime"] == "heterogeneous_condition"
    assert config["outputs"]["summary_dir"] == "outputs/c5_55/summary"
    assert config["outputs"]["analysis_dir"] == "outputs/c5_55/analysis"


def test_c5_55_inherits_c5_54_structure(config):
    assert set(config["routes"]) == {"R_A1", "R_A2", "R_B1", "R_B2", "R_C1", "R_C2"}
    assert "soft_congestion" in config
    assert "h4_balanced_rr_guard" in config
    assert config["mine"]["truck_count"] == 25
    assert config["mine"]["pm_service_capacity"] == 2


def test_c5_55_h5_freeze_settings(config):
    h5 = config["h5_policy"]
    assert h5["official_policy"] == "H5"
    assert h5["source_policy"] == "H4_BALANCED_RR_GUARD"
    assert h5["soft_utilization_threshold"] == pytest.approx(0.90)
    assert h5["risk_guard_level"] == "base"
    assert h5["aggressive_soft_utilization_threshold"] == pytest.approx(0.85)
    assert h5["aggressive_risk_guard_level"] == "strict"
    assert config["policies"]["enabled"] == [
        "H0",
        "H_TIME",
        "H1",
        "H2",
        "H3",
        "H4",
        "H5",
        "BALANCED_RR_H4_PM",
        "H5_AGGRESSIVE",
    ]
