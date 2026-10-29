"""Paired bootstrap CIs (percentile method, seeded RNG).

Each task is run under every arm, so arm differences are paired per task:
the per-task difference is in {-1, 0, +1}. Resampling tasks (not runs)
preserves the pairing. 10,000 resamples, 95% percentile CI.
"""

from __future__ import annotations

import random


def paired_diff_ci(values_a, values_b, seed=0, n_boot=10000):
    """values_a/b: per-task 0/1 outcomes, same order. Returns
    (mean_diff, lo, hi) in percentage points."""
    assert len(values_a) == len(values_b)
    diffs = [b - a for a, b in zip(values_a, values_b)]
    n = len(diffs)
    mean = sum(diffs) / n * 100.0
    rng = random.Random(seed)
    boots = []
    for _ in range(n_boot):
        s = 0
        for _ in range(n):
            s += diffs[rng.randrange(n)]
        boots.append(s / n * 100.0)
    boots.sort()
    lo = boots[int(0.025 * n_boot)]
    hi = boots[int(0.975 * n_boot)]
    return mean, lo, hi


def rate(values):
    return sum(values) / len(values) * 100.0 if values else 0.0
