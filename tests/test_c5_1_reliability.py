import copy
import random
from pathlib import Path

import pytest

from mine_env.config_c5_1 import load_c5_1_config
from mine_env.reliability_c5_1 import C5_1ReliabilityModel
from mine_env.simulator_c5_1 import run_policy_simulation


ROOT = Path(__file__).resolve().parents[1]


def _config(enabled: bool) -> dict:
    config = copy.deepcopy(load_c5_1_config(ROOT / "configs" / "c5_1.yaml"))
    config.setdefault("reliability", {})
    config["reliability"]["enabled"] = enabled
    return config


def _summary(enabled: bool, policy: str = "H1", days: int = 120, seed: int = 1) -> dict:
    return run_policy_simulation(
        _config(enabled), policy_id=policy, seed=seed, days=days
    ).summary


class _FakeRng:
    """Deterministic RNG stub so breakdown draws can be forced on/off in tests."""

    def __init__(self, value: float):
        self._value = value

    def random(self) -> float:
        return self._value


# --- model unit behaviour ----------------------------------------------------------

def test_reliability_disabled_is_a_noop_passthrough():
    model = C5_1ReliabilityModel(_config(False))
    assert model.enabled is False
    assert model.standby_recovery(0.002) == 0.002  # original free recovery preserved
    assert model.breakdown_probability(0.0, 0.0) == 0.0
    assert model.maybe_breakdown({"truck_hi": 0.0, "tire_hi": 0.0}, random.Random(0)) is None


def test_reliability_enabled_disables_free_standby_self_heal():
    model = C5_1ReliabilityModel(_config(True))
    # standby_self_heal defaults to false -> parking no longer restores health for free.
    assert model.standby_recovery(0.002) == 0.0


def test_breakdown_probability_ramps_below_threshold():
    model = C5_1ReliabilityModel(_config(True))
    assert model.breakdown_probability(0.9, 0.9) == 0.0  # both components healthy
    half = model.breakdown_probability(0.225, 0.9)  # half-way below truck threshold (0.45)
    assert model.prob_at_zero / 2 == pytest.approx(half, abs=1e-9)
    assert model.breakdown_probability(0.0, 0.9) == pytest.approx(model.prob_at_zero)


def test_breakdown_repair_is_partial_not_a_free_full_pm():
    model = C5_1ReliabilityModel(_config(True))
    truck = {"truck_hi": 0.05, "tire_hi": 0.05}

    event = model.maybe_breakdown(truck, _FakeRng(0.0))  # forces a failure
    assert event is not None
    assert event.restored_truck_hi == pytest.approx(model.repair_restore_hi)
    assert event.restored_tire_hi == pytest.approx(model.repair_restore_hi)
    assert event.restored_truck_hi < 1.0  # C1 fix: breakdown is not a free full-health PM
    assert event.downtime_hours == model.downtime_hours

    assert model.maybe_breakdown(truck, _FakeRng(0.99)) is None  # draw above prob -> no fire


# --- simulation-level invariants ---------------------------------------------------

def test_disabled_run_reproduces_original_four_component_cost():
    summary = _summary(False, policy="H1", days=120)
    assert summary["failure_count"] == 0
    assert summary["breakdown_cost"] == 0.0
    parts = (
        summary["pm_cost"]
        + summary["downtime_cost"]
        + summary["degradation_cost"]
        + summary["unmet_demand_cost"]
    )
    assert parts == pytest.approx(summary["total_cost"], abs=1e-4)


def test_breakdown_plumbing_flows_into_costs_and_summary():
    # The C5.1 heuristics emergently maintain (min HI ~0.62 over a full year), so they never
    # reach the operating floor and never break down -- which is the honest result. To validate
    # the breakdown -> cost -> summary wiring deterministically, force every loaded dispatch to
    # fail via an out-of-range threshold and a probability that clamps to 1.0.
    config = _config(True)
    config["reliability"]["breakdown_truck_hi_threshold"] = 2.0
    config["reliability"]["breakdown_tire_hi_threshold"] = 2.0
    config["reliability"]["breakdown_prob_at_zero"] = 10.0  # min(.,1.0) -> always fires

    summary = run_policy_simulation(config, policy_id="H0", seed=1, days=20).summary

    assert summary["failure_count"] > 0
    assert summary["breakdown_cost"] == pytest.approx(summary["failure_count"] * 6.5)
    parts = (
        summary["pm_cost"]
        + summary["downtime_cost"]
        + summary["degradation_cost"]
        + summary["unmet_demand_cost"]
        + summary["breakdown_cost"]
    )
    assert parts == pytest.approx(summary["total_cost"], abs=1e-4)


def test_state_aware_heuristics_avoid_breakdowns():
    # State-aware policies (PM driven by per-truck HI / risk) keep every truck above the
    # operating floor, so the breakdown lever stays dormant for them -> 0 failures.
    for policy in ("H1", "H2", "H3"):
        summary = _summary(True, policy=policy, days=200)
        assert summary["failure_count"] == 0


def test_blind_periodic_pm_policies_incur_breakdowns():
    # Calendar PM (H0) and pure operating-hours PM (H_TIME) ignore per-truck HI, so some
    # trucks degrade past the floor between scheduled slots and fail. This is the C3 fix
    # doing its job: health now has a consequence, so blind periodic PM is penalised while
    # state-aware PM is rewarded.
    for policy in ("H0", "H_TIME"):
        summary = _summary(True, policy=policy, days=200)
        assert summary["failure_count"] > 0


def test_summary_exposes_cost_decomposition_columns():
    summary = _summary(True, policy="H3", days=30)
    for key in (
        "downtime_cost",
        "degradation_cost",
        "unmet_demand_cost",
        "breakdown_cost",
        "failure_count",
        "pm_count",
        "total_downtime_hours",
    ):
        assert key in summary


def test_runs_are_deterministic_per_seed():
    first = _summary(True, policy="H1", days=90, seed=2)
    second = _summary(True, policy="H1", days=90, seed=2)
    assert first == second
