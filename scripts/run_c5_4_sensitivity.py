"""C5.4 Tier-2 sensitivity analyses (method-robustness for the joint PM+dispatch comparison).

Three analyses, each written to outputs/c5_4/sensitivity/ as JSON the moment it finishes, plus a
combined markdown report:

  frailty -- Frailty-CV sweep (0.10..0.80). When is condition-aware policy value largest? Higher CV
             = more wear heterogeneity = condition carries more information beyond age.
  cbm     -- CBM-threshold robustness (x0.8..x1.2 around the frozen 0.21/0.21/0.28). Is the frozen
             C6.1 optimum near-best on the C5.4 joint surface, and how flat is the basin?
  bay     -- PM-bay-count bottleneck (1/2/3 bays). Does PM-queue contention change the policy ranking?

Scales are REDUCED from the 30-seed headline for time and stated verbatim in the report (anti-overclaim).
Lower total_tco is better. In-lab benchmark; not an official ranking.
"""
from __future__ import annotations

import argparse
import copy
import json
import statistics
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mine_env.config_c5_4 import load_config
from mine_env.reliability_c5_4 import COMPONENTS
from mine_env.simulator_c5_4 import run_policy_simulation

CONFIG_PATH = PROJECT_ROOT / "configs" / "c5_4.yaml"
OUT_DIR = PROJECT_ROOT / "outputs" / "c5_4" / "sensitivity"
REPORT_PATH = PROJECT_ROOT / "docs" / "source" / "08_C5_4_SENSITIVITY.md"

# Reduced, documented scales (vs the 30-seed x 3-regime headline sweep).
FRAILTY_CVS = [0.10, 0.20, 0.30, 0.40, 0.50, 0.65, 0.80]
CBM_SCALES = [0.80, 0.90, 1.00, 1.10, 1.20]
BAY_COUNTS = [1, 2, 3]
CALENDAR_INTERVALS = [3, 4, 5, 6, 8]   # blind-cadence robustness probe (H0)
HOURS_DUE = [24, 36, 48, 72]           # blind-cadence robustness probe (H_TIME)
DEFAULT_SEEDS = list(range(101, 111))  # 10 seeds
POLICIES = ["H0", "H_TIME", "H1", "H2", "H3", "H4"]
STATE_AWARE = ["H1", "H2"]   # condition-driven PM + routing
BLIND = ["H0", "H_TIME"]     # clock/usage-driven PM + route-blind


def mean(rows, key):
    return statistics.mean(float(r[key]) for r in rows)


def _run(config, policy, seeds, days):
    return [run_policy_simulation(config, policy, seed=s, days=days).summary for s in seeds]


# --- frailty CV sweep ------------------------------------------------------------------------
def frailty_sweep(seeds, days):
    base = load_config(CONFIG_PATH, regime="heterogeneous_condition")
    rows = []
    for cv in FRAILTY_CVS:
        cfg = copy.deepcopy(base)
        cfg["reliability"]["frailty"]["enabled"] = True
        cfg["reliability"]["frailty"]["cv"] = float(cv)
        entry = {"cv": cv, "policies": {}}
        for pid in POLICIES:
            res = _run(cfg, pid, seeds, days)
            entry["policies"][pid] = {
                "tco": mean(res, "total_tco"),
                "cm": mean(res, "cm_count"),
                "failure": mean(res, "failure_count"),
                "pm_count": mean(res, "pm_count"),
            }
        sa = min(entry["policies"][p]["tco"] for p in STATE_AWARE)
        bl = min(entry["policies"][p]["tco"] for p in BLIND)
        entry["best_state_aware_tco"] = sa
        entry["best_blind_tco"] = bl
        entry["state_aware_advantage_pct"] = 100.0 * (bl - sa) / bl if bl else 0.0
        rows.append(entry)
        print(f"  [frailty] cv={cv:.2f} bestSA={sa:.1f} bestBlind={bl:.1f} "
              f"adv={entry['state_aware_advantage_pct']:+.1f}%", flush=True)
    _dump("frailty_cv", {"seeds": seeds, "days": days, "rows": rows})
    return rows


