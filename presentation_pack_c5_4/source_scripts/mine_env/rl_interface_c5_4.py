"""C5.4 joint-decision interface stub for PPO integration.

C5.1 and C5.3 left PPO disconnected: it lived in a separate RL Lab with no shared environment,
so a learned policy and the heuristics were never evaluated on the same surface. C5.4 closes that
gap by pinning down the *contract* both sides target -- without pulling gymnasium/torch into
capstone-main (training stays in the RL Lab). This module is that contract, and nothing more:

  * ``JointPolicy`` -- the protocol every C5.4 policy already satisfies (``decide(state)`` ->
    ``{"pm": ..., "dispatch": ...}`` plus ``reset()``). A PPO policy implements the same protocol.
  * ``encode_observation`` / ``decode_action`` -- the exact observation vector and per-truck
    discrete action set the RL Lab should build its Gymnasium env around. Pure NumPy, no deps.
  * ``AgentJointPolicy`` -- an adapter that wraps a trained ``agent(obs) -> action`` callable so it
    drops into ``mine_env.simulator_c5_4`` exactly where a heuristic joint policy would. This is the
    integration seam; there is deliberately NO ``reset()/step()`` env loop here (per scope).

The RL Lab is expected to: wrap the C5.4 simulator step in a Gymnasium ``Env`` whose
``observation_space`` matches :data:`OBSERVATION_LAYOUT` and whose ``action_space`` is
``MultiDiscrete([len(ACTION_CHOICES)] * truck_count)``; train PPO with reward = -delta_TCO per
step (so episode return = -total_TCO, the same objective the heuristics minimise); then evaluate the
trained agent in-repo via ``AgentJointPolicy(trained_agent)`` on the identical seeds/regimes.
"""
from __future__ import annotations

from typing import Any, Callable, Protocol, runtime_checkable

import numpy as np

from mine_env.reliability_c5_4 import C5_4ReliabilityModel


ROUTES = ("A", "B", "C")

# Per-truck discrete action: send the truck to PM for one component, or run it on a route.
ACTION_CHOICES = ("PM_TIRE", "PM_ENGINE", "PM_BRAKE", "RUN_A", "RUN_B", "RUN_C")

# Per-truck observation features (all on OBSERVED HI -- POMDP), in order.
TRUCK_FEATURES = (
    "obs_tire_hi",
    "obs_engine_hi",
    "obs_brake_hi",
    "status_available",
    "status_pm",
    "status_cm",
    "downtime_remaining_norm",
    "operating_hours_since_pm_norm",
    "days_since_pm_norm",
)

# Global (fleet-level) observation features, appended once after the per-truck block.
GLOBAL_FEATURES = (
    "demand_remaining_norm",
    "route_a_cap_norm",
    "route_b_cap_norm",
    "route_c_cap_norm",
    "free_bays_norm",
    "hour_norm",
    "day_norm",
)

# Normalisation constants for the unbounded counters (documented, not learned).
_DOWNTIME_NORM = 24.0
_OPS_HOURS_NORM = 100.0
_DAYS_SINCE_PM_NORM = 30.0


@runtime_checkable
class JointPolicy(Protocol):
    """The contract a C5.4 policy (heuristic or learned) must satisfy."""

    def reset(self) -> None: ...

    def decide(self, state: dict[str, Any]) -> dict[str, Any]:
        """Return ``{"pm": [(truck_id, components, risk), ...],
        "dispatch": [(truck_id, ranked_routes), ...]}``."""
        ...


def observation_dim(config: dict[str, Any]) -> int:
    truck_count = int(config["mine"]["truck_count"])
    return truck_count * len(TRUCK_FEATURES) + len(GLOBAL_FEATURES)


def OBSERVATION_LAYOUT(config: dict[str, Any]) -> dict[str, Any]:
    """Describe the flat observation vector so the RL Lab can build a matching space."""
    return {
        "truck_count": int(config["mine"]["truck_count"]),
        "truck_features": TRUCK_FEATURES,
        "global_features": GLOBAL_FEATURES,
        "dim": observation_dim(config),
        "action_choices": ACTION_CHOICES,
    }


