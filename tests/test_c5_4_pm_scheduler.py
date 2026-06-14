from __future__ import annotations

import pytest

from mine_env.config_c5_4 import load_config
from mine_env.pm_scheduler_c5_4 import (
    PM_RULE_REGISTRY,
    CalendarPMRule,
    ConditionCBMPMRule,
    CostValuePMRule,
    FlowBackpressurePMRule,
    OperatingHoursPMRule,
    RiskPriorityPMRule,
    create_pm_rule,
)
from tests.c5_4_helpers import CONFIG_PATH, make_truck


@pytest.fixture(scope="module")
def config():
    return load_config(CONFIG_PATH, regime="heterogeneous_condition")


def _refer(rule, trucks, free_bays=2, **ctx):
    available_ids = {t["truck_id"] for t in trucks if t["status"] == "AVAILABLE"}
    context = {
        "day": ctx.get("day", 1),
        "hour": 0,
        "step": ctx.get("step", 1),
        "demand_remaining": 100,
        "slots_this_step": ctx.get("slots_this_step", 9),
        "available_count": len(available_ids),
    }
    return rule.select_referrals(trucks, available_ids, ctx.get("step", 1), free_bays, context)


def test_registry_covers_six_families():
    assert set(PM_RULE_REGISTRY) == {
        "calendar",
        "operating_hours",
        "condition",
        "risk_priority",
        "cost_value",
        "flow_backpressure",
    }


def test_calendar_fires_on_clock_blind_to_condition(config):
    rule = create_pm_rule("calendar", config)
    interval = config["pm_scheduling"]["calendar"]["interval_days"]
    healthy = make_truck("T01")  # phase = 1 % interval; due when (day - phase) % interval == 0
    # Due day for T01: day == 1 (phase) -> referred even though perfectly healthy (blind).
    due = _refer(rule, [healthy], day=1)
    assert due and due[0][0] == "T01"
    assert set(due[0][1]) == {"tire", "engine", "brake"}  # full vehicle service
    # A day that is NOT its slot: not referred, regardless of (here healthy) condition.
    not_due_day = 1 + (interval // 2 if interval > 1 else 0) + 1
    assert _refer(rule, [make_truck("T01")], day=not_due_day) == []
    # Worn but not on its calendar slot -> still NOT referred (condition-blind in WHEN).
    worn_off_slot = make_truck("T01", tire=0.05)
    assert _refer(rule, [worn_off_slot], day=not_due_day) == []


def test_operating_hours_fires_on_usage(config):
    rule = create_pm_rule("operating_hours", config)
    due_hours = config["pm_scheduling"]["operating_hours"]["due_hours"]
    used = make_truck("T01", operating_hours_since_pm=due_hours + 1)
    fresh = make_truck("T02", operating_hours_since_pm=0.0, tire=0.05)  # worn but unused
    refs = {r[0] for r in _refer(rule, [used, fresh])}
    assert "T01" in refs       # over the usage budget -> due
    assert "T02" not in refs   # blind to its low HI; not enough operating hours


def test_condition_cbm_refers_below_threshold(config):
    rule = create_pm_rule("condition", config)
    worn = make_truck("T01", tire=0.15)   # below tire threshold 0.21
    healthy = make_truck("T02")
    refs = _refer(rule, [worn, healthy])
    referred = {r[0]: r[1] for r in refs}
    assert "T01" in referred and "tire" in referred["T01"]
    assert "T02" not in referred


def test_risk_priority_uses_risk_threshold(config):
    rule = create_pm_rule("risk_priority", config)
    threshold = config["pm_scheduling"]["risk_priority"]["risk_threshold"]
    # tire criticality 1.0 -> risk = 1 - hi; below threshold hi the component is referred
    critical = make_truck("T01", tire=1.0 - threshold - 0.02)
    mild = make_truck("T02", tire=0.5)
    refs = {r[0] for r in _refer(rule, [critical, mild])}
    assert "T01" in refs
    assert "T02" not in refs


def test_cost_value_anticipates_threshold_crossing(config):
    rule = create_pm_rule("cost_value", config)
    near = make_truck("T01", tire=0.22)   # just above the 0.20 failure floor -> high p_soon
    healthy = make_truck("T02")
    refs = {r[0] for r in _refer(rule, [near, healthy])}
    assert "T01" in refs       # expected CM cost exceeds the PM cost
    assert "T02" not in refs   # far from threshold -> no anticipation


def test_flow_backpressure_only_acts_with_slack(config):
    rule = create_pm_rule("flow_backpressure", config)
    worn = make_truck("T01", tire=0.25)   # below soft threshold 0.30
    # slack: available_count (1) > slots_this_step (0) -> may PM
    with_slack = {r[0] for r in _refer(rule, [worn], slots_this_step=0)}
    assert "T01" in with_slack
    # no slack: demand needs every truck -> defer PM
    no_slack = _refer(rule, [make_truck("T01", tire=0.25)], slots_this_step=5)
    assert no_slack == []


@pytest.mark.parametrize("family", list(PM_RULE_REGISTRY))
def test_select_respects_free_bays(config, family):
    rule = create_pm_rule(family, config)
    # many trucks that are due on every family's trigger at once
    worn = [
        make_truck(f"T{i:02d}", operating_hours_since_pm=10_000, tire=0.05, engine=0.05, brake=0.05)
        for i in range(1, 7)
    ]
    assert len(_refer(rule, worn, free_bays=2, day=1, slots_this_step=0)) <= 2
    assert _refer(rule, worn, free_bays=0, day=1, slots_this_step=0) == []
