from pathlib import Path

from mine_env.config_c5_1 import load_c5_1_config
from mine_env.logger_c5_1 import load_log_entry_schema, validate_log_entry
from mine_env.simulator_c5_1 import run_policy_simulation


ROOT = Path(__file__).resolve().parents[1]


def test_generated_log_records_match_c5_1_schema():
    config = load_c5_1_config(ROOT / "configs" / "c5_1.yaml")
    schema = load_log_entry_schema(ROOT / "schemas" / "c5_1_simulation_log.schema.json")
    result = run_policy_simulation(config, policy_id="H0", seed=1, days=1)

    assert result.records
    for entry in result.records:
        validate_log_entry(entry, schema)


def test_visualization_mvp_is_log_replay_only():
    index = (ROOT / "ui" / "simulation_visualization" / "index.html").read_text(
        encoding="utf-8"
    )
    app = (ROOT / "ui" / "simulation_visualization" / "app.js").read_text(
        encoding="utf-8"
    )

    assert "type=\"file\"" in index
    assert "records" in app
    assert "operator dashboard" not in index.lower()
    assert "work order" not in app.lower()
