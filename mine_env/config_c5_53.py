from __future__ import annotations

from pathlib import Path
from typing import Any

from mine_env.config_c5_3 import apply_regime, load_config as _load_config_c5_3

CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "c5_53.yaml"


def load_config(path: str | Path = CONFIG_PATH, regime: str | None = None) -> dict[str, Any]:
    """Load the C5.53 congestion-aware route-facility config and apply a named regime."""
    return _load_config_c5_3(path, regime=regime)


__all__ = ["CONFIG_PATH", "apply_regime", "load_config"]
