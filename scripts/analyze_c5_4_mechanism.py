"""C5.4 Tier-3 failure-mechanism analysis (make the joint PM+dispatch mechanism transparent).

Runs every policy with per-failure event logging over held-out seeds and two regimes, then answers
three "why" questions:

  timing  -- Failure-timing histogram (campaign early/mid/late thirds). Does a policy fail early
             (unlucky frailty before PM catches up) or late (accumulated wear)?
  perseed -- Per-seed failure distribution + corr(max_frailty, failures). Is a high-CM seed a
             structural unlucky-frailty draw, or noise?
  causal  -- Per-policy causal profile: route mix %, per-component PM share, per-component CM share,
             end-of-campaign component HI. What fundamentally separates, e.g., H1 from H0 -- route
             selection or part management?

Writes JSON to outputs/c5_4/mechanism/ and a markdown report. Reduced, stated scale (anti-overclaim).
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mine_env.config_c5_4 import load_config
from mine_env.reliability_c5_4 import COMPONENTS
from mine_env.simulator_c5_4 import run_policy_simulation

CONFIG_PATH = PROJECT_ROOT / "configs" / "c5_4.yaml"
OUT_DIR = PROJECT_ROOT / "outputs" / "c5_4" / "mechanism"
REPORT_PATH = PROJECT_ROOT / "docs" / "source" / "09_C5_4_MECHANISM.md"

POLICIES = ["H0", "H_TIME", "H1", "H2", "H3", "H4"]
REGIMES = ["heterogeneous_condition", "high_stress"]
DEFAULT_SEEDS = list(range(101, 113))  # 12 seeds


def _safe_corr(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or x.std() == 0 or y.std() == 0:
        return None
    return round(float(np.corrcoef(x, y)[0, 1]), 3)


def run_all(seeds, days):
    """{(regime, policy): {"summaries": [...], "failures": [event,...]}}."""
    data = {}
    for regime in REGIMES:
        cfg = load_config(CONFIG_PATH, regime=regime)
        for pid in POLICIES:
            summaries, failures = [], []
            for s in seeds:
                res = run_policy_simulation(cfg, pid, seed=s, days=days, record_events=True)
                summaries.append(res.summary)
                for ev in res.failure_log:
                    failures.append({**ev, "seed": s})
            data[(regime, pid)] = {"summaries": summaries, "failures": failures}
            print(f"  [{regime}] {pid}: failures={sum(s['failure_count'] for s in summaries)} "
                  f"(mean {statistics.mean(s['failure_count'] for s in summaries):.1f}/run)", flush=True)
    return data


def timing_histogram(data, days):
    third = max(days / 3.0, 1.0)
    out = {}
    for (regime, pid), d in data.items():
        early = sum(1 for e in d["failures"] if e["day"] <= third)
        mid = sum(1 for e in d["failures"] if third < e["day"] <= 2 * third)
        late = sum(1 for e in d["failures"] if e["day"] > 2 * third)
        total = early + mid + late
        out[f"{regime}|{pid}"] = {"early": early, "mid": mid, "late": late, "total": total}
    return out


def per_seed(data):
    out = {}
    for (regime, pid), d in data.items():
        seeds = [s["seed"] for s in d["summaries"]]
        fails = [s["failure_count"] for s in d["summaries"]]
        maxfr = [s["max_frailty"] for s in d["summaries"]]
        out[f"{regime}|{pid}"] = {
            "by_seed": {s["seed"]: {"failures": s["failure_count"], "max_frailty": s["max_frailty"],
                                     "tco": s["total_tco"]} for s in d["summaries"]},
            "corr_maxfrailty_failures": _safe_corr(maxfr, fails),
            "max_failure_seed": seeds[int(np.argmax(fails))] if fails else None,
        }
    return out


def causal_profile(data):
    out = {}
    for (regime, pid), d in data.items():
        S = d["summaries"]

        def avg(key):
            return statistics.mean(float(s[key]) for s in S)

        completed = max(avg("completed_loads"), 1.0)
        pm_comp = max(avg("pm_component_count"), 1.0)
        cm_tot = max(avg("cm_count"), 1e-9)
        out[f"{regime}|{pid}"] = {
            "route_pct": {r: round(100 * avg(f"route_{r.lower()}_loads") / completed, 1)
                          for r in ("A", "B", "C")},
            "pm_share_pct": {c: round(100 * avg(f"pm_{c}") / pm_comp, 1) for c in COMPONENTS},
            "cm_share_pct": {c: (round(100 * avg(f"cm_{c}") / cm_tot, 1) if avg("cm_count") else 0.0)
                             for c in COMPONENTS},
            "end_hi": {c: round(avg(f"avg_{c}_hi"), 3) for c in COMPONENTS},
            "tco": round(avg("total_tco"), 1),
            "pm_visits": round(avg("pm_count"), 0),
            "cm_per_run": round(avg("cm_count"), 1),
        }
    return out


def write_report(timing, perseed, causal, seeds, days):
    L = [
        "# C5.4 Tier-3 Failure-Mechanism Analysis",
        "",
        f"- Reduced, stated scale: **{len(seeds)} seeds** {seeds}, **{days} days**, regimes "
        f"{REGIMES}; per-failure event logging. Headline numbers: `07_C5_4_RESULTS.md`.",
        "",
        "## 1. Failure-timing histogram (campaign early / mid / late thirds)",
        "",
        "| regime | policy | early | mid | late | total |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for key, h in timing.items():
        regime, pid = key.split("|")
        L.append(f"| {regime} | {pid} | {h['early']} | {h['mid']} | {h['late']} | {h['total']} |")

    L += ["", "## 2. Per-seed failure distribution & frailty correlation",
          "", "corr(max_frailty, failures) across seeds (None = too few/no-variance):", "",
          "| regime | policy | corr(maxFrailty, fails) | worst seed |", "|---|---|---:|---:|"]
    for key, p in perseed.items():
        regime, pid = key.split("|")
        L.append(f"| {regime} | {pid} | {p['corr_maxfrailty_failures']} | {p['max_failure_seed']} |")

    L += ["", "## 3. Per-policy causal profile", "",
          "Route mix %, per-component PM share %, per-component CM share %, end HI. "
          "Shows whether a policy differs by *route selection* or *part management*.", ""]
    for regime in REGIMES:
        L += [f"### Regime `{regime}`", "",
              "| policy | route A/B/C % | PM tire/eng/brake % | CM tire/eng/brake % | "
              "end HI t/e/b | TCO | CM/run |",
              "|---|---|---|---|---|---:|---:|"]
        for pid in POLICIES:
            c = causal[f"{regime}|{pid}"]
            rp, pp, cp, hi = c["route_pct"], c["pm_share_pct"], c["cm_share_pct"], c["end_hi"]
            L.append(
                f"| {pid} | {rp['A']}/{rp['B']}/{rp['C']} | "
                f"{pp['tire']}/{pp['engine']}/{pp['brake']} | "
                f"{cp['tire']}/{cp['engine']}/{cp['brake']} | "
                f"{hi['tire']}/{hi['engine']}/{hi['brake']} | {c['tco']} | {c['cm_per_run']} |"
            )
        L.append("")
    REPORT_PATH.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_PATH}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="C5.4 Tier-3 mechanism analysis.")
    ap.add_argument("--seeds", default=None, help="comma seeds (default: 101..112)")
    ap.add_argument("--days", type=int, default=365)
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")] if args.seeds else DEFAULT_SEEDS
    t0 = time.time()

    data = run_all(seeds, args.days)
    timing = timing_histogram(data, args.days)
    perseed = per_seed(data)
    causal = causal_profile(data)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "c5_4_mechanism.json").write_text(
        json.dumps({"seeds": seeds, "days": args.days, "timing": timing,
                    "per_seed": perseed, "causal": causal}, indent=2),
        encoding="utf-8",
    )
    write_report(timing, perseed, causal, seeds, args.days)
    print(f"Done in {(time.time()-t0)/60:.1f} min", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
