from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], cwd: Path = ROOT) -> None:
    print(f"$ {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def main() -> None:
    python = sys.executable
    run([python, "scripts/run_c5_1_policy_sweep.py", "--config", "configs/c5_1.yaml", "--policies", "H0", "H1", "H2", "H3", "H4", "--seeds", "1", "2", "3"])
    run([python, "scripts/analyze_c5_1_heuristics.py", "--summary", "outputs/c5_1/summary/policy_comparison.csv"])
    run([python, "scripts/export_work_orders.py", "--policy", "H3", "--seed", "1"])
    run([python, "scripts/export_ui_snapshots.py"])


if __name__ == "__main__":
    main()
