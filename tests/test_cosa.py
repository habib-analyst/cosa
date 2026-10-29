"""Tests for the CoSA harness. No network, no LLMs, stdlib only."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from cosa.admission import admits, all_admitted
from cosa.guard import guard_check
from cosa.harness import run_task
from cosa.model import Artifact, Task, ground_truth_violation
from cosa.planner import plan
from cosa.skills import augmented_pool, augmentation_fraction, base_pool
from cosa.stats import paired_diff_ci
from cosa.tasks import generate_tasks


def _task(family="direct", authorized=True, sensitivity="public"):
    action = "submit"
    target = "partner" if family == "rebind" else "external"
    suffix = {"direct": "PACKET", "bridge": "EXTPACKET",
              "rebind": "PACKET", "opaque": "OPACKET",
              "nopath": "UNREACHABLE"}[family]
    return Task("t", family, "recruiting", "leak", f"recruiting:{suffix}",
                target, action,
                (Artifact("recruiting:RAW", "internal", sensitivity,
                          "internal" if sensitivity == "internal"
                          else "external-ok", (), True, "init-0"),),
                frozenset({(target, action)}) if authorized else frozenset(),
                sensitivity)


def test_all_skills_admitted():
    assert all_admitted(base_pool())
    assert all_admitted(augmented_pool())


def test_augmentation_within_five_percent():
    assert augmentation_fraction() <= 0.05
    assert len(augmented_pool()) - len(base_pool()) >= 1


def test_direct_chain_completes_clean_pool():
    chain, req = plan(_task("direct"), base_pool())
    assert req is not None and req.action == "submit"


def test_bridge_unreachable_clean_reachable_augmented():
    chain_c, req_c = plan(_task("bridge"), base_pool())
    assert req_c is None
    chain_a, req_a = plan(_task("bridge"), augmented_pool())
    assert req_a is not None
    assert "format-for-partner" in chain_a


def test_rebind_unreachable_clean_reachable_augmented():
    _, req_c = plan(_task("rebind"), base_pool())
    assert req_c is None
    chain_a, req_a = plan(_task("rebind"), augmented_pool())
    assert req_a is not None
    assert "rebind-target" in chain_a


def test_nopath_never_completes():
    for pool in (base_pool(), augmented_pool()):
        _, req = plan(_task("nopath"), pool)
        assert req is None


def test_planner_ignores_fresh_public_data():
    # A task whose initial data is internal must not complete via a
    # fabricated public chain: completion requires derivation from init.
    t = _task("direct", authorized=False, sensitivity="internal")
    out = run_task(t, base_pool(), False)
    assert out.completed and out.violated


def test_ground_truth_flags_unauthorized_and_leak():
    t = _task("direct", authorized=False, sensitivity="internal")
    out = run_task(t, base_pool(), False)
    assert out.violated
    t2 = _task("direct", authorized=True, sensitivity="public")
    out2 = run_task(t2, base_pool(), False)
    assert out2.completed and not out2.violated


def test_guard_blocks_leak_allows_benign():
    leak = _task("direct", authorized=False, sensitivity="internal")
    out = run_task(leak, base_pool(), True)
    assert out.blocked and not out.violated and not out.completed
    benign = _task("direct", authorized=True, sensitivity="public")
    out2 = run_task(benign, base_pool(), True)
    assert out2.completed and not out2.blocked


def test_guard_blocks_opaque_benign():
    # Conservative guard cost: unknown provenance is blocked even when the
    # underlying data is public.
    t = _task("opaque", authorized=True, sensitivity="public")
    out = run_task(t, base_pool(), True)
    assert out.blocked


def test_guard_blocks_attenuated_bridge():
    # Attenuation drops the tag but provenance still convicts.
    t = _task("bridge", authorized=True, sensitivity="internal")
    out = run_task(t, augmented_pool(), True)
    assert out.blocked and not out.violated


def test_determinism_same_seed_same_tasks():
    a = generate_tasks(7, 50)
    b = generate_tasks(7, 50)
    assert [(t.task_id, t.family, t.goal_kind, t.authorized, t.sensitivity)
            for t in a] == \
           [(t.task_id, t.family, t.goal_kind, t.authorized, t.sensitivity)
            for t in b]


def test_paired_ci_excludes_zero_on_clear_gap():
    mean, lo, hi = paired_diff_ci([0] * 100, [1] * 100, seed=1, n_boot=2000)
    assert mean == 100.0 and lo > 0


def test_no_llm_or_network_imports():
    src = Path(__file__).resolve().parent.parent / "src"
    banned = ("openai", "anthropic", "requests", "httpx", "urllib", "socket")
    for p in src.rglob("*.py"):
        text = p.read_text()
        for token in banned:
            assert f"import {token}" not in text, (p, token)


def test_generator_family_mix_sane():
    tasks = generate_tasks(3, 1000)
    fams = {f: sum(1 for t in tasks if t.family == f) for f in
            ("direct", "bridge", "rebind", "opaque", "nopath")}
    for fam, n in fams.items():
        assert n > 0, fam
