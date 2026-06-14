from __future__ import annotations

import pytest

from mine_env.config_c5_4 import load_config
from mine_env.policies_c5_4 import JOINT_POLICY_REGISTRY, create_joint_policy
from mine_env.rl_interface_c5_4 import ROUTES
from tests.c5_4_helpers import CONFIG_PATH, joint_state, make_truck


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_registry_matches_roster(config):
    assert set(JOINT_POLICY_REGISTRY) == {"H0", "H_TIME", "H1", "H2", "H3", "H4"}


@pytest.mark.parametrize("policy_id", ["H0", "H_TIME", "H1", "H2", "H3", "H4"])
def test_decide_returns_pm_and_dispatch(config, policy_id):
    policy = create_joint_policy(policy_id, config)
    policy.reset()
    trucks = [make_truck("T01"), make_truck("T02", tire=0.3), make_truck("T03", engine=0.25)]
    decision = policy.decide(joint_state(trucks))
    assert set(decision) == {"pm", "dispatch"}
    # dispatch is the reused C5.3 contract: a full route ranking per available truck
    dispatched = {tid for tid, _routes in decision["dispatch"]}
    assert dispatched == {"T01", "T02", "T03"}
    for _tid, ranked in decision["dispatch"]:
        assert set(ranked) == set(ROUTES) and len(ranked) == len(ROUTES)
    # pm referrals (if any) name available trucks and carry >=1 component
    for tid, components, _risk in decision["pm"]:
        assert tid in {"T01", "T02", "T03"}
        assert len(components) >= 1


def test_h0_calendar_full_service_and_route_blind(config):
    policy = create_joint_policy("H0", config)
    trucks = [make_truck(f"T0{i}") for i in range(1, 4)]
    decision = policy.decide(joint_state(trucks, day=1))
    # T01 is on its calendar slot at day 1 -> a full vehicle service referral
    pm = {tid: comps for tid, comps, _r in decision["pm"]}
    assert "T01" in pm and set(pm["T01"]) == {"tire", "engine", "brake"}
    # dispatch is route-blind round-robin (reused C5.3 H0)
    dispatch = dict(decision["dispatch"])
    assert dispatch["T01"][0] == ROUTES[0]
    assert dispatch["T02"][0] == ROUTES[1]


def test_h2_routes_worn_truck_gentler_than_h3(config):
    worn = make_truck("T01", tire=0.3, brake=0.3)
    h2 = create_joint_policy("H2", config)
    h3 = create_joint_policy("H3", config)
    state = joint_state([worn])
    assert dict(h2.decide(state)["dispatch"])["T01"][0] == "A"   # risk-aware -> gentle route
    assert dict(h3.decide(state)["dispatch"])["T01"][0] == "C"   # value-chasing -> high-grade route


def test_condition_policy_refers_worn_component(config):
    policy = create_joint_policy("H1", config)
    worn = make_truck("T01", tire=0.15)
    pm = {tid: comps for tid, comps, _r in policy.decide(joint_state([worn]))["pm"]}
    assert "T01" in pm and "tire" in pm["T01"]
