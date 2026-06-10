"""Tests for the Relate stage (SPEC-relate.md v1)."""
from __future__ import annotations

import textwrap

import pytest

from kpm_builder.relate import (
    AxiomView,
    Relation,
    RelationType,
    RelateResult,
    apply_guards,
    parse_axiom_md,
    propose_relations,
    read_axioms,
    relate_kpm,
    verify_relation,
)


def _axset(*ids):
    return [AxiomView(id=i, statement=f"statement-{i}", status="candidate") for i in ids]


def _write_axiom(kpm, aid, stmt, eid):
    d = kpm / "axioms"
    d.mkdir(exist_ok=True)
    (d / f"{aid}.md").write_text(textwrap.dedent(f'''\
        ---
        id: {aid}
        type: axiom
        title: "{aid}"
        statement: "{stmt}"
        domain: "distilled"
        generativity: 3
        confidence: 0.5
        status: candidate
        relations:
          derives-from: []
          supports: []
          generalizes: []
          contradicts: []
          applies-to-kpm: []
        evidence: [{eid}]
        provenance: "package-research/distilled"
        ---

        # {aid}

        {stmt}

        Evidence: [[{eid}]].
        '''), encoding="utf-8")


def _write_evidence(kpm, eid, passage):
    d = kpm / "evidence"
    d.mkdir(exist_ok=True)
    (d / f"{eid}.md").write_text(textwrap.dedent(f'''\
        ---
        id: {eid}
        type: evidence
        ref: "https://example.com/{eid}"
        url: "https://example.com/{eid}"
        verified: 2026-06-04
        supports: []
        ---

        # Evidence: https://example.com/{eid}

        {passage}
        '''), encoding="utf-8")

# A real assemble() axiom note (verbatim shape).
SAMPLE_AXIOM = textwrap.dedent('''\
    ---
    id: a-bitcoin-full-node-has-modest-minimum-requirements
    type: axiom
    title: "A Bitcoin full node has modest minimum requirements"
    statement: "A Bitcoin full node has modest minimum requirements: 2 GB of RAM."
    domain: "distilled"
    generativity: 4
    confidence: 0.5
    status: candidate
    relations:
      derives-from: []
      supports: []
      generalizes: []
      contradicts: []
      applies-to-kpm: []
    evidence: [https-bitcoin-org-en-full-node]
    provenance: "package-research/distilled"
    ---

    # A Bitcoin full node has modest minimum requirements

    A Bitcoin full node has modest minimum requirements: 2 GB of RAM.

    Evidence: [[https-bitcoin-org-en-full-node]].
    ''')


# ── T1 data model ──────────────────────────────────────────────────────────

def test_relationtype_values_match_doctrine_keys():
    # doctrine_lint REL_KEYS uses exactly these strings.
    assert RelationType.SUPPORTS.value == "supports"
    assert RelationType.DERIVES_FROM.value == "derives-from"
    assert RelationType.GENERALIZES.value == "generalizes"
    assert RelationType.CONTRADICTS.value == "contradicts"
    assert {t.value for t in RelationType} == {
        "supports", "derives-from", "generalizes", "contradicts",
    }


def test_dataclasses_construct():
    a = AxiomView(id="a1", statement="s", status="candidate", evidence_ids=["e1"])
    assert a.evidence_ids == ["e1"]
    r = Relation(from_id="a1", to_id="a2", type=RelationType.SUPPORTS, verified=True)
    assert r.verified and r.reason == ""
    res = RelateResult(relations=[r])
    assert res.relations == [r] and res.capped == 0


# ── T2 parse ────────────────────────────────────────────────────────────────

def test_parse_axiom_md_extracts_fields():
    av = parse_axiom_md(SAMPLE_AXIOM)
    assert av.id == "a-bitcoin-full-node-has-modest-minimum-requirements"
    assert av.statement.startswith("A Bitcoin full node has modest")
    assert av.status == "candidate"
    assert av.evidence_ids == ["https-bitcoin-org-en-full-node"]


