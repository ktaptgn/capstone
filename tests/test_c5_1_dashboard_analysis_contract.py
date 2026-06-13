import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_c5_1_heuristics.py"


def run_analysis(summary: Path, out_dir: Path) -> Path:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--summary",
            str(summary),
            "--out-dir",
            str(out_dir),
            "--report",
            str(out_dir / "analysis_report.md"),
            "--presentation",
            str(out_dir / "presentation_summary.md"),
            "--dashboard",
            str(out_dir / "dashboard_mapping.md"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return out_dir / "dashboard_analysis.json"


def test_dashboard_analysis_json_contract():
    output_path = run_analysis(
        ROOT / "tests" / "fixtures" / "policy_comparison_missing_failure_sample.csv",
        ROOT / "outputs" / "c5_1" / "analysis" / "pytest_dashboard_contract",
    )
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert payload["baseline_policy"] == "H0"
    assert payload["seed_count"] == 2
    assert payload["recommended_policy"]["policy_id"]
    assert payload["recommended_policy"]["warning_ko"] == "수학적으로 모든 경우의 최선임을 보장하지 않습니다."
    assert payload["best_by_kpi"]
    assert payload["h0_improvement"]
    assert payload["stability"]
    assert {item["kpi"] for item in payload["missing_kpis"]} == {"failure_count"}
    assert payload["limitations_ko"]


def test_no_rl_dependency_added_to_official_repo():
    dependency_files = [
        ROOT / "requirements.txt",
        ROOT / "ui" / "operator_dashboard" / "package.json",
        ROOT / "ui" / "pm_worker_app" / "package.json",
    ]
    blocked = ["stable-baselines3", "gymnasium", "torch", "wandb"]
    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in dependency_files)

    for package_name in blocked:
        assert package_name not in combined
