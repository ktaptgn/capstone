from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml


def load_config(path: str | Path, regime: str | None = None) -> dict[str, Any]:
    """Load the C5.3 YAML (UTF-8) and apply a named operating regime.

    The file is always read as UTF-8 (it carries Korean comments); the default Windows
    code page would mis-decode it. ``regime`` selects an entry from the ``regimes`` block;
    when omitted, ``default_regime`` is used.
    """
    with open(path, encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    return apply_regime(config, regime)


def apply_regime(config: dict[str, Any], regime_name: str | None = None) -> dict[str, Any]:
    """Return a copy of ``config`` with one regime's parameters applied (mirrors C6).

    A regime overrides the frailty CV and sensor-noise std, and supplies the wear / hazard /
    cm-cost / downtime / demand multipliers. The multipliers are read by the reliability and
    cost models from ``reliability.regime``; the demand factor scales ``daily_demand_loads``
    off a stored base so re-applying a regime is idempotent.
    """
    config = copy.deepcopy(config)
    regimes = config.get("regimes", {}) or {}
    name = regime_name or config.get("default_regime")
    regime = regimes.get(name, {}) if name else {}

    rel = config["reliability"]
    rel["regime"] = {
        "name": name,
        "wear_multiplier": float(regime.get("wear_multiplier", 1.0) or 1.0),
        "hazard_multiplier": float(regime.get("hazard_multiplier", 1.0) or 1.0),
        "cm_cost_multiplier": float(regime.get("cm_cost_multiplier", 1.0) or 1.0),
        "downtime_multiplier": float(regime.get("downtime_multiplier", 1.0) or 1.0),
    }
    if "heterogeneity_cv" in regime:
        rel.setdefault("frailty", {})["enabled"] = True
        rel["frailty"]["cv"] = float(regime["heterogeneity_cv"])
    if "condition_noise_std" in regime:
        rel.setdefault("condition_observation", {})["noise_std"] = float(
            regime["condition_noise_std"]
        )

    demand = config["demand"]
    base = float(demand.setdefault("base_daily_demand_loads", demand["daily_demand_loads"]))
    demand["daily_demand_loads"] = int(round(base * float(regime.get("demand_factor", 1.0) or 1.0)))

    config["active_regime"] = name
    return config
