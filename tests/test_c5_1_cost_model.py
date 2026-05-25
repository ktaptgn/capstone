from pathlib import Path

from mine_env.config_c5_1 import load_c5_1_config
from mine_env.costs_c5_1 import C5_1CostModel
from mine_env.maintenance_c5_1 import C5_1MaintenanceModel


ROOT = Path(__file__).resolve().parents[1]


def test_c5_1_cost_model_uses_configured_event_costs():
    config = load_c5_1_config(ROOT / "configs" / "c5_1.yaml")
    cost_model = C5_1CostModel(config)

    assert cost_model.pm_cost("PM_TIRE") == 1.0
    assert cost_model.pm_cost("PM_VEHICLE") == 1.5

    step_cost = cost_model.step_cost(
        "PM_TIRE", downtime_hours=2, hi_loss=0.5, unmet_loads=3
    )

    assert step_cost.pm_cost == 1.0
    assert step_cost.downtime_cost == 1.0
    assert step_cost.degradation_cost == 0.1
    assert step_cost.unmet_demand_cost == 6.0
    assert step_cost.total == 8.1


def test_maintenance_alias_maps_policy_vehicle_pm_to_configured_action():
    config = load_c5_1_config(ROOT / "configs" / "c5_1.yaml")
    maintenance = C5_1MaintenanceModel(config)

    action = maintenance.resolve_action("PM_VEHICLE")

    assert action.action_id == "PM_VEHICLE_BALANCED"
    assert action.duration_hours == 4
    assert maintenance.pm_bay_capacity == 2
