from pathlib import Path

from mine_env.config_c5_1 import load_c5_1_config
from mine_env.policies import POLICY_REGISTRY, create_policy
from mine_env.policies.base_policy import ACTION_SPACE, BasePolicy


ROOT = Path(__file__).resolve().parents[1]


def _state():
    return {
        "day": 1,
        "seed": 1,
        "daily_demand": 18,
        "completed_loads": 0,
        "queue_time": 1.0,
        "available_trucks": 2,
        "remaining_truck_ids": ["T01", "T02"],
        "next_crusher": "Crusher 1",
        "trucks": [
            {
                "truck_id": "T01",
                "truck_hi": 0.9,
                "tire_hi": 0.86,
                "pm_due_hours": 48,
                "truck_state": "STANDBY",
                "location": "Yard",
            },
            {
                "truck_id": "T02",
                "truck_hi": 0.42,
                "tire_hi": 0.82,
                "pm_due_hours": 8,
                "truck_state": "STANDBY",
                "location": "Yard",
            },
        ],
    }


def test_h0_h4_share_base_policy_decide_interface():
    config = load_c5_1_config(ROOT / "configs" / "c5_1.yaml")

    assert set(POLICY_REGISTRY) == {
        "H_TIME",
        "H0",
        "H1",
        "H2",
        "H3",
        "H4",
    }

    for policy_id in ["H_TIME", "H0", "H1", "H2", "H3", "H4"]:
        policy = create_policy(policy_id, config)
        decision = policy.decide(_state())

        assert isinstance(policy, BasePolicy)
        assert policy.policy_id == policy_id
        assert set(decision) == {
            "truck_id",
            "action",
            "destination",
            "reason_code",
            "score",
        }
        assert decision["truck_id"] in {"T01", "T02"}
        assert decision["action"] in ACTION_SPACE


def test_h_time_uses_pm_due_hours_only_for_pm_trigger():
    config = load_c5_1_config(ROOT / "configs" / "c5_1.yaml")
    policy = create_policy("H_TIME", config)
    state = _state()
    state["trucks"][0]["truck_hi"] = 0.2
    state["trucks"][0]["tire_hi"] = 0.2
    state["trucks"][0]["pm_due_hours"] = 48
    state["trucks"][1]["truck_hi"] = 0.9
    state["trucks"][1]["tire_hi"] = 0.9
    state["trucks"][1]["pm_due_hours"] = 8

    decision = policy.decide(state)

    assert decision["truck_id"] == "T02"
    assert decision["action"] == "PM_VEHICLE"
    assert decision["reason_code"] == "PM_DUE_TIME_PM_DUE"


def test_h0_uses_calendar_slot_not_pm_due_or_hi():
    config = load_c5_1_config(ROOT / "configs" / "c5_1.yaml")
    policy = create_policy("H0", config)
    state = _state()
    state["day"] = 1
    state["trucks"][0]["truck_hi"] = 0.95
    state["trucks"][0]["tire_hi"] = 0.95
    state["trucks"][0]["pm_due_hours"] = 72
    state["trucks"][1]["truck_hi"] = 0.2
    state["trucks"][1]["tire_hi"] = 0.2
    state["trucks"][1]["pm_due_hours"] = 1

    decision = policy.decide(state)

    assert decision["truck_id"] == "T01"
    assert decision["action"] == "PM_VEHICLE"
    assert decision["reason_code"] == "BASELINE_PERIODIC_PM_SLOT"


def test_h1_uses_former_h0_due_and_health_rule():
    config = load_c5_1_config(ROOT / "configs" / "c5_1.yaml")
    policy = create_policy("H1", config)
    state = _state()

    decision = policy.decide(state)

    assert decision["truck_id"] == "T02"
    assert decision["action"] in {"PM_TIRE", "PM_VEHICLE"}
    assert decision["reason_code"] == "DUE_HEALTH_PM_REQUIRED"


def test_legacy_bottleneck_policy_is_excluded_from_registry():
    assert "H1_LEGACY_EXCLUDED" not in POLICY_REGISTRY
    assert "H_PERIODIC" not in POLICY_REGISTRY
