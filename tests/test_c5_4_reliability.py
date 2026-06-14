from __future__ import annotations

import copy

import numpy as np
import pytest

from mine_env.config_c5_4 import load_config
from mine_env.reliability_c5_4 import COMPONENTS, C5_4ReliabilityModel
from mine_env.simulator_c5_4 import run_policy_simulation
from tests.c5_4_helpers import CONFIG_PATH, make_truck


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


# --- sensor-noise boundary (POMDP) -----------------------------------------------------------
def test_observed_hi_is_clipped_to_unit_range(config):
    """Even with heavy noise, observed HI never leaves [0, 1] (the clip boundary holds)."""
    cfg = copy.deepcopy(config)
    cfg["reliability"]["condition_observation"]["noise_std"] = 0.5  # extreme noise
    rel = C5_4ReliabilityModel(cfg)
    rng = np.random.default_rng(0)
    edges = [make_truck("T_HI", tire=1.0, engine=1.0, brake=1.0),
             make_truck("T_LO", tire=0.0, engine=0.0, brake=0.0)]
    lo, hi = 1.0, 0.0
    for _ in range(2000):
        for truck in edges:
            obs = rel.observe(truck, rng)
            lo = min(lo, min(obs.values()))
            hi = max(hi, max(obs.values()))
    assert lo >= 0.0 and hi <= 1.0
    assert lo < 0.5 and hi > 0.5  # noise actually moved the observation off the edges


def test_noise_disabled_gives_exact_observation(config):
    cfg = copy.deepcopy(config)
    cfg["reliability"]["condition_observation"]["noise_enabled"] = False
    rel = C5_4ReliabilityModel(cfg)
    truck = make_truck("T01", tire=0.42, engine=0.73, brake=0.55)
    obs = rel.observe(truck, np.random.default_rng(1))
    for component in COMPONENTS:
        assert obs[component] == pytest.approx(float(truck[f"{component}_hi"]))


# --- failure hazard shape --------------------------------------------------------------------
def test_failure_probability_zero_above_threshold_and_rises_below(config):
    rel = C5_4ReliabilityModel(config)
    th = rel.threshold_hi
    assert rel.failure_probability("tire", th + 0.01) == 0.0
    assert rel.failure_probability("tire", th + 0.5) == 0.0
    p_mid = rel.failure_probability("tire", th * 0.5)
    p_low = rel.failure_probability("tire", th * 0.1)
    assert 0.0 < p_mid <= 1.0
    assert p_low >= p_mid                    # hazard rises as HI falls
    assert rel.failure_probability("tire", 0.0) == 1.0


def test_frailty_cv_controls_heterogeneity(config):
    rel = C5_4ReliabilityModel(config)  # heterogeneous_condition -> cv 0.50
    rng = np.random.default_rng(7)
    draws = [rel.draw_frailty(rng)["tire"] for _ in range(2000)]
    assert np.std(draws) > 0.1                # cv>0 -> real spread
    cfg0 = copy.deepcopy(config)
    cfg0["reliability"]["frailty"]["enabled"] = False
    rel0 = C5_4ReliabilityModel(cfg0)
    assert all(rel0.draw_frailty(rng)[c] == 1.0 for c in COMPONENTS)


def test_truck_hi_is_min_over_components(config):
    rel = C5_4ReliabilityModel(config)
    truck = make_truck("T01", tire=0.8, engine=0.3, brake=0.6)
    assert rel.truck_hi(truck) == pytest.approx(0.3)


# --- Tier-1 per-component failure logging ----------------------------------------------------
def test_per_component_cm_counts_sum_to_total():
    # a stress regime so the failure/CM path actually activates
    cfg = load_config(CONFIG_PATH, regime="high_stress")
    s = run_policy_simulation(cfg, "H0", seed=108, days=120).summary
    assert s["cm_tire"] + s["cm_engine"] + s["cm_brake"] == s["cm_count"]
    assert s["cm_count"] == s["failure_count"]  # one CM per failed component


def test_record_events_log_matches_failure_count():
    cfg = load_config(CONFIG_PATH, regime="high_stress")
    result = run_policy_simulation(cfg, "H0", seed=108, days=120, record_events=True)
    assert len(result.failure_log) == result.summary["failure_count"]
    if result.failure_log:
        ev = result.failure_log[0]
        assert set(ev) == {"day", "hour", "step", "truck_id", "component", "truck_hi_after", "route"}
        assert ev["component"] in COMPONENTS
