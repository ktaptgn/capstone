from __future__ import annotations

from typing import Any

import numpy as np


COMPONENTS = ("tire", "engine", "brake")


class C5_3ReliabilityModel:
    """Three-component (tire/engine/brake) reliability model for C5.3.

    A faithful, self-contained re-implementation of the RL Lab C6 reliability stack
    (capstone-main does not import c6). It bundles four documented C6 mechanics so the
    C5.3 dispatch comparison runs on the same honest cost surface:

    * Degradation -- each haul on a route loses, per component,
      ``base_loss x route_wear_multiplier x frailty_multiplier x regime_wear_multiplier``
      plus zero-mean Gaussian wear noise. Truck HI aggregate = min over components
      (a truck is only as healthy as its worst part).
    * Frailty -- a per-truck, per-component latent wear-rate multiplier drawn once per
      episode from ``Gamma(mean=1, cv)``. ``cv=0`` is homogeneous; ``cv>0`` makes two
      same-age trucks degrade at different real rates, so condition is informative
      beyond age (the ``heterogeneous_condition`` regime).
    * Sensor noise (POMDP) -- the OBSERVED component HI is the true HI plus
      ``Gaussian(0, noise_std)``, clipped to [0, 1]. Policies and the rule-based PM
      see the noisy observation, never the latent truth.
    * Failure hazard -- a Weibull-like wear-out hazard that is exactly 0 above
      ``threshold_hi`` and rises as HI falls below it, so a P-F interval exists.

    All parameters come from ``config["reliability"]`` (see ``configs/c5_3.yaml``); the
    ``regime`` multipliers are applied transparently on top of the documented base
    values. The cm-cost and downtime regime multipliers are NOT applied here -- they
    belong to the cost/maintenance layer and are applied there.
    """

    def __init__(self, config: dict[str, Any]):
        rel = config["reliability"]
        self.rel = rel

        regime = rel.get("regime", {}) or {}
        self.wear_multiplier = float(regime.get("wear_multiplier", 1.0) or 1.0)
        self.hazard_multiplier = float(regime.get("hazard_multiplier", 1.0) or 1.0)

        self.min_hi = float(rel.get("min_hi", 0.0))
        self.max_hi = float(rel.get("max_hi", 1.0))

        wear = rel.get("wear", {})
        self.base_loss = wear.get("base_loss_per_load", {})
        self.wear_noise_std = wear.get("stochastic_noise_std", {})

        frailty = rel.get("frailty", {}) or {}
        self.frailty_cv = (
            float(frailty.get("cv", 0.0) or 0.0)
            if bool(frailty.get("enabled", False))
            else 0.0
        )

        failure = rel.get("failure", {})
        self.threshold_hi = float(failure.get("threshold_hi", 0.20))
        self.hazard_scale = failure.get("hazard_scale", {})
        self.hazard_shape = failure.get("hazard_shape", {})

        obs = rel.get("condition_observation", {}) or {}
        self.noise_enabled = bool(obs.get("noise_enabled", True))
        self.noise_std = float(obs.get("noise_std", 0.0) or 0.0)
        self.clip_obs = bool(obs.get("clip_to_range", True))

    # --- initial state -------------------------------------------------------------
    def initial_hi(self) -> dict[str, float]:
        init = self.rel.get("initial_hi", {})
        return {component: float(init.get(component, 1.0)) for component in COMPONENTS}

    def draw_frailty(self, rng: np.random.Generator) -> dict[str, float]:
        """Per-truck per-component wear multiplier ~ Gamma(mean=1, cv). cv<=0 -> all 1.0."""
        cv = self.frailty_cv
        if cv <= 0:
            return {component: 1.0 for component in COMPONENTS}
        shape = 1.0 / max(cv * cv, 1e-6)
        scale = 1.0 / shape  # mean = shape * scale = 1.0
        return {component: float(rng.gamma(shape, scale)) for component in COMPONENTS}

    # --- aggregation ---------------------------------------------------------------
    @staticmethod
    def truck_hi(truck: dict[str, Any]) -> float:
        value = min(float(truck[f"{component}_hi"]) for component in COMPONENTS)
        truck["truck_hi"] = value
        return value

    def _clip_hi(self, value: float) -> float:
        return max(self.min_hi, min(self.max_hi, float(value)))

    # --- degradation (per haul on a route) -----------------------------------------
    def component_loss(
        self,
        component: str,
        route: dict[str, Any],
        truck: dict[str, Any],
        rng: np.random.Generator,
    ) -> float:
        base = float(self.base_loss.get(component, 0.0) or 0.0)
        route_mult = float(route.get(f"{component}_wear_multiplier", 1.0) or 1.0)
        frailty_mult = float(truck.get(f"{component}_wear_multiplier", 1.0) or 1.0)
        std = float(self.wear_noise_std.get(component, 0.0) or 0.0)
        noise = float(rng.normal(0.0, std)) if std > 0 else 0.0
        loss = base * route_mult * frailty_mult * self.wear_multiplier + noise
        return max(loss, 0.0)

    def apply_route_wear(
        self, truck: dict[str, Any], route: dict[str, Any], rng: np.random.Generator
    ) -> dict[str, float]:
        """Apply one haul's wear to every component; return the per-component HI loss."""
        losses: dict[str, float] = {}
        for component in COMPONENTS:
            key = f"{component}_hi"
            before = float(truck.get(key, 1.0))
            loss = self.component_loss(component, route, truck, rng)
            truck[key] = self._clip_hi(before - loss)
            losses[component] = before - float(truck[key])
        self.truck_hi(truck)
        return losses

    # --- sensor noise (POMDP) ------------------------------------------------------
    def observe(self, truck: dict[str, Any], rng: np.random.Generator) -> dict[str, float]:
        """Write noisy ``observed_<component>_hi`` onto the truck and return them."""
        observed: dict[str, float] = {}
        for component in COMPONENTS:
            value = float(truck.get(f"{component}_hi", 1.0))
            if self.noise_enabled and self.noise_std > 0:
                value += float(rng.normal(0.0, self.noise_std))
            if self.clip_obs:
                value = max(0.0, min(1.0, value))
            truck[f"observed_{component}_hi"] = value
            observed[component] = value
        return observed

    # --- failure hazard (Weibull-like) ---------------------------------------------
    def failure_probability(self, component: str, hi: float) -> float:
        """Per-haul failure probability for a component at health ``hi``.

        Exactly 0 above ``threshold_hi``; rises as ``(threshold - hi)/threshold`` to the
        ``hazard_shape`` power, scaled by the regime-adjusted ``hazard_scale``.
        """
        hi = float(hi)
        if hi > self.threshold_hi:
            return 0.0
        if hi <= 0.0:
            return 1.0
        scale = float(self.hazard_scale.get(component, 0.0) or 0.0) * self.hazard_multiplier
        shape = float(self.hazard_shape.get(component, 1.0) or 1.0)
        severity = max((self.threshold_hi - hi) / max(self.threshold_hi, 1e-9), 0.0)
        return min(scale * (severity ** shape), 1.0)

    def check_failures(self, truck: dict[str, Any], rng: np.random.Generator) -> list[str]:
        """Draw which components fail this haul (after wear has been applied)."""
        failed: list[str] = []
        for component in COMPONENTS:
            hi = float(truck[f"{component}_hi"])
            if float(rng.random()) < self.failure_probability(component, hi):
                failed.append(component)
        return failed

    @staticmethod
    def component_risk_score(component: str, hi: float) -> float:
        """Bounded condition-risk score used for PM eligibility (engine/brake weighted up)."""
        criticality = {"tire": 1.0, "engine": 1.1, "brake": 1.05}.get(component, 1.0)
        return min(max((1.0 - float(hi)) * criticality, 0.0), 1.0)
