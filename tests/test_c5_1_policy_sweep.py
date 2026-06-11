import json
from pathlib import Path

from mine_env.config_c5_1 import load_c5_1_config
from mine_env.simulator_c5_1 import run_policy_sweep


ROOT = Path(__file__).resolve().parents[1]


def test_policy_sweep_generates_logs_and_kpi_summaries():
    config = load_c5_1_config(ROOT / "configs" / "c5_1.yaml")
    log_dir = ROOT / "outputs" / "c5_1" / "logs" / "pytest_sweep"
    summary_dir = ROOT / "outputs" / "c5_1" / "summary" / "pytest_sweep"

    rows = run_policy_sweep(
        config,
        policies=["H0", "H1", "H2", "H3", "H4"],
        seeds=[1],
        log_dir=log_dir,
        summary_dir=summary_dir,
        days=2,
    )

    assert len(rows) == 5
    assert {row["policy_id"] for row in rows} == {"H0", "H1", "H2", "H3", "H4"}
    assert len({row["total_demand"] for row in rows}) == 1
    assert all(
        {"total_cost", "pm_cost", "unmet_demand", "demand_fulfillment_rate"}
        <= set(row)
        for row in rows
    )

    assert (summary_dir / "policy_comparison.csv").exists()
    summary_json = summary_dir / "policy_comparison.json"
    assert summary_json.exists()
    assert len(json.loads(summary_json.read_text(encoding="utf-8"))) == 5

    for policy_id in ["H0", "H1", "H2", "H3", "H4"]:
        log_file = log_dir / f"{policy_id}_seed_1.json"
        assert log_file.exists()
        payload = json.loads(log_file.read_text(encoding="utf-8"))
        assert payload["seed"] == 1
        assert payload["demand_scenario"] == rows[0].get("demand_scenario", payload["demand_scenario"])
        assert payload["records"]


def test_policy_sweep_can_compare_time_periodic_pm_against_h0_h4():
    config = load_c5_1_config(ROOT / "configs" / "c5_1.yaml")
    log_dir = ROOT / "outputs" / "c5_1" / "logs" / "pytest_time_pm_sweep"
    summary_dir = ROOT / "outputs" / "c5_1" / "summary" / "pytest_time_pm_sweep"

    rows = run_policy_sweep(
        config,
        policies=["H_TIME", "H0", "H1", "H2", "H3", "H4"],
        seeds=[1],
        log_dir=log_dir,
        summary_dir=summary_dir,
        days=2,
    )

    assert len(rows) == 6
    assert {row["policy_id"] for row in rows} == {
        "H_TIME",
        "H0",
        "H1",
        "H2",
        "H3",
        "H4",
    }
    assert len({row["total_demand"] for row in rows}) == 1

    payload = json.loads((log_dir / "H_TIME_seed_1.json").read_text(encoding="utf-8"))
    assert payload["records"]
    assert {
        record["reason_code"] for record in payload["records"]
    } <= {
        "PM_DUE_TIME_PM_DUE",
        "PM_DUE_TIME_DISPATCH",
        "PM_DUE_TIME_DEMAND_MET",
        "PM_BAY_CAPACITY_FULL",
    }


def test_h0_is_the_pure_periodic_pm_baseline_in_the_default_sweep():
    config = load_c5_1_config(ROOT / "configs" / "c5_1.yaml")
    log_dir = ROOT / "outputs" / "c5_1" / "logs" / "pytest_periodic_pm_sweep"
    summary_dir = ROOT / "outputs" / "c5_1" / "summary" / "pytest_periodic_pm_sweep"

    rows = run_policy_sweep(
        config,
        policies=["H_TIME", "H0", "H1", "H2", "H3", "H4"],
        seeds=[1],
        log_dir=log_dir,
        summary_dir=summary_dir,
        days=3,
    )

    assert len(rows) == 6
    assert {row["policy_id"] for row in rows} == {
        "H_TIME",
        "H0",
        "H1",
        "H2",
        "H3",
        "H4",
    }
    assert len({row["total_demand"] for row in rows}) == 1

    payload = json.loads(
        (log_dir / "H0_seed_1.json").read_text(encoding="utf-8")
    )
    assert payload["records"]
    assert "BASELINE_PERIODIC_PM_SLOT" in {
        record["reason_code"] for record in payload["records"]
    }
