from __future__ import annotations

import numpy as np
import pytest

from mine_env.config_c5_4 import load_config
from mine_env.policies_c5_4 import create_joint_policy
from mine_env.rl_interface_c5_4 import (
    ACTION_CHOICES,
    ROUTES,
    AgentJointPolicy,
    JointPolicy,
    decode_action,
    encode_observation,
    make_random_agent,
    observation_dim,
)
from mine_env.simulator_c5_4 import run_policy_simulation
from tests.c5_4_helpers import CONFIG_PATH, joint_state, make_truck


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_heuristics_and_adapter_satisfy_protocol(config):
    assert isinstance(create_joint_policy("H1", config), JointPolicy)
    assert isinstance(AgentJointPolicy(make_random_agent(config), config), JointPolicy)


def test_observation_dim_and_encoding(config):
    trucks = [make_truck(f"T{i:02d}") for i in range(1, 4)]
    state = joint_state(trucks)
    obs = encode_observation(state, config)
    # encode uses the trucks actually present in state; dim formula uses config truck_count
    assert obs.shape == (len(trucks) * 9 + 7,)
    assert obs.dtype == np.float32
    assert observation_dim(config) == int(config["mine"]["truck_count"]) * 9 + 7


def test_decode_action_respects_availability_and_structure(config):
    trucks = [
        make_truck("T01"),
        make_truck("T02", status="PM"),   # not available -> must be ignored
        make_truck("T03", tire=0.1),
    ]
    state = joint_state(trucks)
    # force PM_TIRE for every truck index
    action = np.zeros(len(trucks), dtype=int)  # index 0 == PM_TIRE
    decision = decode_action(action, state, config)
    pm_ids = {tid for tid, _c, _r in decision["pm"]}
    assert pm_ids == {"T01", "T03"}          # the PM (unavailable) truck excluded
    assert all(comp == ("tire",) for _t, comp, _r in decision["pm"])

    # RUN choices become a valid route ranking
    run_idx = ACTION_CHOICES.index("RUN_B")
    action = np.full(len(trucks), run_idx, dtype=int)
    decision = decode_action(action, state, config)
    for _tid, ranked in decision["dispatch"]:
        assert ranked[0] == "B" and set(ranked) == set(ROUTES)


def test_agent_policy_runs_through_simulator(config):
    agent = make_random_agent(config, seed=7)
    policy = AgentJointPolicy(agent, config)
    result = run_policy_simulation(config, "PPO_RANDOM", seed=101, days=8, policy=policy)
    s = result.summary
    assert s["policy_id"] == "PPO_RANDOM"
    assert np.isfinite(s["total_tco"])
    parts = (
        s["pm_cost"] + s["cm_cost"] + s["downtime_cost"]
        + s["degradation_cost"] + s["unmet_demand_cost"]
    )
    assert parts == pytest.approx(s["total_tco"], abs=1e-2)