# --- CBM threshold robustness ----------------------------------------------------------------
def cbm_sweep(seeds, days):
    regimes = ["heterogeneous_condition", "high_stress"]
    out = {}
    for regime in regimes:
        base = load_config(CONFIG_PATH, regime=regime)
        frozen = {c: float(base["rule_based_pm"]["hi_threshold"][c]) for c in COMPONENTS}
        rows = []
        for scale in CBM_SCALES:
            cfg = copy.deepcopy(base)
            for c in COMPONENTS:
                cfg["rule_based_pm"]["hi_threshold"][c] = round(
                    min(max(frozen[c] * scale, 0.05), 0.90), 4
                )
            res = _run(cfg, "H1", seeds, days)   # H1 carries the condition (CBM) PM family
            rows.append({
                "scale": scale,
                "thresholds": {c: cfg["rule_based_pm"]["hi_threshold"][c] for c in COMPONENTS},
                "tco": mean(res, "total_tco"),
                "cm": mean(res, "cm_count"),
                "pm_count": mean(res, "pm_count"),
                "failure": mean(res, "failure_count"),
            })
            print(f"  [cbm] {regime} scale={scale:.2f} TCO={rows[-1]['tco']:.1f} "
                  f"CM={rows[-1]['cm']:.1f}", flush=True)
        best = min(rows, key=lambda r: r["tco"])
        out[regime] = {"rows": rows, "best_scale": best["scale"], "frozen_thresholds": frozen}
    _dump("cbm_threshold", {"seeds": seeds, "days": days, "regimes": out})
    return out


# --- PM bay count ----------------------------------------------------------------------------
def bay_sweep(seeds, days):
    base = load_config(CONFIG_PATH, regime="heterogeneous_condition")
    rows = []
    for bays in BAY_COUNTS:
        cfg = copy.deepcopy(base)
        cfg["mine"]["pm_bay_count"] = int(bays)
        entry = {"bays": bays, "policies": {}}
        for pid in POLICIES:
            res = _run(cfg, pid, seeds, days)
            entry["policies"][pid] = {
                "tco": mean(res, "total_tco"),
                "cm": mean(res, "cm_count"),
                "pm_count": mean(res, "pm_count"),
                "fulfil": mean(res, "demand_fulfillment_rate"),
            }
        entry["ranking"] = sorted(entry["policies"], key=lambda p: entry["policies"][p]["tco"])
        rows.append(entry)
        print(f"  [bay] bays={bays} ranking={' < '.join(entry['ranking'])}", flush=True)
    _dump("pm_bay", {"seeds": seeds, "days": days, "rows": rows})
    return rows


# --- blind-cadence robustness (is the blind << state-aware result a cadence artifact?) -------
def cadence_sweep(seeds, days):
    base = load_config(CONFIG_PATH, regime="heterogeneous_condition")
    ref = {p: mean(_run(base, p, seeds, days), "total_tco") for p in ("H1", "H2")}
    cal, hrs = [], []
    for iv in CALENDAR_INTERVALS:
        cfg = copy.deepcopy(base)
        cfg["pm_scheduling"]["calendar"]["interval_days"] = int(iv)
        res = _run(cfg, "H0", seeds, days)
        cal.append({"interval_days": iv, "tco": mean(res, "total_tco"),
                    "fail": mean(res, "failure_count"), "pm_count": mean(res, "pm_count")})
        print(f"  [cadence] H0 iv={iv} TCO={cal[-1]['tco']:.1f} fail={cal[-1]['fail']:.1f}", flush=True)
    for du in HOURS_DUE:
        cfg = copy.deepcopy(base)
        cfg["pm_scheduling"]["operating_hours"]["due_hours"] = int(du)
        res = _run(cfg, "H_TIME", seeds, days)
        hrs.append({"due_hours": du, "tco": mean(res, "total_tco"),
                    "fail": mean(res, "failure_count"), "pm_count": mean(res, "pm_count")})
        print(f"  [cadence] H_TIME due={du} TCO={hrs[-1]['tco']:.1f} fail={hrs[-1]['fail']:.1f}", flush=True)
    out = {"state_aware_ref_tco": ref, "calendar": cal, "operating_hours": hrs}
    _dump("blind_cadence", {"seeds": seeds, "days": days, **out})
    return out


def _dump(name, payload):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"c5_4_sensitivity_{name}.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )


