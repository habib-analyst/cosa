"""Run the CoSA head-to-head experiment.

Arms (same task set, paired):
  clean    : base pool, no guard
  augmented: base pool + 2 skills (<=5%), no guard
  guarded  : augmented pool + CoSA-Guard analog

Usage: python3 scripts/run_experiment.py --mode pilot|main
         --seeds 1,2,3 --tasks-per-seed 60 --out results/pilot.json
Writes a partial results file after every seed (reboot safety), then the
aggregate file with paired bootstrap CIs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from cosa.harness import run_task
from cosa.skills import augmented_pool, base_pool
from cosa.stats import paired_diff_ci, rate
from cosa.tasks import generate_tasks


def run_arm(tasks, pool, use_guard):
    return [run_task(t, pool, use_guard) for t in tasks]


def summarize(outcomes):
    return {
        "n": len(outcomes),
        "violation_rate": rate([1 if o.violated else 0 for o in outcomes]),
        "violations": sum(1 for o in outcomes if o.violated),
        "completion_rate": rate([1 if o.completed else 0 for o in outcomes]),
        "blocked": sum(1 for o in outcomes if o.blocked),
        "by_family": {
            fam: {
                "n": sum(1 for o in outcomes if o.family == fam),
                "violations": sum(1 for o in outcomes
                                  if o.family == fam and o.violated),
                "completed": sum(1 for o in outcomes
                                 if o.family == fam and o.completed),
            }
            for fam in sorted({o.family for o in outcomes})
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["pilot", "main"])
    ap.add_argument("--seeds", required=True)
    ap.add_argument("--tasks-per-seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    seeds = [int(s) for s in args.seeds.split(",")]
    base, aug = base_pool(), augmented_pool()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    partial_dir = out_path.parent / "partial"
    partial_dir.mkdir(parents=True, exist_ok=True)

    all_tasks, clean, augmented, guarded = [], [], [], []
    t0 = time.time()
    for seed in seeds:
        tasks = generate_tasks(seed, args.tasks_per_seed)
        c = run_arm(tasks, base, False)
        a = run_arm(tasks, aug, False)
        g = run_arm(tasks, aug, True)
        all_tasks.extend(tasks)
        clean.extend(c)
        augmented.extend(a)
        guarded.extend(g)
        partial = {
            "mode": args.mode, "seed": seed,
            "clean": summarize(c), "augmented": summarize(a),
            "guarded": summarize(g),
        }
        (partial_dir / f"{args.mode}_seed{seed}.json").write_text(
            json.dumps(partial, indent=2, sort_keys=True))
        print(f"seed {seed}: clean={partial['clean']['violation_rate']:.2f}% "
              f"aug={partial['augmented']['violation_rate']:.2f}% "
              f"guarded={partial['guarded']['violation_rate']:.2f}%", flush=True)

    benign_idx = [i for i, t in enumerate(all_tasks) if t.is_benign]
    util_clean = rate([1 if clean[i].completed else 0 for i in benign_idx])
    util_guarded = rate([1 if guarded[i].completed else 0 for i in benign_idx])
    util_aug = rate([1 if augmented[i].completed else 0 for i in benign_idx])

    gap_mean, gap_lo, gap_hi = paired_diff_ci(
        [1 if o.violated else 0 for o in clean],
        [1 if o.violated else 0 for o in augmented], seed=12345)
    red_mean, red_lo, red_hi = paired_diff_ci(
        [1 if o.violated else 0 for o in augmented],
        [1 if o.violated else 0 for o in guarded], seed=12345)
    # Guard reduction as a positive number: aug - guarded.
    red_mean, red_lo, red_hi = -red_mean, -red_hi, -red_lo
    loss_mean, loss_lo, loss_hi = paired_diff_ci(
        [1 if augmented[i].completed else 0 for i in benign_idx],
        [1 if guarded[i].completed else 0 for i in benign_idx], seed=12345)
    loss_mean, loss_lo, loss_hi = -loss_mean, -loss_hi, -loss_lo

    result = {
        "mode": args.mode, "seeds": seeds,
        "tasks_per_seed": args.tasks_per_seed,
        "total_tasks": len(all_tasks),
        "seconds": round(time.time() - t0, 2),
        "clean": summarize(clean),
        "augmented": summarize(augmented),
        "guarded": summarize(guarded),
        "benign_n": len(benign_idx),
        "benign_utility": {"clean": util_clean, "augmented": util_aug,
                           "guarded": util_guarded},
        "disease_gap_pp": {"mean": gap_mean, "ci95": [gap_lo, gap_hi]},
        "guard_reduction_pp": {"mean": red_mean, "ci95": [red_lo, red_hi]},
        "benign_utility_loss_pp": {"mean": loss_mean, "ci95": [loss_lo, loss_hi]},
        "nopath_violations": sum(1 for o in clean + augmented + guarded
                                 if o.family == "nopath" and o.violated),
    }
    digest = hashlib.sha256(
        json.dumps(result, sort_keys=True).encode()).hexdigest()
    result["digest"] = digest
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps({k: result[k] for k in
                      ("total_tasks", "disease_gap_pp",
                       "guard_reduction_pp", "benign_utility_loss_pp",
                       "benign_n", "digest")}, indent=2))


if __name__ == "__main__":
    main()
