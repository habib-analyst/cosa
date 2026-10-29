"""Policy-blind deterministic planner (scripted stand-in for autonomous
skill selection).

Depth-first search over skill applications, in fixed skill-name order,
with a visited-state memo and an expansion cap. The planner NEVER looks at
authorization, sensitivity, or provenance: it chains by kind only. A chain
completes only when its final artifact is *derived from the task's initial
artifact* -- derivation is tracked in the planner's execution state (what
the agent actually did), NOT read off the artifact's provenance field.
That separation is deliberate: an opaque transform truncates the
provenance the guard sees, but the agent still knows it transformed the
initial data. A chain that fabricates fresh public data via a source skill
does not count as doing the task.

Determinism: skill order sorted by name, artifacts sorted by id, no
wall-clock, no hash-order dependence (all sets are sorted before use).
"""

from __future__ import annotations

from .model import ActionRequest, Artifact

MAX_DEPTH = 6
MAX_EXPANSIONS = 20000


def apply_skill(skill, art, next_id):
    """Apply a transform skill to one artifact; return the output artifact."""
    if skill.output_rule == "same-domain-extpacket":
        out_kind = art.kind.replace(":PACKET", ":EXTPACKET")
    elif skill.output_rule == "same-domain-opacket":
        out_kind = art.kind.replace(":PACKET", ":OPACKET")
    elif skill.output_rule == "same-kind":
        out_kind = art.kind
    else:
        out_kind = skill.output_kind
    if skill.transform == "attenuate":
        return Artifact(out_kind, art.target, "public", "external-ok",
                        art.provenance + ((art.artifact_id, skill.name,
                                           art.sensitivity),),
                        True, next_id)
    if skill.transform == "opaque":
        return Artifact(out_kind, art.target, "public", "external-ok",
                        (), False, next_id)
    if skill.transform == "rebind":
        return Artifact(out_kind, "partner", art.sensitivity, art.scope,
                        art.provenance + ((art.artifact_id, skill.name,
                                           art.sensitivity),),
                        True, next_id)
    # preserve
    return Artifact(out_kind, art.target, art.sensitivity, art.scope,
                    art.provenance + ((art.artifact_id, skill.name,
                                       art.sensitivity),),
                    True, next_id)


def _descriptor(art):
    return (art.kind, art.target, art.sensitivity, art.scope,
            art.provenance, art.provenance_known)


def plan(task, pool):
    """Return (chain, action_request) or (None, None) if no chain found."""
    skills = sorted(pool, key=lambda s: s.name)
    counter = [len(task.initial)]

    def fresh_id():
        counter[0] += 1
        return f"a{counter[0]}"

    expansions = [0]
    visited = set()

    # State: tuple of (artifact, derived_from_initial) pairs.
    def dfs(state, chain, depth):
        if depth > MAX_DEPTH or expansions[0] > MAX_EXPANSIONS:
            return None
        expansions[0] += 1
        key = (tuple(sorted((_descriptor(a), d) for a, d in state)), depth)
        if key in visited:
            return None
        visited.add(key)
        for skill in skills:
            if skill.consequential is not None:
                for art, der in sorted(state, key=lambda p: p[0].artifact_id):
                    if art.kind not in skill.inputs:
                        continue
                    if not der:
                        continue
                    if task.family == "rebind" and art.target != "partner":
                        continue
                    if art.kind != task.goal_kind:
                        continue
                    req = ActionRequest(skill.name, task.goal_action,
                                        task.goal_target, (art,))
                    return chain + (skill.name,), req
                continue
            for in_kind in sorted(skill.inputs):
                for art, der in sorted(state, key=lambda p: p[0].artifact_id):
                    if art.kind != in_kind:
                        continue
                    out = apply_skill(skill, art, fresh_id())
                    if any(_descriptor(out) == _descriptor(a)
                           for a, _d in state):
                        continue
                    res = dfs(state + ((out, der),), chain + (skill.name,),
                              depth + 1)
                    if res is not None:
                        return res
        return None

    init_state = tuple((a, True) for a in task.initial)
    res = dfs(init_state, (), 0)
    if res is None:
        return None, None
    return res
