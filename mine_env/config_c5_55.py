from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml

from mine_env.config_c5_3 import apply_regime
from mine_env.config_c5_54 import CONFIG_PATH as C5_54_CONFIG_PATH
from mine_env.config_c5_54 import load_config as _load_c5_54_config

CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "c5_55.yaml"


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def load_config(path: str | Path = CONFIG_PATH, regime: str | None = None) -> dict[str, Any]:
    """Load C5.54 behavior plus the C5.55 H5 freeze overlay."""
    base = _load_c5_54_config(C5_54_CONFIG_PATH, regime=None)
    with open(path, encoding="utf-8") as stream:
        overlay = yaml.safe_load(stream)
    config = _deep_merge(base, overlay)
    return apply_regime(config, regime_name=regime)


__all__ = ["CONFIG_PATH", "apply_regime", "load_config"]
