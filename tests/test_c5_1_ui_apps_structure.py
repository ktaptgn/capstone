from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def _is_git_ignored(path: Path) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", str(path.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def test_imported_ui_apps_have_expected_vite_structure():
    operator = ROOT / "ui" / "operator_dashboard"
    pm_app = ROOT / "ui" / "pm_worker_app"

    for app in (operator, pm_app):
        assert (app / "package.json").exists()
        assert (app / "package-lock.json").exists()
        assert (app / "src").is_dir()
        assert (app / "public").is_dir()
        assert (app / "public" / "c5_1").is_dir()
        assert not (app / ".git").exists()
        assert _is_git_ignored(app / "node_modules")
        assert _is_git_ignored(app / "dist")


def test_no_official_rl_training_artifacts_are_imported():
    forbidden_paths = [
        ROOT / "train_ppo.py",
        ROOT / "models",
        ROOT / "tensorboard",
        ROOT / "ui" / "pm_worker_app" / "src" / "policies" / "rlPolicyPlaceholder.ts",
    ]

    for path in forbidden_paths:
        assert not path.exists()

    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    for dependency in ("stable-baselines3", "gymnasium", "wandb", "torch"):
        assert dependency not in requirements
