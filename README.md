# cosa — skill-composition violations + guard (scripted reproduction)

An independent, CPU-only, zero-cost re-implementation of the *claim
structure* of Zheng et al., "CoSA: The Conflict of Skills Attack in
Real-World LLM Agent Ecosystems" (arXiv:2610.35082): adding a small
fraction of individually-admitted skills to a pool raises the rate at
which composed skill chains violate policy, and a harness-level guard
that checks information flow and authorization before consequential
actions cuts those violations with a small benign-utility cost.

**No LLMs are involved.** The "agent" is a deterministic, policy-blind
planner that chains skills by input/output kind only. The paper's
effect is reproduced at scripted scale: the disease is a property of
composition (individually safe skills + a policy-blind selector), not
of any particular model. All numbers in `results/` are measured from
this harness; see `PREREG.md` for the locked bars and `KILLGATE.md`
for per-gate verdicts.

## What it contains

- `src/cosa/` — model (artifacts with provenance chains), skill pools
  (41 base + 2 added = 4.88% augmentation), policy-blind DFS planner,
  ground-truth violation detector, CoSA-Guard analog, deterministic
  task generator, paired bootstrap statistics.
- `tests/` — 15 pytest tests, including per-skill admission, bridge /
  rebind reachability, guard allow/block cases, determinism, and a
  no-LLM/no-network import ban.
- `scripts/run_experiment.py` — pilot/main runner; writes partial
  results after every seed (reboot safety) and an aggregate with CIs.
- `PREREG.md` — bars locked before the main run.
- `KILLGATE.md` — per-gate verdicts, including the author-code recheck.
- `results/` — pilot + main aggregates and per-seed partials.

## Quickstart

```bash
python3 -m pytest tests/ -q
python3 scripts/run_experiment.py --mode main \
  --seeds 101,102,103,104,105,106,107,108,109,110,111,112 \
  --tasks-per-seed 150 --out results/main.json
```

Requirements: Python 3.10+, pytest. No third-party runtime
dependencies, no API keys, no network, no GPU.

## Key result (preregistered main run, 1,800 tasks/arm)

| Arm | Violation rate | Completion |
| --- | --- | --- |
| Clean pool, no guard | 23.17% (417/1,800) | 37.72% |
| Augmented pool (+4.88%), no guard | 55.56% (1,000/1,800) | 89.33% |
| Augmented pool + guard | 0.00% (0/1,800) | 31.28% |

Disease gap +32.39pp, 95% CI [30.28, 34.61]. Guard reduction +55.56pp,
95% CI [53.22, 57.89]. Benign utility 100.00% → 96.08% (loss +3.92pp,
n = 586). Nopath control violations: 0. Full table in
`results/main.json`; verdicts in `KILLGATE.md`.

## Honest limits

- The planner is scripted, not an LLM: this shows the composition
  mechanism is exhibitable without model behaviour, but it does not
  estimate LLM violation rates (the paper's 35.02% → 58.45% and
  65.28% → 6.67% are theirs, not ours).
- The guard shares the evaluator's provenance representation. A real
  deployment whose tags are stripped outside the harness's view would
  not see the provenance this guard relies on; the opaque-provenance
  block is the model's acknowledgment of that gap, not a solution to it.
- The violation detector cannot see through truncated provenance
  either, so opaque-family leaks are undercounted by the detector even
  as the guard blocks them — the guard's conservatism and the
  detector's blindness are two sides of the same coin.
- Tasks, authorization, and sensitivity are synthetic draws, not
  real-world skills or policies. Effect sizes are properties of this
  ecosystem design, calibrated to be measurable, not estimates of
  real-world risk.

## Attribution

Inspired by arXiv:2610.35082 and its project page
(https://sigmir-org.github.io/CoSA/). No author code, data, or text
is reused; the task generator, skills, planner, and guard are original.

## Determinism

Main-run aggregate digest (SHA-256): `eddca343d3cca987ef016cacf11f61593de8c59abe92f1d8a15438bfc2fb82f3`. Re-running seeds 101–102 reproduces the per-seed partial results byte-for-byte.
