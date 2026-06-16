from __future__ import annotations

import importlib.util
import math
import sys
import hashlib
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1] / "transfer_tests" / "rsw_c5_4_level2"


def _load(name):
    path = ROOT / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def sim():
    sys.path.insert(0, str(ROOT))
    return _load("rsw_c5_4_mini_sim")


def test_all_policies_run_and_report_required_fields(sim):
    config = sim.load_config()
    for policy in config["policies"]["enabled"]:
        result = sim.run_policy_episode(config, policy, seed=101, days=2, record_events=True)
        assert result.summary["policy"] == policy
        assert result.summary["max_pm_slots_used"] <= config["simulation"]["maintenance_slots"]
        assert result.event_log
        assert result.summary["failures"] == len(result.failure_log)


def test_policy_episode_is_reproducible(sim):
    config = sim.load_config(regime="high_stress")
    left = sim.run_policy_episode(config, "H1", seed=102, days=3, record_events=True)
    right = sim.run_policy_episode(config, "H1", seed=102, days=3, record_events=True)
    assert left.summary == right.summary
    assert left.event_log == right.event_log
    assert left.failure_log == right.failure_log


def test_cost_decomposition_and_full_service_accounting(sim):
    config = sim.load_config()
    for policy in ("H0", "H_TIME"):
        result = sim.run_policy_episode(config, policy, seed=101, days=5)
        cost_sum = sum(
            result.summary[f"{name}_cost"] for name in config["cost"]["tco_components"]
        )
        assert math.isclose(cost_sum, result.summary["TCO"], abs_tol=1e-5)
        assert result.summary["pm_components"] == result.summary["pm_visits"] * 3


def test_state_aware_policy_can_target_components(sim):
    config = sim.load_config(regime="high_stress")
    targeted = False
    for policy in ("H1", "H2", "H3", "H4"):
        result = sim.run_policy_episode(config, policy, seed=101, days=10)
        if result.summary["pm_components"] < result.summary["pm_visits"] * 3:
            targeted = True
    assert targeted


def test_aggregate_summary_has_required_kpis(sim):
    config = sim.load_config()
    rows = [
        sim.run_policy_episode(config, policy, seed=seed, days=1).summary
        for policy in ("H0", "H1")
        for seed in (101, 102)
    ]
    summary = sim.aggregate_policy_summaries(rows)
    required = {
        "scenario", "regime", "policy", "seed_count", "days", "TCO_mean", "TCO_std", "PMvisits_mean",
        "PMcomps_mean", "CM_mean", "failure_mean", "defect_mean", "fulfillment_mean",
        "completed_welds_mean", "unmet_welds_mean", "endHI_mean", "downtime_hours_mean",
        "pm_cost_mean", "cm_cost_mean", "downtime_cost_mean", "degradation_cost_mean",
        "unmet_demand_cost_mean", "defect_cost_mean",
        "pm_tip_share", "pm_cooling_share", "pm_actuator_share", "cm_tip_share",
        "cm_cooling_share", "cm_actuator_share", "route_A_share", "route_B_share",
        "route_C_share",
    }
    assert len(summary) == 2
    assert required.issubset(summary[0])


def test_base_default_config_is_unchanged(sim):
    config = sim.load_config()
    assert config["simulation"]["campaign_days"] == 30
    assert config["simulation"]["seeds"] == list(range(101, 111))
    assert config["demand"]["family_daily_targets"] == {"A": 70, "B": 70, "C": 70}
    assert config["default_regime"] == "heterogeneous_condition"
    assert list(config["regimes"]) == [
        "heterogeneous_condition",
        "high_stress",
        "high_demand_high_stress",
    ]
    assert config["policies"]["enabled"] == ["H0", "H_TIME", "H1", "H2", "H3", "H4"]


def test_scenario_contracts_use_distinct_outputs(sim):
    config = sim.load_config()
    base = sim.build_scenario_contract(config)
    stress = sim.build_scenario_contract(config, "demand_pressure_stress")
    horizon = sim.build_scenario_contract(config, "horizon_sanity_90")
    assert base["outputs"]["directory"] == "outputs"
    assert stress["outputs"]["directory"] == "outputs/stress"
    assert horizon["outputs"]["directory"] == "outputs/horizon_90"
    assert len({base["outputs"]["directory"], stress["outputs"]["directory"], horizon["outputs"]["directory"]}) == 3
    assert sum(stress["family_daily_targets"].values()) > sum(base["family_daily_targets"].values())
    assert horizon["days"] == 90


def test_demand_stress_outputs_do_not_overwrite_base(sim, monkeypatch):
    config = sim.load_config()
    base_files = [
        ROOT / "outputs" / "rsw_c5_4_policy_summary.csv",
        ROOT / "outputs" / "rsw_c5_4_event_log.csv",
        ROOT / "outputs" / "rsw_c5_4_failure_log.csv",
    ]
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in base_files}
    written_paths = []
    monkeypatch.setattr(sim, "write_csv", lambda path, rows: written_paths.append(path))
    output_spec = {
        "directory": "outputs",
        "policy_summary_csv": "sanity_summary.csv",
        "event_log_csv": "sanity_events.csv",
        "failure_log_csv": "sanity_failures.csv",
    }
    sim.run_policy_sweep(
        config,
        policies=["H1"],
        seeds=[101],
        regimes=["high_demand_high_stress"],
        days=1,
        scenario="demand_pressure_stress",
        output_spec=output_spec,
        family_daily_targets={"A": 500, "B": 500, "C": 500},
    )

    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in base_files}
    assert before == after
    assert {path.name for path in written_paths} == {
        "sanity_summary.csv",
        "sanity_events.csv",
        "sanity_failures.csv",
    }
    assert not set(written_paths).intersection(base_files)


