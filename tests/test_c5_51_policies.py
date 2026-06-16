from __future__ import annotations

import pytest

from mine_env.config_c5_51 import load_config
from mine_env.policies_c5_51 import ROUTES, ROUTE_FACILITY_POLICY_REGISTRY, create_route_facility_policy
from tests.c5_51_helpers import CONFIG_PATH, make_truck, route_state

FACILITY_ACTION_PREFIXES = ("SEND_TO_", "STANDBY", "EMERGENCY_PM", "SAFE_STOP")


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_registry_matches_roster(config):
    assert set(ROUTE_FACILITY_POLICY_REGISTRY) == set(config["policies"]["enabled"])


@pytest.mark.parametrize("policy_id", ["H0", "H_TIME", "H1", "H2", "H3", "H4"])
def test_policies_return_ranked_routes_not_facility_actions(config, policy_id):
    policy = create_route_facility_policy(policy_id, config)
    trucks = [make_truck("T01"), make_truck("T02", tire=0.25), make_truck("T03", engine=0.25)]
    decision = policy.decide(route_state(trucks))
    assert set(decision) == {"pm", "dispatch"}
    dispatch = dict(decision["dispatch"])
    assert set(dispatch) == {"T01", "T02", "T03"}
    for ranked in dispatch.values():
        assert set(ranked) == set(ROUTES)
        assert not any(route.startswith(FACILITY_ACTION_PREFIXES) for route in ranked)
    for tid, components, _risk in decision["pm"]:
        assert tid in {"T01", "T02", "T03"}
        assert len(components) >= 1


def test_h3_prefers_best_grade_per_cycle_route(config):
    policy = create_route_facility_policy("H3", config)
    truck = make_truck("T01")
    ranked = dict(policy.decide(route_state([truck]))["dispatch"])["T01"]
    assert ranked[0] == "R_C1"


def test_h2_steers_worn_truck_to_gentler_route_than_h3(config):
    worn = make_truck("T01", tire=0.25, brake=0.25)
    h2 = create_route_facility_policy("H2", config)
    h3 = create_route_facility_policy("H3", config)
    assert dict(h2.decide(route_state([worn]))["dispatch"])["T01"][0] in {"R_C1", "R_C2"}
    assert dict(h3.decide(route_state([worn]))["dispatch"])["T01"][0] == "R_C1"
