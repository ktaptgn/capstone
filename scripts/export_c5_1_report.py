from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mine_env.config_c5_1 import load_c5_1_config, project_root_from_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a C5.1 KPI markdown report.")
    parser.add_argument("--config", required=True, help="Path to configs/c5_1.yaml")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_c5_1_config(args.config)
    root = project_root_from_config(args.config)
    summary_dir = root / Path(config["outputs"]["summary_dir"])
    summary_json = summary_dir / "policy_comparison.json"
    if not summary_json.exists():
        raise FileNotFoundError(
            f"Run scripts/run_c5_1_policy_sweep.py before exporting: {summary_json}"
        )

    rows = json.loads(summary_json.read_text(encoding="utf-8"))
    report_path = summary_dir / "c5_1_policy_report.md"
    lines = [
        "# C5.1 Policy KPI Report",
        "",
        "| Policy | Seed | Total Cost | PM Cost | Unmet Demand | Fulfillment |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {policy_id} | {seed} | {total_cost:.3f} | {pm_cost:.3f} | "
            "{unmet_demand} | {demand_fulfillment_rate:.3f} |".format(**row)
        )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
