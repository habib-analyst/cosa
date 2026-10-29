#!/bin/bash
# Run the CoSA test suite from the build dir.
cd "$(dirname "$0")/.." || exit 1
python3 -m pytest tests/ -q
