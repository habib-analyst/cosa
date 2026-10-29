#!/bin/bash
# Preregistered main run (see PREREG.md). Seeds are disjoint from pilot
# (1-3) and test seeds. Partial results are written after every seed.
cd "$(dirname "$0")/.." || exit 1
python3 scripts/run_experiment.py --mode main \
  --seeds 101,102,103,104,105,106,107,108,109,110,111,112 \
  --tasks-per-seed 150 --out results/main.json