def test_parse_axiom_md_handles_dashes_in_values():
    # A frontmatter value containing '---' must not truncate parsing.
    txt = SAMPLE_AXIOM.replace(
        "https-bitcoin-org-en-full-node",
        "https-x-com-a---b",
    )
    av = parse_axiom_md(txt)
    assert av.evidence_ids == ["https-x-com-a---b"]


def test_read_axioms_reads_directory(tmp_path):
    axdir = tmp_path / "axioms"
    axdir.mkdir()
    (axdir / "a.md").write_text(SAMPLE_AXIOM, encoding="utf-8")
    views = read_axioms(tmp_path)
    assert len(views) == 1
    assert views[0].id == "a-bitcoin-full-node-has-modest-minimum-requirements"


# ── T3 propose ────────────────────────────────────────────────────────────────

def test_propose_caps_out_degree():
    axioms = _axset(*[f"a{i}" for i in range(1, 9)])

    def fake(prompt, schema):
        return {"relations": [
            {"from_id": "a1", "to_id": f"a{i}", "type": "supports", "rationale": "r"}
            for i in range(2, 9)  # 7 edges out of a1
        ]}

    kept, capped = propose_relations(axioms, complete_json=fake)
    assert len(kept) == 5 and capped == 2          # out-degree cap = 5


def test_propose_drops_malformed_and_unknown_type():
    axioms = _axset("a1", "a2")

    def fake(prompt, schema):
        return {"relations": [
            {"from_id": "a1", "to_id": "a2", "type": "bogus"},          # unknown type
            {"from_id": "a1", "type": "supports"},                       # missing to_id
            {"from_id": "a1", "to_id": "a2", "type": "contradicts", "rationale": "x"},
        ]}

    kept, capped = propose_relations(axioms, complete_json=fake)
    assert len(kept) == 1 and kept[0].type == RelationType.CONTRADICTS
    assert kept[0].verified is False               # propose never marks verified


def test_propose_global_cap():
    axioms = _axset(*[f"a{i}" for i in range(60)])

    def fake(prompt, schema):
        # 60 distinct from_ids × 4 edges each = 240 candidates, all under out-degree cap
        return {"relations": [
            {"from_id": f"a{i}", "to_id": f"a{(i + j) % 60}", "type": "supports"}
            for i in range(60) for j in range(1, 5)
        ]}

    kept, capped = propose_relations(axioms, complete_json=fake, global_cap=200)
    assert len(kept) == 200 and capped == 40


# ── T4 verify (refute-framed, directional, isolated) ──────────────────────────

_AXBY = {
    "a1": AxiomView("a1", "ALPHA STATEMENT", "candidate"),
    "a2": AxiomView("a2", "BETA STATEMENT", "candidate"),
    "a3": AxiomView("a3", "GAMMA SECRET", "candidate"),
}
_PASS = {"a1": "PASSAGE-ONE", "a2": "PASSAGE-TWO"}


def test_verify_holds_true():
    out = verify_relation(
        Relation("a1", "a2", RelationType.SUPPORTS, verified=False),
        _AXBY, _PASS, complete_json=lambda p, s: {"holds": True, "reason": "ok"},
    )
    assert out.verified is True and out.reason == "ok"


def test_verify_defaults_to_drop_on_malformed():
    out = verify_relation(
        Relation("a1", "a2", RelationType.SUPPORTS, verified=False),
        _AXBY, _PASS, complete_json=lambda p, s: {},      # no 'holds'
    )
    assert out.verified is False


def test_verify_defaults_to_drop_when_holds_not_strict_true():
    out = verify_relation(
        Relation("a1", "a2", RelationType.SUPPORTS, verified=False),
        _AXBY, _PASS, complete_json=lambda p, s: {"holds": "yes"},  # not bool True
    )
    assert out.verified is False


def test_verify_prompt_isolation_and_direction():
    captured = {}

    def fake(prompt, schema):
        captured["p"] = prompt
        return {"holds": True}

    rel = Relation("a1", "a2", RelationType.SUPPORTS, verified=False,
                   reason="PROPOSER RATIONALE SECRET")
    verify_relation(rel, _AXBY, _PASS, complete_json=fake)
    p = captured["p"]
    assert "ALPHA STATEMENT" in p and "BETA STATEMENT" in p
    assert "GAMMA SECRET" not in p                    # other axioms not leaked
    assert "PROPOSER RATIONALE SECRET" not in p       # proposer rationale not leaked
    assert "PASSAGE-ONE" in p and "PASSAGE-TWO" in p  # evidential type → passages
    assert "FROM" in p and "TO" in p                  # directional labels


