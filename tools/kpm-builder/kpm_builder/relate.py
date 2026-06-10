"""kpm_builder.relate — the Relate stage (judgment side).

Establishes independently-verified typed edges *between axioms* so a KPM is a
navigable web, not a star of source-pinned facts.  This is the JUDGMENT module
(LLM seam, like ground.py); the mechanical writer lives in ``apply_relations.py``.

Design (SPEC-relate.md v1):
- Propose candidate edges with ONE call that sees all (id, statement) pairs.
- Verify each edge with an INDEPENDENT, refute-framed, directional call that sees
  only the two statements (+ source passages for the evidential types) — never the
  other axioms or the proposer's rationale (isolation, mirroring ground.py).
- Default to dropping an edge: a relation ships only if a verifier framed to
  refute it could not.
- NO confidence recompute / corroboration in v1 (deferred — see SPEC §2, §10).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import yaml

# Reuse the existing seam — do not reimplement.  The seam returns a parsed dict
# (same contract as ground.py), so no JSON text-parsing is needed here.
from kpm_builder.providers import CompleteJSON

# Line-anchored frontmatter split (same shape as the public linter's _parse):
# a bare `---` inside a value can't truncate it.
_FM_SPLIT = re.compile(r"(?m)^---[ \t]*$")


# ── data model ────────────────────────────────────────────────────────────────

class RelationType(Enum):
    """The four doctrine relation types (values == doctrine_lint REL_KEYS)."""
    SUPPORTS = "supports"
    DERIVES_FROM = "derives-from"
    GENERALIZES = "generalizes"
    CONTRADICTS = "contradicts"


#: The two evidential types whose verifier also sees the source passages.
EVIDENTIAL: frozenset[RelationType] = frozenset(
    {RelationType.SUPPORTS, RelationType.DERIVES_FROM}
)


@dataclass
class AxiomView:
    """A read-only view of a KPM axiom note (no LLM)."""
    id: str
    statement: str
    status: str                      # "candidate" | "locked" (F2 guard)
    evidence_ids: list[str] = field(default_factory=list)


@dataclass
class Relation:
    """A directed typed edge between two axioms; ``verified`` gates whether it ships."""
    from_id: str
    to_id: str
    type: RelationType
    verified: bool
    reason: str = ""


@dataclass
class RelateResult:
    """Output of the Relate judgment stage: verified edges + cap-drop count."""
    relations: list[Relation]        # verified == True only
    capped: int = 0                  # # candidate edges dropped by the budget cap


# ── parsing (no LLM) ──────────────────────────────────────────────────────────

def parse_axiom_md(text: str) -> AxiomView:
    """Parse a KPM axiom .md into an AxiomView.

    Splits on a line-anchored ``---`` so a ``---`` inside a value (e.g. a slugged
    URL) cannot truncate the frontmatter, then yaml-loads the frontmatter block.
    """
    parts = _FM_SPLIT.split(text, maxsplit=2)
    if len(parts) < 3:
        raise ValueError("axiom note has no parseable frontmatter")
    fm = yaml.safe_load(parts[1]) or {}
    evidence = fm.get("evidence")
    if not isinstance(evidence, list):       # malformed/missing → no evidence ids
        evidence = []
    return AxiomView(
        id=str(fm.get("id", "")),
        statement=str(fm.get("statement", "")),
        status=str(fm.get("status", "candidate")),
        evidence_ids=[str(e) for e in evidence],
    )


def read_axioms(kpm_dir: str | Path) -> list[AxiomView]:
    """Read every ``axioms/*.md`` note in a KPM directory into AxiomViews."""
    axdir = Path(kpm_dir) / "axioms"
    return [
        parse_axiom_md(f.read_text(encoding="utf-8"))
        for f in sorted(axdir.glob("*.md"))
    ]


# ── propose (1 LLM call — recall) ─────────────────────────────────────────────

_PROPOSE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "relations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "from_id": {"type": "string"},
                    "to_id": {"type": "string"},
                    "type": {"type": "string",
                             "enum": [t.value for t in RelationType]},
                    "rationale": {"type": "string"},
                },
                "required": ["from_id", "to_id", "type"],
            },
        },
    },
    "required": ["relations"],
    "additionalProperties": False,
}

_PROPOSE_SYSTEM = """\
You connect ideas. Below is a numbered list of axioms (id: statement) from one
knowledge package. Propose DIRECTED typed relations BETWEEN axioms — never an
axiom to itself. Use only these types, with these exact directional meanings:
- supports      : FROM gives an independent reason to believe TO.
- derives-from  : FROM is derivable from the more-fundamental TO.
- generalizes   : FROM is the broader statement; TO is a special case of FROM.
- contradicts   : FROM and TO cannot both be true.
Propose at most 5 edges out of any single axiom. Only propose a relation you are
confident a skeptical reviewer would confirm; an independent verifier will check
each one and drop the rest. Output JSON only.
"""


def _propose_prompt(axioms: list[AxiomView]) -> str:
    listing = "\n".join(f"- {a.id}: {a.statement}" for a in axioms)
    return f"{_PROPOSE_SYSTEM}\n\nAXIOMS:\n{listing}\n\nRespond with JSON only."


def propose_relations(
    axioms: list[AxiomView],
    *,
    complete_json: CompleteJSON,
    max_out_degree: int = 5,
    global_cap: int = 200,
) -> tuple[list[Relation], int]:
    """Propose candidate (unverified) edges with one call that sees all axioms.

    Enforces an out-degree cap per source axiom and a global candidate cap;
    returns ``(candidates, capped)`` where ``capped`` counts edges dropped by
    the caps (honest degradation — never a silent truncation).  Malformed rows
    and unknown relation types are skipped.
    """
    raw = complete_json(_propose_prompt(axioms), _PROPOSE_SCHEMA)
    rows = raw.get("relations", []) if isinstance(raw, dict) else []

    candidates: list[Relation] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        try:
            rtype = RelationType(row["type"])
            from_id = str(row["from_id"])
            to_id = str(row["to_id"])
        except (KeyError, ValueError, TypeError):
            continue
        candidates.append(Relation(
            from_id=from_id, to_id=to_id, type=rtype,
            verified=False, reason=str(row.get("rationale", "")),
        ))

    capped = 0
    kept: list[Relation] = []
    out_degree: dict[str, int] = {}
    for c in candidates:
        if out_degree.get(c.from_id, 0) >= max_out_degree:
            capped += 1
            continue
        out_degree[c.from_id] = out_degree.get(c.from_id, 0) + 1
        kept.append(c)

    if len(kept) > global_cap:
        capped += len(kept) - global_cap
        kept = kept[:global_cap]

    return kept, capped


# ── verify (1 call/edge — independent, refute-framed, directional) ────────────

_VERIFY_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "holds": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "required": ["holds", "reason"],
    "additionalProperties": False,
}

_VERIFY_SYSTEM = """\
You are a skeptical, independent reviewer. A relation between two ideas has been
PROPOSED. Your job is to find a concrete reason it does NOT hold in the stated
direction. Answer holds=true ONLY if, after genuinely trying, you cannot find
any such reason. Default to holds=false when uncertain, when the link is merely
topical, or when the direction is wrong. Use only the information below."""

_MEANING: dict[RelationType, str] = {
    RelationType.SUPPORTS:
        "FROM gives an independent evidential or argumentative reason to believe TO.",
    RelationType.DERIVES_FROM:
        "FROM is a consequence or specialization derivable from the more-fundamental TO.",
    RelationType.GENERALIZES:
        "FROM is the broader statement and TO is a special case of FROM.",
    RelationType.CONTRADICTS:
        "FROM and TO cannot both be true.",
}


def _verify_prompt(
    rtype: RelationType,
    from_stmt: str,
    to_stmt: str,
    from_passage: str,
    to_passage: str,
) -> str:
    lines = [
        _VERIFY_SYSTEM,
        "",
        f"PROPOSED RELATION:  FROM  {rtype.value}  TO",
        f"MEANING: {_MEANING[rtype]}",
        f"FROM: {from_stmt}",
        f"TO: {to_stmt}",
    ]
    if rtype in EVIDENTIAL:
        lines += [
            f"FROM source passage: {from_passage}",
            f"TO source passage: {to_passage}",
        ]
    lines.append(
        'Respond with JSON only: {"holds": <bool>, "reason": <one sentence>}.'
    )
    return "\n".join(lines)


def verify_relation(
    rel: Relation,
    axioms_by_id: dict[str, AxiomView],
    passages: dict[str, str],
    *,
    complete_json: CompleteJSON,
) -> Relation:
    """Independently verify one proposed edge.

    The verifier sees ONLY the two statements (labelled FROM/TO), the type's
    directional meaning, and — for the evidential types — the two source
    passages.  It never sees the other axioms or the proposer's rationale
    (isolation).  Returns a Relation whose ``verified`` is True only when the
    reviewer affirmatively could not refute it; any malformed/uncertain output
    defaults to dropped.
    """
    frm = axioms_by_id.get(rel.from_id)
    to = axioms_by_id.get(rel.to_id)
    prompt = _verify_prompt(
        rel.type,
        frm.statement if frm else "",
        to.statement if to else "",
        passages.get(rel.from_id, ""),
        passages.get(rel.to_id, ""),
    )
    raw = complete_json(prompt, _VERIFY_SCHEMA)
    holds = isinstance(raw, dict) and raw.get("holds") is True
    reason = str(raw.get("reason", "")) if isinstance(raw, dict) else ""
    return Relation(rel.from_id, rel.to_id, rel.type, verified=holds, reason=reason)


# ── evidence passages (no LLM) ────────────────────────────────────────────────

def parse_evidence_md(text: str) -> tuple[str, str]:
    """Parse a KPM evidence .md into ``(id, passage)``.

    The passage is the note body with markdown header lines (``# …``) removed —
    i.e. the verbatim source snippet the axiom is grounded to.
    """
    parts = _FM_SPLIT.split(text, maxsplit=2)
    if len(parts) < 3:
        return "", ""
    fm = yaml.safe_load(parts[1]) or {}
    body_lines = [
        ln for ln in parts[2].strip().splitlines() if not ln.lstrip().startswith("#")
    ]
    return str(fm.get("id", "")), "\n".join(body_lines).strip()


def read_evidence(kpm_dir: str | Path) -> dict[str, str]:
    """Map evidence id → passage for every ``evidence/*.md`` note."""
    evdir = Path(kpm_dir) / "evidence"
    out: dict[str, str] = {}
    if not evdir.is_dir():
        return out
    for f in sorted(evdir.glob("*.md")):
        eid, passage = parse_evidence_md(f.read_text(encoding="utf-8"))
        if eid:
            out[eid] = passage
    return out


def _build_passages(
    axioms: list[AxiomView], evidence: dict[str, str]
) -> dict[str, str]:
    """Concatenate each axiom's linked source passages, keyed by axiom id."""
    return {
        a.id: "\n".join(evidence.get(eid, "") for eid in a.evidence_ids).strip()
        for a in axioms
    }


# ── guards + orchestration ────────────────────────────────────────────────────

def apply_guards(
    candidates: list[Relation], axioms_by_id: dict[str, AxiomView]
) -> list[Relation]:
    """Mechanical guards (no LLM): drop self-edges, dangling endpoints, duplicate
    ``(from, to, type)`` edges, and — F2 invariant — any ``contradicts`` edge
    between two ``locked`` axioms.  Order-preserving."""
    valid = set(axioms_by_id)
    seen: set[tuple[str, str, RelationType]] = set()
    kept: list[Relation] = []
    for c in candidates:
        if c.from_id == c.to_id:
            continue
        if c.from_id not in valid or c.to_id not in valid:
            continue
        key = (c.from_id, c.to_id, c.type)
        if key in seen:
            continue
        if c.type is RelationType.CONTRADICTS and (
            axioms_by_id[c.from_id].status == "locked"
            and axioms_by_id[c.to_id].status == "locked"
        ):
            continue  # F2: contradicts edge between two locked axioms
        seen.add(key)
        kept.append(c)
    return kept


def relate_kpm(
    kpm_dir: str | Path,
    *,
    complete_json: CompleteJSON,
    max_out_degree: int = 5,
    global_cap: int = 200,
) -> RelateResult:
    """Read a produced KPM, propose typed edges, independently verify each, and
    return only the verified relations (plus the cap-drop count).

    Pure judgment — does NOT write to disk; hand the result to
    ``apply_relations.apply_relations`` to persist it.
    """
    axioms = read_axioms(kpm_dir)
    axioms_by_id = {a.id: a for a in axioms}
    passages = _build_passages(axioms, read_evidence(kpm_dir))

    candidates, capped = propose_relations(
        axioms,
        complete_json=complete_json,
        max_out_degree=max_out_degree,
        global_cap=global_cap,
    )
    guarded = apply_guards(candidates, axioms_by_id)

    verified = [
        r for c in guarded
        if (r := verify_relation(c, axioms_by_id, passages, complete_json=complete_json)).verified
    ]
    return RelateResult(relations=verified, capped=capped)


# ── CLI (API path) ────────────────────────────────────────────────────────────

def _build_parser():
    import argparse

    p = argparse.ArgumentParser(
        prog="python -m kpm_builder.relate",
        description="Relate stage: propose, independently verify, and write typed "
                    "edges between a produced KPM's axioms (API path).",
    )
    p.add_argument("--kpm", required=True, help="Path to a produced KPM directory.")
    p.add_argument(
        "--family", default="anthropic",
        choices=["anthropic", "deepseek", "google"],
        help="Provider family for the API path (default: anthropic).",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    # Deferred imports: avoid an import cycle (apply_relations imports this module)
    # and keep SDK construction lazy.
    from kpm_builder.apply_relations import relate_and_apply
    from kpm_builder.providers import Family, make_provider

    cj = make_provider(Family(args.family))
    result = relate_and_apply(args.kpm, complete_json=cj)
    print(
        f"relate: wrote {len(result.relations)} verified relation(s) to "
        f"{args.kpm} (capped {result.capped})."
    )


if __name__ == "__main__":
    main()
