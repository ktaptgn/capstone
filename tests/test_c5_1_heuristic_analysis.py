import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "analyze_c5_1_heuristics.py"
POLICY_FILES = sorted((ROOT / "mine_env" / "policies").glob("h[0-4]_*.py"))


def file_hashes(paths: list[Path]) -> dict[Path, str]:
    return {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def test_analysis_script_exists():
    assert SCRIPT.exists()


def test_analysis_script_generates_outputs_without_policy_mutation():
    summary = ROOT / "tests" / "fixtures" / "policy_comparison_sample.csv"
    out_dir = ROOT / "outputs" / "c5_1" / "analysis" / "pytest_analysis"
    report = out_dir / "C5_1_HEURISTIC_COMPARISON_ANALYSIS.md"
    presentation = out_dir / "C5_1_PRESENTATION_RESULT_SUMMARY.md"
    dashboard = out_dir / "C5_1_DASHBOARD_ANALYSIS_MAPPING.md"
    before = file_hashes(POLICY_FILES)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--summary",
            str(summary),
            "--out-dir",
            str(out_dir),
            "--report",
            str(report),
            "--presentation",
            str(presentation),
            "--dashboard",
            str(dashboard),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (out_dir / "policy_kpi_summary.csv").exists()
    assert (out_dir / "h0_improvement_table.csv").exists()
    assert (out_dir / "policy_ranking_table.csv").exists()
    assert (out_dir / "policy_stability_table.csv").exists()
    assert (out_dir / "policy_tradeoff_notes.md").exists()
    assert report.exists()
    assert (ROOT / "docs" / "c5_1" / "C5_1_HEURISTIC_COMPARISON_ANALYSIS.md").exists()
    assert presentation.exists()
    assert dashboard.exists()
    assert before == file_hashes(POLICY_FILES)