def test_verify_non_evidential_excludes_passages():
    captured = {}

    def fake(prompt, schema):
        captured["p"] = prompt
        return {"holds": True}

    verify_relation(
        Relation("a1", "a2", RelationType.GENERALIZES, verified=False),
        _AXBY, _PASS, complete_json=fake,
    )
    # generalizes is a claim-level relation; passages are not shown.
    assert "PASSAGE-ONE" not in captured["p"]


def test_verify_direction_slots_carry_correct_statements():
    # The FROM slot must carry the from-axiom's statement and TO the to-axiom's,
    # so "A generalizes B" and "B generalizes A" present differently to the verifier.
    captured = {}

    def fake(prompt, schema):
        captured["p"] = prompt
        return {"holds": True}

    axby = {
        "a1": AxiomView("a1", "FROM-STATEMENT-ALPHA", "candidate"),
        "a2": AxiomView("a2", "TO-STATEMENT-BETA", "candidate"),
    }
    verify_relation(
        Relation("a1", "a2", RelationType.GENERALIZES, verified=False),
        axby, {}, complete_json=fake,
    )
    p = captured["p"]
    from_idx, to_idx = p.index("FROM:"), p.index("TO:")
    assert "FROM-STATEMENT-ALPHA" in p[from_idx:to_idx]   # from-statement in FROM slot
    assert "TO-STATEMENT-BETA" in p[to_idx:]              # to-statement in TO slot


# ── T5 guards + relate_kpm ────────────────────────────────────────────────────

def test_apply_guards_drops_self_dup_unknown_and_f2():
    axby = {
        "a1": AxiomView("a1", "s", "candidate"),
        "a2": AxiomView("a2", "s", "locked"),
        "a3": AxiomView("a3", "s", "locked"),
    }
    cands = [
        Relation("a1", "a1", RelationType.SUPPORTS, False),       # self → drop
        Relation("a1", "a2", RelationType.SUPPORTS, False),       # keep
        Relation("a1", "a2", RelationType.SUPPORTS, False),       # dup → drop
        Relation("a1", "zz", RelationType.SUPPORTS, False),       # unknown id → drop
        Relation("a2", "a3", RelationType.CONTRADICTS, False),    # locked+locked → F2 drop
        Relation("a1", "a2", RelationType.CONTRADICTS, False),    # candidate+locked → keep
    ]
    out = apply_guards(cands, axby)
    keys = {(r.from_id, r.to_id, r.type) for r in out}
    assert keys == {
        ("a1", "a2", RelationType.SUPPORTS),
        ("a1", "a2", RelationType.CONTRADICTS),
    }
    assert len(out) == 2


def test_relate_kpm_end_to_end(tmp_path):
    _write_axiom(tmp_path, "a1", "Statement one.", "e1")
    _write_axiom(tmp_path, "a2", "Statement two.", "e2")
    _write_evidence(tmp_path, "e1", "passage one")
    _write_evidence(tmp_path, "e2", "passage two")

    proposed = {"relations": [
        {"from_id": "a1", "to_id": "a2", "type": "supports", "rationale": "r"},
        {"from_id": "a2", "to_id": "a1", "type": "contradicts", "rationale": "r"},
    ]}

    def fake(prompt, schema):
        if "PROPOSED RELATION" not in prompt:        # the propose call
            return proposed
        return {"holds": "supports" in prompt, "reason": "x"}   # confirm only supports

    res = relate_kpm(tmp_path, complete_json=fake)
    assert isinstance(res, RelateResult)
    assert len(res.relations) == 1
    r = res.relations[0]
    assert (r.from_id, r.to_id, r.type, r.verified) == (
        "a1", "a2", RelationType.SUPPORTS, True,
    )