def test_demand_stress_has_higher_daily_target_than_base(sim):
    config = sim.load_config()
    base = sim.build_scenario_contract(config)
    stress = sim.build_scenario_contract(config, "demand_pressure_stress")
    assert sum(stress["family_daily_targets"].values()) > sum(base["family_daily_targets"].values())


def test_horizon_sanity_uses_90_days(sim):
    contract = sim.build_scenario_contract(sim.load_config(), "horizon_sanity_90")
    assert contract["days"] == 90


def test_configured_sanity_sweeps_use_scenario_contracts(sim, monkeypatch):
    calls = []

    def capture_sweep(base_config, **kwargs):
        calls.append(kwargs)
        return []

    monkeypatch.setattr(sim, "run_policy_sweep", capture_sweep)
    config = sim.load_config()
    sim.run_configured_scenario(config, "demand_pressure_stress")
    sim.run_configured_scenario(config, "horizon_sanity_90")

    stress, horizon = calls
    assert stress["scenario"] == "demand_pressure_stress"
    assert stress["days"] == 30
    assert stress["regimes"] == ["high_demand_high_stress"]
    assert stress["family_daily_targets"] == {"A": 500, "B": 500, "C": 500}
    assert stress["output_spec"]["directory"] == "outputs/stress"
    assert horizon["scenario"] == "horizon_sanity_90"
    assert horizon["days"] == 90
    assert horizon["regimes"] == list(config["regimes"])
    assert horizon["family_daily_targets"] == config["demand"]["family_daily_targets"]
    assert horizon["output_spec"]["directory"] == "outputs/horizon_90"
    assert stress["seeds"] == horizon["seeds"] == config["simulation"]["seeds"]
    assert stress["policies"] == horizon["policies"] == config["policies"]["enabled"]


def test_cli_sanity_flags_select_configured_contract(sim, monkeypatch):
    selected = []

    def capture_scenario(base_config, scenario):
        contract = sim.build_scenario_contract(base_config, scenario)
        selected.append(scenario)
        return [], contract

    monkeypatch.setattr(sim, "run_configured_scenario", capture_scenario)
    for flag in ("--demand-stress", "--horizon-sanity-90"):
        monkeypatch.setattr(sys, "argv", ["rsw_c5_4_mini_sim.py", flag])
        assert sim.main() == 0

    assert selected == ["demand_pressure_stress", "horizon_sanity_90"]


def test_cli_sanity_flags_reject_execution_overrides(sim, monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["rsw_c5_4_mini_sim.py", "--demand-stress", "--days", "1"],
    )
    with pytest.raises(SystemExit) as error:
        sim.main()
    assert error.value.code == 2


def test_sanity_outputs_have_required_columns(sim):
    config = sim.load_config(regime="high_demand_high_stress")
    stress_row = sim.run_policy_episode(
        config,
        "H1",
        seed=101,
        days=1,
        scenario="demand_pressure_stress",
    ).summary
    horizon_row = {**stress_row, "scenario": "horizon_sanity_90", "days": 90}
    rows = [stress_row, horizon_row]
    summaries = {row["scenario"]: row for row in sim.aggregate_policy_summaries(rows)}
    stress_required = {
        "scenario", "regime", "policy", "seed_count", "TCO_mean", "TCO_std",
        "PMvisits_mean", "CM_mean", "failure_mean", "defect_mean", "completed_welds_mean",
        "unmet_welds_mean", "fulfillment_mean", "downtime_hours_mean", "pm_cost_mean",
        "cm_cost_mean", "downtime_cost_mean", "degradation_cost_mean",
        "unmet_demand_cost_mean", "defect_cost_mean", "endHI_mean",
    }
    horizon_required = {
        "scenario", "regime", "policy", "seed_count", "days", "TCO_mean", "TCO_std",
        "PMvisits_mean", "CM_mean", "failure_mean", "defect_mean", "completed_welds_mean",
        "unmet_welds_mean", "fulfillment_mean", "downtime_hours_mean", "endHI_mean",
        "pm_tip_share", "pm_cooling_share", "pm_actuator_share", "cm_tip_share",
        "cm_cooling_share", "cm_actuator_share",
    }
    assert stress_required.issubset(summaries["demand_pressure_stress"])
    assert horizon_required.issubset(summaries["horizon_sanity_90"])


def test_sanity_reports_include_not_real_factory_validation():
    report_paths = [
        ROOT / "outputs" / "rsw_c5_4_sanity_improvement_report.md",
        ROOT / "outputs" / "stress" / "rsw_c5_4_demand_stress_report.md",
        ROOT / "outputs" / "horizon_90" / "rsw_c5_4_90day_report.md",
    ]
    for path in report_paths:
        text = path.read_text(encoding="utf-8")
        assert "not real factory validation" in text
        assert "not tuned to reproduce the C5.4 mining ranking" in text

    integrated = report_paths[0].read_text(encoding="utf-8")
    assert "The original 30-day base result is preserved." in integrated
    assert "한국어 발표 요약" in integrated


def test_sanity_plots_exist_and_are_nonempty():
    plot_paths = [
        ROOT / "outputs" / "stress" / "rsw_c5_4_demand_stress_plot.png",
        ROOT / "outputs" / "horizon_90" / "rsw_c5_4_90day_plot.png",
    ]
    for path in plot_paths:
        assert path.exists()
        assert path.stat().st_size > 10_000
