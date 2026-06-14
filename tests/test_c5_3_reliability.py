from __future__ import annotations

import numpy as np
import pytest

from mine_env.config_c5_3 import load_config
from mine_env.reliability_c5_3 import COMPONENTS, C5_3ReliabilityModel
from tests.c5_3_helpers import CONFIG_PATH


@pytest.fixture(scope="module")
def model():
    return C5_3ReliabilityModel(load_config(CONFIG_PATH, regime="heterogeneous_condition"))


def test_three_components_initial_full(model):
    assert COMPONENTS == ("tire", "engine", "brake")
    assert model.initial_hi() == {"tire": 1.0, "engine": 1.0, "brake": 1.0}


def test_truck_hi_is_min_over_components(model):
    truck = {"tire_hi": 0.8, "engine_hi": 0.4, "brake_hi": 0.9}
    assert model.truck_hi(truck) == 0.4
    assert truck["truck_hi"] == 0.4


def test_frailty_gamma_mean_one_cv_matches(model):
    rng = np.random.default_rng(0)
    draws = np.array([list(model.draw_frailty(rng).values()) for _ in range(5000)])
    assert draws.mean() == pytest.approx(1.0, abs=0.03)
    # heterogeneous_condition cv = 0.50
    assert draws.std() == pytest.approx(0.50, abs=0.05)


def test_rougher_route_wears_tire_faster(model):
    cfg = load_config(CONFIG_PATH, regime="heterogeneous_condition")

    def end_tire(route_id):
        truck = {f"{c}_hi": 1.0 for c in COMPONENTS}
        truck.update({f"{c}_wear_multiplier": 1.0 for c in COMPONENTS})
        rng = np.random.default_rng(7)
        for _ in range(50):
            model.apply_route_wear(truck, cfg["routes"][route_id], rng)
        return truck["tire_hi"]

    # route B has tire_wear_multiplier 1.6 vs A's 1.0
    assert end_tire("B") < end_tire("A")


def test_hazard_zero_above_threshold_and_rises_below(model):
    assert model.failure_probability("tire", 0.50) == 0.0
    assert model.failure_probability("tire", model.threshold_hi) == 0.0
    assert model.failure_probability("tire", 0.10) > model.failure_probability("tire", 0.15) > 0.0
    assert model.failure_probability("tire", 0.0) == 1.0


def test_observation_adds_noise_and_clips(model):
    rng = np.random.default_rng(1)
    truck = {f"{c}_hi": 1.0 for c in COMPONENTS}
    seen = {model.observe(truck, rng)["tire"] for _ in range(50)}
    assert len(seen) > 1                      # noise actually applied
    assert all(0.0 <= v <= 1.0 for v in seen)  # clipped to range


def test_wear_draws_are_reproducible(model):
    cfg = load_config(CONFIG_PATH, regime="heterogeneous_condition")

    def run():
        truck = {f"{c}_hi": 1.0 for c in COMPONENTS}
        truck.update({f"{c}_wear_multiplier": 1.0 for c in COMPONENTS})
        rng = np.random.default_rng(42)
        for _ in range(30):
            model.apply_route_wear(truck, cfg["routes"]["C"], rng)
        return truck["tire_hi"], truck["engine_hi"], truck["brake_hi"]

    assert run() == run()
