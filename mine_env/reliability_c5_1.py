from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BreakdownEvent:
    """A reactive failure that overrides a truck's RUN attempt for one turn."""

    downtime_hours: float
    restored_truck_hi: float
    restored_tire_hi: float
    trigger: str  # "TRUCK_HI" or "TIRE_HI"


class C5_1ReliabilityModel:
    """Config-gated reliability levers for C5.1.

    These levers control the structural defects the RL Lab PPO experiments exposed,
    so the heuristic comparison runs on an honest cost surface:

    * C1 (free self-healing) -- a breakdown no longer acts as a free full-health PM.
      Reactive repair only restores health *partially* and is charged a breakdown cost
      plus downtime, so proactive PM (full restore, scheduled, cheaper) stays preferable.
      Free STANDBY health recovery can also be switched off.
    * C3 (health has no operational consequence) -- once truck/tire HI drops below the
      operating thresholds, a RUN attempt can fail. The failed turn produces nothing
      (its demand becomes unmet) and incurs a breakdown cost, giving preventive
      maintenance real protective value instead of being pure cost.

    When ``reliability.enabled`` is false (or the section is absent) the model is a no-op:
    no breakdowns fire and STANDBY recovery keeps its configured value, so the simulation
    reproduces the original C5.1 numbers exactly. The new cost-decomposition columns are
    still emitted -- they only split the existing ``total_cost`` into its parts.
    """

    def __init__(self, config: dict[str, Any]):
        rel = config.get("reliability", {}) or {}
        self.enabled = bool(rel.get("enabled", False))
        self.truck_hi_threshold = float(rel.get("breakdown_truck_hi_threshold", 0.45))
        self.tire_hi_threshold = float(rel.get("breakdown_tire_hi_threshold", 0.40))
        self.prob_at_zero = float(rel.get("breakdown_prob_at_zero", 0.6))
        self.downtime_hours = float(rel.get("breakdown_downtime_hours", 8.0))
        self.repair_restore_hi = float(rel.get("repair_restore_hi", 0.70))
        self.standby_self_heal = bool(rel.get("standby_self_heal", False))

    # --- self-healing control (C1) -------------------------------------------------
    def standby_recovery(self, configured_recovery: float) -> float:
        """HI a parked truck regains on STANDBY.

        Original behaviour (levers off, or self-heal explicitly allowed) keeps the
        configured recovery. With levers on and self-heal off, parking no longer
        restores health for free -- closing the STANDBY-trick / free-PM path.
        """
        if not self.enabled or self.standby_self_heal:
            return configured_recovery
        return 0.0

    # --- breakdown risk (C3) -------------------------------------------------------
    def breakdown_probability(self, truck_hi: float, tire_hi: float) -> float:
        """Failure probability for a RUN attempt, ramping from 0 at the operating
        threshold to ``prob_at_zero`` at HI = 0. Returns 0 when levers are off or both
        components are above threshold."""
        if not self.enabled:
            return 0.0
        prob = 0.0
        if self.truck_hi_threshold > 0 and truck_hi < self.truck_hi_threshold:
            severity = (self.truck_hi_threshold - truck_hi) / self.truck_hi_threshold
            prob = max(prob, severity * self.prob_at_zero)
        if self.tire_hi_threshold > 0 and tire_hi < self.tire_hi_threshold:
            severity = (self.tire_hi_threshold - tire_hi) / self.tire_hi_threshold
            prob = max(prob, severity * self.prob_at_zero)
        return min(prob, 1.0)

    def maybe_breakdown(
        self, truck: dict[str, Any], rng: random.Random
    ) -> BreakdownEvent | None:
        """Draw a breakdown for this RUN attempt, or return None.

        The RNG is only consumed when the truck is actually at risk (below an operating
        threshold), so a disabled or all-healthy fleet leaves the stream untouched and
        results stay reproducible per seed.
        """
        truck_hi = float(truck["truck_hi"])
        tire_hi = float(truck["tire_hi"])
        prob = self.breakdown_probability(truck_hi, tire_hi)
        if prob <= 0.0 or rng.random() >= prob:
            return None
        trigger = "TRUCK_HI" if truck_hi <= tire_hi else "TIRE_HI"
        return BreakdownEvent(
            downtime_hours=self.downtime_hours,
            restored_truck_hi=max(truck_hi, self.repair_restore_hi),
            restored_tire_hi=max(tire_hi, self.repair_restore_hi),
            trigger=trigger,
        )
