# CoSA — kill-gate record (project #92, slug `cosa`)

Source paper: Zheng et al., "CoSA: The Conflict of Skills Attack in
Real-World LLM Agent Ecosystems", arXiv:2610.35082 (submitted 26 Oct 2026).
Project site: https://sigmir-org.github.io/CoSA/
This build is an independent, scripted, CPU-only re-implementation of the
paper's *claim structure* (small pool additions raise composition-violation
rates; a harness-level guard cuts them with small benign cost). It does NOT
reuse author code, data, or model outputs, and it uses NO LLM calls: the
"agent" is a deterministic policy-blind planner, so every number below is
a measured property of the scripted ecosystem, not a model behaviour claim.

## G0 — harness: PASS
Deterministic scripted skill/service ecosystem (41-skill base pool across
recruiting/finance/IT/business + 2-skill CoSA-style augmentation = 4.88%
of pool, within the paper's 5% cap). CPU only, $0, no LLM calls anywhere
(enforced by test_no_llm_or_network_imports), no network. pytest: 15
passed (2026-10-29). All skills pass the per-skill admission check, so
violations can only arise from composition, as in the paper's premise.

## G1 — author-code recheck: PASS (no author code found, build proceeds)
Checked 2026-10-29, fresh:
- arXiv abs page (arxiv.org/abs/2610.35082): title, 9 authors
  (Yujia Zheng et al.), abstract only. NO code/data link, NO GitHub link
  anywhere on the page (only PDF, license, arXivLabs toggles).
- Project site (sigmir-org.github.io/CoSA/): abstract, Tables 1-3,
  figures, BibTeX. NO code, repo, dataset, or download link in the
  fetched page text.
- Web searches "CoSA Conflict of Skills Attack github sigmir CoSA-Bench"
  and "CoSA-Bench OR CoSA-Guard github code": only the project site
  itself plus unrelated results (CoSA model checker, COSBench, a
  vulnerability-severity paper also named CoSA). No author benchmark or
  guard repository surfaced.
Caveat: the project site is hosted on GitHub Pages (sigmir-org org), so
a website-only repo presumably exists; that is not benchmark/guard code
and no such code was found. If author code appears later, this build's
novelty claim must be revisited.

## Pilot gate: PASS
Pilot (seeds 1–3, 60 tasks each, 180 total): clean violation 23.33%,
augmented 68.33%, guarded 0.00%. Disease gap +45.00pp, 95% paired
bootstrap CI [37.78, 52.22] (excludes 0). Guard reduction +68.33pp, CI
[61.67, 75.00] (excludes 0). Benign utility loss +2.33pp (benign n=43).
The disease is exhibitable at CPU/scripted scale with a large margin,
so the build proceeds to preregistration and the main run. Pilot numbers
are NOT part of the main result.
## PREREG: see PREREG.md (locked before the main run)
Locked 2026-10-29 after the pilot, before main seeds 101–112 ran. No
parameter, mix weight, threshold, or code path changed after the lock.
No deviations.

## G2 — disease: PASS
Main run (seeds 101–112, 150 tasks each, 1,800 tasks/arm, 5,400 runs):
clean violation 23.17% (417/1,800), augmented 55.56% (1,000/1,800).
Gap +32.39pp, 95% paired bootstrap CI [30.28, 34.61] — excludes 0 and
exceeds the 10pp preregistered bar. By family (augmented): direct
307/477, bridge 286/471, rebind 297/458, opaque 110/202, nopath 0/192.
In the clean arm, bridge and rebind families complete 0 tasks: the
violating paths do not exist until the additions arrive.

## G3 — load-bearing guard: PASS
Guarded (augmented pool + guard): 0.00% violations (0/1,800).
Reduction +55.56pp, 95% CI [53.22, 57.89] — excludes 0 and exceeds the
20pp bar. Benign utility: augmented 100.00% → guarded 96.08%
(n = 586); loss +3.92pp, 95% CI [2.39, 5.63] — within the 15pp bound.
The loss is the guard's conservative blocking of opaque-provenance
tasks, a genuine measured cost, not an assumed zero.
Sanity: nopath violations = 0 in all arms (harness integrity holds).

## Determinism
Re-running main seeds 101–102 reproduces the per-seed partial result
files byte-for-byte (cmp clean). Main aggregate digest:
eddca343d3cca987ef016cacf11f61593de8c59abe92f1d8a15438bfc2fb82f3.
pytest: 15 passed, re-run green after the main run.

## Overall verdict: ALL GATES PASS — payload staged, REPO NEEDED
Staged payload in ~/workspace/build/cosa/ (src, tests, README, LICENSE,
PREREG, KILLGATE, run scripts, results). PAPER.md at
~/workspace/goals/github-portfolio-linkedin-presence-buildout/hidden_files/papers/cosa/PAPER.md.
LinkedIn draft ONLY at
~/workspace/goals/github-portfolio-linkedin-presence-buildout/hidden_files/linkedin_drafts/cosa.md
(header: DO NOT POST). NO GitHub push made (per task rules).
REPO NEEDED: habib-analyst/cosa.
