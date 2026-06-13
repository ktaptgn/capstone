from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


REQUIRED_MAIN_SECTIONS = {
    "simulation",
    "mine",
    "fleet",
    "demand",
    "operations",
    "policies",
    "outputs",
}


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected a mapping in {path}")
    return data


def load_c5_1_config(config_path: str | Path) -> dict[str, Any]:
    """Load the C5.1 config plus the companion cost and maintenance configs."""

    main_path = Path(config_path).resolve()
    if not main_path.exists():
        raise FileNotFoundError(main_path)

    config = deepcopy(_read_yaml(main_path))
    missing = REQUIRED_MAIN_SECTIONS - set(config)
    if missing:
        raise ValueError(f"C5.1 config missing sections: {sorted(missing)}")

    config_dir = main_path.parent
    config["cost_model"] = _read_yaml(config_dir / "cost_model_c5_1.yaml")["cost_model"]
    config["maintenance"] = _read_yaml(config_dir / "maintenance_c5_1.yaml")["maintenance"]

    if config["mine"].get("use_drop_zone") is not False:
        raise ValueError("C5.1 requires mine.use_drop_zone: false")
    if config["policies"].get("rl_enabled") is not False:
        raise ValueError("C5.1 requires policies.rl_enabled: false")

    return config


def project_root_from_config(config_path: str | Path) -> Path:
    return Path(config_path).resolve().parent.parent
