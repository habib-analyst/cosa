"""Run one task under one arm (pool + guard on/off)."""

from __future__ import annotations

from .guard import guard_check
from .model import RunOutcome, ground_truth_violation
from .planner import plan


def run_task(task, pool, use_guard: bool) -> RunOutcome:
    chain, req = plan(task, pool)
    if req is None:
        return RunOutcome(task.task_id, task.family, False, False, False,
                          () if chain is None else chain, ())
    if use_guard:
        decision, reasons = guard_check(req, task.authorized)
        if decision == "BLOCK":
            return RunOutcome(task.task_id, task.family, False, False, True,
                              chain, reasons)
    reasons = ground_truth_violation(req, task.authorized)
    return RunOutcome(task.task_id, task.family, True, bool(reasons), False,
                      chain, reasons)
