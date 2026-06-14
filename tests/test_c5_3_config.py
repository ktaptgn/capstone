from __future__ import annotations

import pytest

from mine_env.config_c5_3 import load_config
from tests.c5_3_helpers import CONFIG_PATH


def test_default_regime_is_heterogeneous_condition():
    cfg = load_config(CONFIG_PATH)
    assert cfg["active_regime"] == "heterogeneous_condition"


def test_fleet_and_routes_match_spec():
    cfg = load_config(CONFIG_PATH)
    assert cfg["mine"]["truck_count"] == 25
    assert set(cfg["routes"]) == {"A", "B", "C"}
    # H_TIME is excluded from the dispatch-only roster
    assert cfg["policies"]["enabled"] == ["H0", "H1", "H2", "H3", "H4"]


def test_heterogeneous_condition_overrides_cv_noise_and_multipliers():
    cfg = load_config(CONFIG_PATH, regime="heterogeneous_condition")
    rel = cfg["reliability"]
    assert rel["frailty"]["cv"] == 0.50          # regime overrides base 0.30
    assert rel["condition_observation"]["noise_std"] == 0.03
    assert rel["regime"]["wear_multiplier"] == 1.2
    assert rel["regime"]["hazard_multiplier"] == 1.3
    assert rel["regime"]["cm_cost_multiplier"] == 1.2
    assert rel["regime"]["downtime_multiplier"] == 1.2


def test_high_stress_regime_raises_wear_and_hazard():
    cfg = load_config(CONFIG_PATH, regime="high_stress")
    assert cfg["reliability"]["regime"]["wear_multiplier"] == 1.5
    assert cfg["reliability"]["regime"]["hazard_multiplier"] == 1.8
    assert cfg["reliability"]["frailty"]["cv"] == 0.30


def test_high_demand_regime_scales_daily_demand():
    base = load_config(CONFIG_PATH, regime="high_stress")["demand"]["daily_demand_loads"]
    high = load_config(CONFIG_PATH, regime="high_demand_high_stress")["demand"]["daily_demand_loads"]
    assert high == pytest.approx(round(base * 1.15))


def test_regime_application_is_idempotent():
    # demand scaling reads a stored base, so re-applying must not compound
    from mine_env.config_c5_3 import apply_regime

    once = load_config(CONFIG_PATH, regime="high_demand_high_stress")
    twice = apply_regime(once, "high_demand_high_stress")
    assert twice["demand"]["daily_demand_loads"] == once["demand"]["daily_demand_loads"]
