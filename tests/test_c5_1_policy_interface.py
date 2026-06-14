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

    assert set(POLICY_REGISTRY) == {"H0", "H1", "H2", "H3", "H4", "H_TIME"}

    for policy_id in ["H0", "H1", "H2", "H3", "H4", "H_TIME"]:
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
