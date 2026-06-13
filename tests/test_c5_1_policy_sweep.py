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
