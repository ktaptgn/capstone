from __future__ import annotations

import pytest

from mine_env.config_c5_5 import load_config
from mine_env.policies_c5_5 import (
    CRUSHER_ACTION_TO_ID,
    EMPTY_ACTIONS,
    FACILITY_POLICY_REGISTRY,
    LOADED_ACTIONS,
    SHOVEL_ACTION_TO_ID,
    create_facility_policy,
)
from tests.c5_5_helpers import CONFIG_PATH, facility_state, make_truck


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_registry_matches_roster(config):
    assert set(FACILITY_POLICY_REGISTRY) == set(config["policies"]["enabled"])


@pytest.mark.parametrize("policy_id", ["H0", "H_TIME", "H1", "H2", "H3", "H4"])
def test_all_policies_produce_valid_decisions(config, policy_id):
    policy = create_facility_policy(policy_id, config)
    trucks = [
        make_truck("T01", status="AVAILABLE_EMPTY"),
        make_truck("T02", status="LOADED", load_origin="SHOVEL_B"),
        make_truck("T03", status="AVAILABLE_EMPTY", tire=0.2),
    ]
    decision = policy.decide(facility_state(trucks))
    assert set(decision) == {"pm", "dispatch"}
    dispatch = dict(decision["dispatch"])
    assert set(dispatch) == {"T01", "T02", "T03"}
    assert set(dispatch["T01"]).issubset(set(EMPTY_ACTIONS))
    assert set(dispatch["T03"]).issubset(set(EMPTY_ACTIONS))
    assert set(dispatch["T02"]).issubset(set(LOADED_ACTIONS))
    for tid, components, _risk in decision["pm"]:
        assert tid in {"T01", "T03"}
        assert len(components) >= 1


def test_empty_trucks_cannot_rank_crushers(config):
    policy = create_facility_policy("H3", config)
    empty = make_truck("T01", status="AVAILABLE_EMPTY")
    ranked = dict(policy.decide(facility_state([empty]))["dispatch"])["T01"]
    assert not (set(ranked) & set(CRUSHER_ACTION_TO_ID))
    assert set(ranked) <= set(EMPTY_ACTIONS)


def test_loaded_trucks_cannot_rank_shovels(config):
    policy = create_facility_policy("H4", config)
    loaded = make_truck("T01", status="LOADED", load_origin="SHOVEL_A")
    ranked = dict(policy.decide(facility_state([loaded]))["dispatch"])["T01"]
    assert not (set(ranked) & set(SHOVEL_ACTION_TO_ID))
    assert set(ranked) <= set(LOADED_ACTIONS)


def test_h3_prefers_high_grade_shovel_a(config):
    policy = create_facility_policy("H3", config)
    empty = make_truck("T01", status="AVAILABLE_EMPTY")
    ranked = dict(policy.decide(facility_state([empty]))["dispatch"])["T01"]
    assert ranked[0] == "SEND_TO_SHOVEL_A"