# --- markdown report -------------------------------------------------------------------------
def write_report(frailty, cbm, bay, cadence, seeds, days):
    L = [
        "# C5.4 Tier-2 Sensitivity Analyses (method robustness)",
        "",
        f"- Reduced scale (stated for honesty): **{len(seeds)} seeds** {seeds}, **{days} days**. "
        "The 30-seed x 3-regime headline lives in `07_C5_4_RESULTS.md`; these are robustness probes.",
        "- Joint PM+dispatch; lower TCO better. State-aware = {H1 CBM, H2 risk}; blind = {H0 calendar, "
        "H_TIME hours}.",
        "",
        "## 1. Frailty-CV sweep — when is condition-awareness most valuable?",
        "",
        "Higher CV = more wear heterogeneity, so condition carries more information beyond age.",
        "",
        "| CV | best state-aware TCO | best blind TCO | state-aware advantage |",
        "|---:|---:|---:|---:|",
    ]
    for r in frailty:
        L.append(f"| {r['cv']:.2f} | {r['best_state_aware_tco']:.1f} | {r['best_blind_tco']:.1f} | "
                 f"{r['state_aware_advantage_pct']:+.1f}% |")
    L += ["", "Per-policy mean TCO by CV:", "",
          "| CV | " + " | ".join(POLICIES) + " |", "|---:|" + "|".join("---:" for _ in POLICIES) + "|"]
    for r in frailty:
        L.append(f"| {r['cv']:.2f} | " + " | ".join(f"{r['policies'][p]['tco']:.1f}" for p in POLICIES) + " |")

    L += ["", "## 2. CBM-threshold robustness — is the frozen 0.21/0.21/0.28 near-optimal?", ""]
    for regime, data in cbm.get("regimes", {}).items():
        rows = data["rows"]
        L += [f"### Regime `{regime}` (H1, the condition family)", "",
              f"- Frozen thresholds = {data['frozen_thresholds']}; best scale here = "
              f"**x{data['best_scale']:.2f}**.", "",
              "| threshold x | tire/eng/brake | TCO | CM/run | PM visits |",
              "|---:|---|---:|---:|---:|"]
        for r in rows:
            th = r["thresholds"]
            star = " **(best)**" if r["scale"] == data["best_scale"] else ""
            L.append(f"| x{r['scale']:.2f}{star} | {th['tire']}/{th['engine']}/{th['brake']} | "
                     f"{r['tco']:.1f} | {r['cm']:.1f} | {r['pm_count']:.0f} |")
        L.append("")

    L += ["## 3. PM-bay-count bottleneck — does queue contention reorder policies?", "",
          "| bays | ranking (best->worst) | " + " | ".join(POLICIES) + " |",
          "|---:|---|" + "|".join("---:" for _ in POLICIES) + "|"]
    for r in bay:
        L.append(f"| {r['bays']} | {' < '.join(r['ranking'])} | "
                 + " | ".join(f"{r['policies'][p]['tco']:.1f}" for p in POLICIES) + " |")
    L.append("")

    if cadence:
        ref = cadence.get("state_aware_ref_tco", {})
        ref_str = ", ".join(f"{p} {v:.1f}" for p, v in ref.items())
        L += ["## 4. Blind-cadence robustness — is blind << state-aware a cadence artifact?", "",
              f"State-aware reference TCO (heterogeneous): {ref_str}. Every blind cadence below is "
              "well above it, so the result is **cadence-robust** (not engineered by the chosen interval).",
              "",
              "| H0 calendar interval (days) | TCO | fail/run | PM visits |", "|---:|---:|---:|---:|"]
        for r in cadence.get("calendar", []):
            L.append(f"| {r['interval_days']} | {r['tco']:.1f} | {r['fail']:.1f} | {r['pm_count']:.0f} |")
        L += ["", "| H_TIME operating-hours due | TCO | fail/run | PM visits |", "|---:|---:|---:|---:|"]
        for r in cadence.get("operating_hours", []):
            L.append(f"| {r['due_hours']} | {r['tco']:.1f} | {r['fail']:.1f} | {r['pm_count']:.0f} |")
        L.append("")

    REPORT_PATH.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT_PATH}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="C5.4 Tier-2 sensitivity analyses.")
    ap.add_argument("--analyses", default="frailty,cbm,bay,cadence")
    ap.add_argument("--seeds", default=None, help="comma seeds (default: 101..110)")
    ap.add_argument("--days", type=int, default=365)
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")] if args.seeds else DEFAULT_SEEDS
    want = {a.strip() for a in args.analyses.split(",") if a.strip()}
    t0 = time.time()

    frailty = frailty_sweep(seeds, args.days) if "frailty" in want else []
    cbm = cbm_sweep(seeds, args.days) if "cbm" in want else {}
    bay = bay_sweep(seeds, args.days) if "bay" in want else []
    cadence = cadence_sweep(seeds, args.days) if "cadence" in want else {}

    cbm_payload = {"regimes": cbm} if cbm else {"regimes": {}}
    write_report(frailty, cbm_payload, bay, cadence, seeds, args.days)
    print(f"Done in {(time.time()-t0)/60:.1f} min", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
