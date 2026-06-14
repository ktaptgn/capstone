from __future__ import annotations

import pytest

from mine_env.config_c5_3 import load_config
from mine_env.policies_c5_3 import DISPATCH_POLICY_REGISTRY, create_dispatch_policy
from mine_env.policies_c5_3.base_dispatch import ROUTES
from mine_env.pm_rule_engine_c5_3 import C5_3RuleBasedPMEngine
from mine_env.reliability_c5_3 import C5_3ReliabilityModel
from tests.c5_3_helpers import CONFIG_PATH, dispatch_state, make_truck


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def test_roster_excludes_h_time(config):
    assert set(DISPATCH_POLICY_REGISTRY) == {"H0", "H1", "H2", "H3", "H4"}
    assert "H_TIME" not in DISPATCH_POLICY_REGISTRY


@pytest.mark.parametrize("policy_id", ["H0", "H1", "H2", "H3", "H4"])
def test_decide_dispatch_returns_full_route_ranking(config, policy_id):
    policy = create_dispatch_policy(policy_id, config)
    trucks = [make_truck("T01"), make_truck("T02", tire=0.3), make_truck("T03", engine=0.25)]
    intents = policy.decide_dispatch(dispatch_state(trucks))
    assert len(intents) == 3
    seen_ids = set()
    for truck_id, ranked_routes in intents:
        seen_ids.add(truck_id)
        # dispatch-only: a policy only ever returns routes, never a PM action
        assert set(ranked_routes) == set(ROUTES)        # full fallback ranking
        assert len(ranked_routes) == len(ROUTES)
    assert seen_ids == {"T01", "T02", "T03"}


def test_h0_is_route_blind_round_robin(config):
    policy = create_dispatch_policy("H0", config)
    trucks = [make_truck(f"T0{i}") for i in range(1, 4)]
    intents = dict(policy.decide_dispatch(dispatch_state(trucks)))
    # truck i takes ROUTES[i % 3] first, ignoring health entirely
    assert intents["T01"][0] == ROUTES[0]
    assert intents["T02"][0] == ROUTES[1]
    assert intents["T03"][0] == ROUTES[2]


def test_h2_routes_worn_truck_to_gentler_route_than_h3(config):
    # A truck worn on tire/brake should, under risk-aware H2, prefer the gentle route A,
    # whereas value-chasing H3 ignores condition and prefers the high-grade route C.
    worn = make_truck("T01", tire=0.3, brake=0.3)
    h2 = create_dispatch_policy("H2", config)
    h3 = create_dispatch_policy("H3", config)
    state = dispatch_state([worn])
    assert h2.decide_dispatch(state)[0][1][0] == "A"
    assert h3.decide_dispatch(state)[0][1][0] == "C"


def test_rule_pm_refers_component_below_threshold(config):
    reliability = C5_3ReliabilityModel(config)
    engine = C5_3RuleBasedPMEngine(config, reliability)
    healthy = make_truck("T01")
    worn = make_truck("T02", tire=0.15)   # below tire threshold 0.21
    referrals = engine.select_referrals([healthy, worn], {"T01", "T02"}, step=0, free_bays=2)
    referred = {(tid, comp) for tid, comp, _action, _risk in referrals}
    assert ("T02", "tire") in referred
    assert all(tid != "T01" for tid, _c in referred)   # healthy truck not referred


def test_rule_pm_respects_free_bays(config):
    reliability = C5_3ReliabilityModel(config)
    engine = C5_3RuleBasedPMEngine(config, reliability)
    worn = [make_truck(f"T0{i}", tire=0.10) for i in range(1, 5)]
    ids = {t["truck_id"] for t in worn}
    assert len(engine.select_referrals(worn, ids, step=0, free_bays=2)) == 2
    assert engine.select_referrals(worn, ids, step=0, free_bays=0) == []
