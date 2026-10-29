"""Per-skill admission check (the "individually admitted" gate).

A skill passes iff:
  - it performs no consequential action, OR it is a consequential skill
    whose inputs are packet kinds only (it acts on data it was given);
  - it does not both create an artifact from nothing and execute a
    consequential action (no skill does both);
  - its transform is one of the known, declared transforms.
This mirrors the paper's premise: every skill in both pools passes its
individual check, so any violation must come from composition.
"""

from __future__ import annotations

from .model import Skill

KNOWN_TRANSFORMS = {"preserve", "attenuate", "opaque", "rebind"}


def admits(skill: Skill) -> tuple:
    """Return (passes, reasons)."""
    reasons = []
    if skill.transform not in KNOWN_TRANSFORMS:
        reasons.append(f"unknown transform {skill.transform!r}")
    if skill.consequential is not None and not skill.inputs:
        reasons.append("consequential skill with no inputs")
    if skill.consequential is not None and skill.output_kind is not None:
        reasons.append("skill both produces and acts (not a pure action)")
    return (not reasons, tuple(reasons))


def all_admitted(pool) -> bool:
    return all(admits(s)[0] for s in pool)
