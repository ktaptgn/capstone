from __future__ import annotations

from pathlib import Path
from typing import Any

# C5.4 reuses the C5.3 loader verbatim: the YAML structure (reliability / cost / routes /
# regimes) is identical -- C5.4 only adds a ``pm_scheduling`` block and a different policy
# roster, both of which are plain dict keys the loader already passes through untouched.
from mine_env.config_c5_3 import apply_regime, load_config as _load_config_c5_3

CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "c5_4.yaml"


def load_config(path: str | Path = CONFIG_PATH, regime: str | None = None) -> dict[str, Any]:
    """Load the C5.4 YAML (UTF-8) and apply a named operating regime.

    Thin wrapper over :func:`mine_env.config_c5_3.load_config` that defaults to the C5.4
    config file. Reliability/cost/route/regime parameters are carried over verbatim from
    C5.3 (anti-overclaim: not re-tuned); the regime machinery is unchanged.
    """
    return _load_config_c5_3(path, regime=regime)


__all__ = ["CONFIG_PATH", "apply_regime", "load_config"]
