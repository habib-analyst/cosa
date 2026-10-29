# CoSA build summary (project #92, slug `cosa`)

## Verdicts
- G0 harness: PASS — deterministic scripted ecosystem, 15 pytest green.
- G1 author-code recheck: PASS — no author code found (arXiv abs page:
  no code link; project site: no repo link; web/GitHub searches: only
  unrelated results). Build is original.
- Pilot gate: PASS — gap +45.00pp, CI [37.78, 52.22].
- PREREG: locked before main run, no deviations.
- G2 disease: PASS — gap +32.39pp, CI [30.28, 34.61].
- G3 guard: PASS — reduction +55.56pp, CI [53.22, 57.89];
  benign utility loss +3.92pp (bound 15pp); nopath violations 0.

## Exact numbers (main run, 1,800 tasks/arm, 5,400 runs, ~12.7 min CPU)
- Clean violation: 23.17% (417/1,800); completion 37.72%.
- Augmented (+4.88% skills) violation: 55.56% (1,000/1,800);
  completion 89.33%.
- Guarded violation: 0.00% (0/1,800); completion 31.28%; blocked 1,045.
- Benign utility (n=586): augmented 100.00%, guarded 96.08%.
- By family, augmented violations: direct 307/477, bridge 286/471,
  rebind 297/458, opaque 110/202, nopath 0/192.
- Clean-arm bridge/rebind completions: 0 (paths do not exist pre-add).
- Digest: eddca343d3cca987ef016cacf11f61593de8c59abe92f1d8a15438bfc2fb82f3
- Determinism: seeds 101–102 re-run byte-identical partials; pytest
  15 passed (re-run green).

## Cost
$0. CPU only. No LLM calls, no network, no pushes, no LinkedIn touches.
Runtime: pilot 58s; main 762s; rerun 2 seeds ~150s.

## Payload / next action
- Staged payload: ~/workspace/build/cosa/ (src, tests, README, LICENSE,
  PREREG.md, KILLGATE.md, SUMMARY.md, scripts, results/).
- PAPER.md: ~/workspace/goals/github-portfolio-linkedin-presence-buildout/hidden_files/papers/cosa/PAPER.md
- LinkedIn DRAFT ONLY (DO NOT POST header):
  ~/workspace/goals/github-portfolio-linkedin-presence-buildout/hidden_files/linkedin_drafts/cosa.md
- **REPO NEEDED: habib-analyst/cosa** (creation via browser flow by the
  main agent; no push made from this build).
