from __future__ import annotations

import pytest

from mine_env.config_c5_54 import CONFIG_PATH, load_config


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_c5_54_config_loads(config):
    assert config["simulation"]["version"] == "C5.54"
    assert config["active_regime"] == "heterogeneous_condition"
    assert config["outputs"]["summary_dir"] == "outputs/c5_54/summary"


def test_c5_54_inherits_c5_53_structure(config):
    assert set(config["routes"]) == {"R_A1", "R_A2", "R_B1", "R_B2", "R_C1", "R_C2"}
    assert "truck_motion" in config
    assert "soft_congestion" in config
    assert "grade_aware_objective" in config


def test_h4_balanced_rr_guard_config(config):
    guard = config["h4_balanced_rr_guard"]
    assert guard["official_candidate"] is True
    assert guard["route_order"] == ["R_A1", "R_B1", "R_C1", "R_A2", "R_B2", "R_C2"]
    assert guard["soft_utilization_threshold"] == pytest.approx(0.90)
    assert guard["risk_guard_mode"] == "h4_baseline_percentile"
    assert guard["risk_guard_level"] == "base"
    assert guard["risk_guard_levels"] == {"relaxed": 0.95, "base": 0.90, "strict": 0.75}
    assert guard["fallback_policy"] == "h4_route_score"
    assert config["policies"]["enabled"] == ["H4", "BALANCED_RR_H4_PM", "H4_BALANCED_RR_GUARD"]
