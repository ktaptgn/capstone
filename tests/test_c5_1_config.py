from pathlib import Path

from mine_env.config_c5_1 import load_c5_1_config


ROOT = Path(__file__).resolve().parents[1]


def test_c5_1_config_loads_and_keeps_deferred_features_disabled():
    config = load_c5_1_config(ROOT / "configs" / "c5_1.yaml")

    assert config["simulation"]["version"] == "C5.1"
    assert config["mine"]["use_drop_zone"] is False
    assert config["policies"]["rl_enabled"] is False
    assert config["policies"]["enabled"] == ["H0", "H1", "H2", "H3", "H4", "H_TIME"]
    assert "event_costs" in config["cost_model"]
    assert "actions" in config["maintenance"]
    assert config["outputs"]["log_dir"] == "outputs/c5_1/logs"