def encode_observation(state: dict[str, Any], config: dict[str, Any]) -> np.ndarray:
    """Flatten the simulator ``state`` into the fixed-length observation vector.

    Layout: ``truck_count`` blocks of ``TRUCK_FEATURES`` (in ``state["trucks"]`` order) followed
    by one ``GLOBAL_FEATURES`` block. Every component HI is the OBSERVED (noisy) value.
    """
    trucks = state["trucks"]
    dispatch_state = state["dispatch_state"]
    routes = config["routes"]
    day = float(dispatch_state.get("day", 1))
    hour = float(dispatch_state.get("hour", 0))
    horizon_days = float(config["simulation"].get("horizon_days", 365) or 365)
    daily_demand = float(config["demand"]["daily_demand_loads"])

    feats: list[float] = []
    for truck in trucks:
        status = truck.get("status", "AVAILABLE")
        feats.extend(
            [
                float(truck.get("observed_tire_hi", truck.get("tire_hi", 1.0))),
                float(truck.get("observed_engine_hi", truck.get("engine_hi", 1.0))),
                float(truck.get("observed_brake_hi", truck.get("brake_hi", 1.0))),
                1.0 if status == "AVAILABLE" else 0.0,
                1.0 if status == "PM" else 0.0,
                1.0 if status == "CM" else 0.0,
                float(truck.get("downtime_remaining", 0)) / _DOWNTIME_NORM,
                float(truck.get("operating_hours_since_pm", 0.0)) / _OPS_HOURS_NORM,
                (day - float(truck.get("last_pm_day", 0))) / _DAYS_SINCE_PM_NORM,
            ]
        )

    caps = dispatch_state.get("route_capacity_remaining", {})
    feats.extend(
        [
            float(dispatch_state.get("demand_remaining", 0)) / max(daily_demand, 1.0),
            float(caps.get("A", 0)) / max(float(routes["A"]["capacity_loads_per_day"]), 1.0),
            float(caps.get("B", 0)) / max(float(routes["B"]["capacity_loads_per_day"]), 1.0),
            float(caps.get("C", 0)) / max(float(routes["C"]["capacity_loads_per_day"]), 1.0),
            float(state.get("free_bays", 0)) / max(float(config["mine"]["pm_bay_count"]), 1.0),
            hour / 24.0,
            day / max(horizon_days, 1.0),
        ]
    )
    return np.asarray(feats, dtype=np.float32)


def decode_action(
    action: Any, state: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    """Translate a per-truck discrete ``action`` vector into a ``{"pm", "dispatch"}`` decision.

    ``action[i]`` is an index into :data:`ACTION_CHOICES` for the ``i``-th truck in
    ``state["trucks"]``. Only AVAILABLE trucks are acted on. PM choices become shop-visit
    referrals (priority = observed condition-risk so the simulator's free-bay cap keeps the most
    at-risk); RUN choices become a dispatch ranking with the chosen route first and the others as
    capacity fallbacks (the C5.3 masking behaviour). Bay capacity is enforced downstream by the
    simulator, so this decoder never needs to know how many bays are free.
    """
    action = np.asarray(action).reshape(-1)
    reliability = C5_4ReliabilityModel(config)
    trucks = state["trucks"]
    available_ids = state.get("available_ids", {t["truck_id"] for t in trucks})

    pm: list[tuple[str, tuple[str, ...], float]] = []
    dispatch: list[tuple[str, list[str]]] = []
    for i, truck in enumerate(trucks):
        tid = truck["truck_id"]
        if tid not in available_ids:
            continue
        choice = int(action[i]) if i < len(action) else ACTION_CHOICES.index("RUN_A")
        label = ACTION_CHOICES[choice % len(ACTION_CHOICES)]
        if label.startswith("PM_"):
            component = label[len("PM_"):].lower()
            obs = float(truck.get(f"observed_{component}_hi", 1.0))
            risk = reliability.component_risk_score(component, obs)
            pm.append((tid, (component,), risk))
        else:
            chosen = label[len("RUN_"):]
            ranked = [chosen] + [r for r in ROUTES if r != chosen]
            dispatch.append((tid, ranked))
    pm.sort(key=lambda item: item[2], reverse=True)
    return {"pm": pm, "dispatch": dispatch}


class AgentJointPolicy:
    """Adapter: wrap a trained ``agent(obs) -> action`` callable as a C5.4 ``JointPolicy``.

    Lets a policy trained in the RL Lab run inside ``mine_env.simulator_c5_4`` on the same seeds
    and regimes as the heuristics, with no env loop required in capstone-main. ``agent`` receives
    the :func:`encode_observation` vector and must return a length-``truck_count`` action vector of
    indices into :data:`ACTION_CHOICES`.
    """

    policy_id = "PPO"

    def __init__(self, agent: Callable[[np.ndarray], Any], config: dict[str, Any]):
        self.agent = agent
        self.config = config

    def reset(self) -> None:
        reset = getattr(self.agent, "reset", None)
        if callable(reset):
            reset()

    def decide(self, state: dict[str, Any]) -> dict[str, Any]:
        obs = encode_observation(state, self.config)
        action = self.agent(obs)
        return decode_action(action, state, self.config)


def make_random_agent(config: dict[str, Any], seed: int = 0) -> Callable[[np.ndarray], np.ndarray]:
    """A uniform-random action sampler -- for wiring/illustration and tests, NOT a trained policy."""
    rng = np.random.default_rng(seed)
    truck_count = int(config["mine"]["truck_count"])
    n = len(ACTION_CHOICES)

    def _agent(_obs: np.ndarray) -> np.ndarray:
        return rng.integers(0, n, size=truck_count)

    return _agent


__all__ = [
    "ROUTES",
    "ACTION_CHOICES",
    "TRUCK_FEATURES",
    "GLOBAL_FEATURES",
    "JointPolicy",
    "OBSERVATION_LAYOUT",
    "observation_dim",
    "encode_observation",
    "decode_action",
    "AgentJointPolicy",
    "make_random_agent",
]
