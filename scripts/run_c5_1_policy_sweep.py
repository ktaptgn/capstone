from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mine_env.config_c5_1 import load_c5_1_config, project_root_from_config
from mine_env.policies import POLICY_REGISTRY
from mine_env.simulator_c5_1 import run_policy_sweep


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the C5.1 policy sweep.")
    parser.add_argument("--config", required=True, help="Path to configs/c5_1.yaml")
    parser.add_argument("--policies", nargs="+", default=None, help="Policy ids to run")
    parser.add_argument("--seeds", nargs="+", type=int, default=[1], help="Seed values")
    parser.add_argument("--days", type=int, default=None, help="Optional horizon override")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_c5_1_config(args.config)
    root = project_root_from_config(args.config)
    policies = args.policies or list(config["policies"]["enabled"])
    supported = set(POLICY_REGISTRY)
    unsupported = [policy for policy in policies if policy not in supported]
    if unsupported:
        raise ValueError(f"Unknown C5.1 policies: {unsupported}")

    log_dir = root / Path(config["outputs"]["log_dir"])
    summary_dir = root / Path(config["outputs"]["summary_dir"])
    rows = run_policy_sweep(
        config,
        policies=policies,
        seeds=args.seeds,
        log_dir=log_dir,
        summary_dir=summary_dir,
        days=args.days,
    )
    print(f"Generated {len(rows)} policy summary rows")
    print(f"Logs: {log_dir}")
    print(f"Summary: {summary_dir}")


if __name__ == "__main__":
    main()
